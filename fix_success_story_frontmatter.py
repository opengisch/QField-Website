#!/usr/bin/env python3
"""Fix front matter image references in success stories to match actual filenames."""

import os
import re
from pathlib import Path

def fix_frontmatter_images(folder_path):
    """Fix image references in front matter to match actual files."""
    index_file = folder_path / 'index.md'
    
    if not index_file.exists():
        return False
    
    # Get list of actual image files in the folder
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG'}
    actual_images = {f.name for f in folder_path.iterdir() if f.suffix in image_extensions}
    
    if not actual_images:
        return False
    
    # Read the content
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find and fix image references in front matter
    # Match patterns like: image: "/images/ss/filename.ext"
    def replace_image_ref(match):
        prefix = match.group(1)  # field name and quotes
        old_path = match.group(2)  # the path
        suffix = match.group(3)  # closing quote
        
        # Extract filename from path
        old_filename = os.path.basename(old_path)
        base_name = os.path.splitext(old_filename)[0]
        
        # Find matching actual file (case-insensitive basename match)
        for actual_file in actual_images:
            actual_base = os.path.splitext(actual_file)[0]
            if actual_base.lower() == base_name.lower():
                return f'{prefix}{actual_file}{suffix}'
        
        # If no match found, return original
        return match.group(0)
    
    # Match image fields in front matter
    pattern = r'((?:image|ogImage|cover_image):\s*["\']?)(/images/ss/[^"\'\s]+|https?://[^"\'\s]+)(["\']?)'
    content = re.sub(pattern, replace_image_ref, content)
    
    # Write back if changed
    if content != original_content:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    success_stories_dir = Path('content/success-stories')
    
    if not success_stories_dir.exists():
        print(f"Error: {success_stories_dir} not found")
        return
    
    fixed_count = 0
    
    for folder in sorted(success_stories_dir.iterdir()):
        if folder.is_dir() and folder.name != '_index':
            if fix_frontmatter_images(folder):
                print(f"Fixed: {folder.name}")
                fixed_count += 1
    
    print(f"\nTotal fixed: {fixed_count}")

if __name__ == '__main__':
    main()
