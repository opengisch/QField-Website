#!/usr/bin/env python3
"""Copy non-image files from the legacy wp-content folder into this project.

The script walks the source tree at /home/bky/DEV/qfield_hugo/static/wp-content,
skips image files, and copies everything else into static/wp-content while
preserving the relative folder structure.
"""

from __future__ import annotations

import shutil
from pathlib import Path

# Source WordPress content root (outside of this repo)
SOURCE_ROOT = Path("/home/bky/DEV/qfield_hugo/static/wp-content")

# Destination root inside this repo
DEST_ROOT = Path("static/wp-content")

# File extensions (lowercase) to skip. Extend as needed.
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


def is_image_file(path: Path) -> bool:
    """Return True if the file has an image extension."""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def copy_non_images() -> int:
    """Copy non-image files; return number of files copied."""
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Source path not found: {SOURCE_ROOT}")

    copied = 0
    for src_path in SOURCE_ROOT.rglob("*"):
        if not src_path.is_file():
            continue

        if is_image_file(src_path):
            continue

        relative_path = src_path.relative_to(SOURCE_ROOT)
        dest_path = DEST_ROOT / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        copied += 1
        print(f"Copied {relative_path}")

    return copied


def main() -> None:
    copied = copy_non_images()
    print(f"\nDone. Copied {copied} non-image file(s).")


if __name__ == "__main__":
    main()
