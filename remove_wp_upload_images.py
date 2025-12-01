#!/usr/bin/env python3
"""Delete image files from static/wp-content/uploads.

This script traverses the uploads tree, removes files with common image
extensions, and then prunes any empty directories left behind.
"""

from __future__ import annotations

from pathlib import Path

UPLOADS_ROOT = Path("static/wp-content/uploads")
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


def delete_images() -> int:
    if not UPLOADS_ROOT.exists():
        print(f"Uploads folder not found: {UPLOADS_ROOT}")
        return 0

    deleted = 0
    for file_path in sorted(UPLOADS_ROOT.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        file_path.unlink()
        deleted += 1
        print(f"Deleted {file_path.relative_to(UPLOADS_ROOT)}")
    return deleted


def prune_empty_dirs() -> int:
    removed = 0
    for dir_path in sorted(UPLOADS_ROOT.rglob("*"), reverse=True):
        if not dir_path.is_dir():
            continue
        try:
            next(dir_path.iterdir())
        except StopIteration:
            dir_path.rmdir()
            removed += 1
            print(f"Removed empty directory {dir_path.relative_to(UPLOADS_ROOT)}")
    return removed


def main() -> None:
    deleted = delete_images()
    emptied = prune_empty_dirs()
    print(f"\nDone. Deleted {deleted} image(s); removed {emptied} empty directorie(s).")


if __name__ == "__main__":
    main()
