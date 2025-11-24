#!/usr/bin/env python3
"""Convert markdown images to figure shortcode in success stories."""

import re
from pathlib import Path

def convert_markdown_images_to_figure(content):
    """Convert markdown image syntax to figure shortcode."""
    
    # Pattern: ![alt text](image.jpg)
    # Replace with: {{< figure src="image.jpg" alt="alt text" caption="" >}}
    def replace_image(match):
        alt_text = match.group(1)
        src = match.group(2)
        
        # Skip external URLs (already handled by figure shortcode)
        if src.startswith(('http://', 'https://')):
            return f'{{{{< figure src="{src}" alt="{alt_text}" caption="" >}}}}'
        
        # Local images
        return f'{{{{< figure src="{src}" alt="{alt_text}" caption="" >}}}}'
    
    # Match markdown images: ![alt](src)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    updated_content = re.sub(pattern, replace_image, content)
    
    return updated_content

def process_success_story(folder_path):
    """Convert images in a success story to figure shortcode."""
    index_file = folder_path / 'index.md'
    
    if not index_file.exists():
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Convert markdown images to figure shortcode
    updated_content = convert_markdown_images_to_figure(content)
    
    if updated_content != original_content:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    
    return False

def main():
    success_stories_dir = Path('content/success-stories')
    
    if not success_stories_dir.exists():
        print(f"Error: {success_stories_dir} not found")
        return
    
    converted_count = 0
    
    for folder in sorted(success_stories_dir.iterdir()):
        if folder.is_dir() and folder.name != '_index':
            if process_success_story(folder):
                print(f"Converted: {folder.name}")
                converted_count += 1
    
    print(f"\nTotal converted: {converted_count}")

if __name__ == '__main__':
    main()
