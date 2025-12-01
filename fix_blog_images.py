#!/usr/bin/env python3
"""Migrate blog image references away from /wp-content/uploads.

For every blog post that still references the legacy WordPress uploads path,
copy the referenced image into the post's bundle folder and update the content
(front matter + body) to point to the local copy. Also re-wrap orphaned figure
shortcodes that lost their opening tag.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set
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

WP_PATH_PATTERN = re.compile(
    r"((?:https?:\/\/[\w\.-]+(?::\d+)?[\w\/-]*)?\/(?:blog\/)?wp-content\/uploads\/(?P<path>[^\s\"'\)]+))",
    re.IGNORECASE,
)


def find_source(rel_path: str) -> Path | None:
    """Locate the source file inside SOURCE_UPLOADS, trying decoded variants."""
    rel_clean = rel_path.split("?")[0]
    candidates: List[Path] = []
    raw_parts = Path(*rel_clean.split("/"))
    candidates.append(SOURCE_UPLOADS / raw_parts)

    decoded = unquote(rel_clean)
    if decoded != rel_clean:
        decoded_parts = Path(*decoded.split("/"))
        candidates.append(SOURCE_UPLOADS / decoded_parts)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_figure_shortcodes(text: str) -> str:
    """Add missing `{{< figure ... >}}` prefixes when only the tail remains."""
    lines = text.splitlines()
    changed = False
    for idx, line in enumerate(lines):
        lower = line.lower()
        if "{{< figure" in lower or ">}}" not in line:
            continue
        if not any(ext in lower for ext in IMAGE_EXTENSIONS):
            continue
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        lines[idx] = f"{indent}{{{{< figure src=\"{stripped}"
        changed = True
    if changed:
        return "\n".join(lines)
    return text


def process_post(index_path: Path) -> bool:
    text = index_path.read_text(encoding="utf-8")
    matches = list(WP_PATH_PATTERN.finditer(text))
    if not matches:
        return False

    replacements: Dict[str, str] = {}
    copies: Set[str] = set()

    for match in matches:
        full_match = match.group(0)
        rel_path = match.group("path")
        ext = Path(rel_path.split("?")[0]).suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            continue
        replacements[full_match] = rel_path
        copies.add(rel_path)

    if not replacements:
        return False

    post_dir = index_path.parent
    modified = text

    for rel_path in sorted(copies):
        source = find_source(rel_path)
        if source is None:
            print(f"[WARN] Missing source for {rel_path} in {index_path.relative_to(BLOG_ROOT)}", file=sys.stderr)
            continue
        dest_name = Path(rel_path.split("?")[0]).name
        dest = post_dir / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(source, dest)
            print(f"Copied {source.name} -> {index_path.parent.relative_to(BLOG_ROOT)}/{dest_name}")

    for full_match, rel_path in replacements.items():
        dest_name = Path(rel_path.split("?")[0]).name
        modified = modified.replace(full_match, dest_name)

    modified = ensure_figure_shortcodes(modified)

    if modified != text:
        index_path.write_text(modified, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not SOURCE_UPLOADS.exists():
        raise SystemExit(f"Source uploads directory not found: {SOURCE_UPLOADS}")

    updated = 0
    for index_path in sorted(BLOG_ROOT.glob("*/index.md")):
        if process_post(index_path):
            updated += 1
    print(f"Done. Updated {updated} blog post(s).")


if __name__ == "__main__":
    main()
