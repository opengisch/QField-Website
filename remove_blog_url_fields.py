#!/usr/bin/env python3
"""Remove explicit `url` entries from blog post front matter so Hugo permalinks apply."""

from pathlib import Path

BLOG_DIR = Path("content/blog")


def strip_url_field(file_path: Path) -> bool:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return False

    # locate end of front matter
    fm_end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm_end_index = idx
            break

    if fm_end_index is None:
        return False

    fm_lines = lines[1:fm_end_index]
    body_lines = lines[fm_end_index:]

    updated_fm_lines = []
    removed = False
    for line in fm_lines:
        stripped = line.lstrip()
        if stripped.startswith("url:"):
            removed = True
            continue
        updated_fm_lines.append(line)

    if not removed:
        return False

    new_content = "---\n" + "".join(updated_fm_lines) + "".join(body_lines)
    file_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    if not BLOG_DIR.exists():
        raise SystemExit("content/blog directory not found")

    removed_count = 0
    for index_md in BLOG_DIR.glob("**/index.md"):
        if strip_url_field(index_md):
            removed_count += 1
            print(f"Removed url from {index_md.relative_to(BLOG_DIR)}")

    print(f"Total posts updated: {removed_count}")


if __name__ == "__main__":
    main()
