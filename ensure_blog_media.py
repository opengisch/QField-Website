#!/usr/bin/env python3
"""Ensure each blog post bundle contains every referenced image file."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
from urllib.parse import unquote

BLOG_ROOT = Path("content/blog")
SOURCE_UPLOADS = Path("/home/bky/DEV/qfield_hugo/static/wp-content/uploads")
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".bmp",
    ".tif",
    ".tiff",
    ".avif",
    ".heic",
    ".heif",
}

FIGURE_PATTERN = re.compile(r"{{<\s*figure[^>]*?src\s*=\s*\"([^\"]+)\"", re.IGNORECASE)
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_IMAGE_PATTERN = re.compile(r"<img[^>]+src=\"([^\"]+)\"", re.IGNORECASE)
SINGLE_QUOTE_IMG_PATTERN = re.compile(r"<img[^>]+src='([^']+)'", re.IGNORECASE)
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def build_source_index() -> Dict[str, List[Path]]:
    index: Dict[str, List[Path]] = {}
    for path in SOURCE_UPLOADS.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        index.setdefault(path.name.lower(), []).append(path)
    return index


SOURCE_INDEX = build_source_index()


def candidate_names(ref: str) -> List[str]:
    cleaned = ref.split("?")[0].lstrip("./")
    names: List[str] = []
    if cleaned:
        names.append(Path(cleaned).name)
    decoded = unquote(cleaned)
    if decoded and decoded not in names:
        names.append(Path(decoded).name)
    # Handle PYYMMDD_* -> 20YYMMDD_* conversion
    if decoded:
        stem = Path(decoded).stem
        suffix = Path(decoded).suffix
        if stem.startswith("P") and len(stem) > 7 and stem[1:7].isdigit() and (len(stem) == 7 or stem[7] in {"_", "-"} or stem[7:].isdigit()):
            alt_stem = f"20{stem[1:]}"
            alt_name = alt_stem + suffix
            if alt_name not in names:
                names.append(alt_name)
    return names


def find_source_for_ref(ref: str) -> Path | None:
    for name in candidate_names(ref):
        matches = SOURCE_INDEX.get(name.lower())
        if matches:
            if len(matches) > 1:
                print(f"[WARN] Multiple source candidates for {ref}; using {matches[0]}", file=sys.stderr)
            return matches[0]
    return None


def extract_refs(text: str) -> List[str]:
    refs: List[str] = []
    def maybe_add(value: str) -> None:
        value = value.strip()
        if not value:
            return
        lower = value.lower()
        if lower.startswith(("http://", "https://", "//", "/", "#", "{{")):
            return
        ext = Path(value.split("?")[0]).suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            return
        refs.append(value)

    for pattern in (FIGURE_PATTERN, HTML_IMAGE_PATTERN, SINGLE_QUOTE_IMG_PATTERN, MARKDOWN_IMAGE_PATTERN):
        for match in pattern.findall(text):
            maybe_add(match)
    return refs


def process_post(index_path: Path) -> bool:
    text = index_path.read_text(encoding="utf-8")
    refs = extract_refs(text)
    if not refs:
        return False

    post_dir = index_path.parent
    updated = False

    for ref in refs:
        rel_path = ref.split("?")[0].lstrip("./")
        dest = post_dir / rel_path
        if dest.exists():
            continue
        source = find_source_for_ref(ref)
        if source is None:
            print(f"[WARN] Could not locate source for {ref} (post {index_path.relative_to(BLOG_ROOT)})", file=sys.stderr)
            continue
        dest_name = source.name
        dest = post_dir / dest_name
        if not dest.exists():
            shutil.copy2(source, dest)
            print(f"Copied missing {dest_name} -> {index_path.parent.relative_to(BLOG_ROOT)}")
        if dest_name != rel_path:
            text = text.replace(ref, dest_name)
            updated = True

    if updated:
        index_path.write_text(text, encoding="utf-8")
    return updated


def main() -> None:
    updated_posts = 0
    for index_path in sorted(BLOG_ROOT.glob("*/index.md")):
        if process_post(index_path):
            updated_posts += 1
    print(f"Done. Updated {updated_posts} post(s).")


if __name__ == "__main__":
    if not SOURCE_UPLOADS.exists():
        raise SystemExit(f"Missing source uploads directory: {SOURCE_UPLOADS}")
    main()
