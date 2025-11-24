#!/usr/bin/env python3
"""
Copy blog images from static/wp-content/uploads to blog post folders
"""

import os
import re
import shutil
from pathlib import Path

# Configuration
BLOG_DIR = Path(__file__).parent / "content" / "blog"
STATIC_UPLOADS = Path(__file__).parent / "static" / "wp-content" / "uploads"

def find_images_in_content(content):
    """Find all image references in markdown content"""
    images = set()
    
    # Hugo figure shortcode: {{< figure src="image.jpg" >}}
    figure_pattern = r'{{\s*<\s*figure[^>]*src\s*=\s*["\']([^"\']+)["\']'
    images.update(re.findall(figure_pattern, content))
    
    # Markdown images: ![alt](image.jpg)
    md_pattern = r'!\[.*?\]\(([^)]+)\)'
    images.update(re.findall(md_pattern, content))
    
    # HTML img tags: <img src="image.jpg">
    html_pattern = r'<img[^>]*src\s*=\s*["\']([^"\']+)["\']'
    images.update(re.findall(html_pattern, content))
    
    return images

def get_image_source_path(image_ref, static_uploads):
    """Find the source path of an image in static/wp-content/uploads"""
    # Clean up the reference
    image_ref = image_ref.strip()
    
    # Skip external URLs
    if image_ref.startswith(('http://', 'https://', '//')):
        return None
    
    # Extract filename if it's a path
    filename = os.path.basename(image_ref)
    
    # Search for the file in static/wp-content/uploads
    for root, dirs, files in os.walk(static_uploads):
        if filename in files:
            return Path(root) / filename
    
    return None

def copy_images_for_post(post_folder):
    """Copy all referenced images to a blog post folder"""
    index_md = post_folder / "index.md"
    
    if not index_md.exists():
        return 0
    
    # Read the content
    content = index_md.read_text(encoding='utf-8')
    
    # Find all images
    images = find_images_in_content(content)
    
    copied_count = 0
    for image_ref in images:
        # Get source path
        source_path = get_image_source_path(image_ref, STATIC_UPLOADS)
        
        if source_path and source_path.exists():
            # Get just the filename for destination
            filename = source_path.name
            dest_path = post_folder / filename
            
            # Copy if not already there
            if not dest_path.exists():
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"  ✓ Copied: {filename}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ✗ Error copying {filename}: {e}")
            else:
                print(f"  - Already exists: {filename}")
    
    return copied_count

def main():
    print("=" * 60)
    print("Copy Blog Images to Post Folders")
    print("=" * 60)
    print()
    
    if not BLOG_DIR.exists():
        print(f"Error: Blog directory not found: {BLOG_DIR}")
        return
    
    if not STATIC_UPLOADS.exists():
        print(f"Error: Static uploads directory not found: {STATIC_UPLOADS}")
        return
    
    # Find all blog post folders
    blog_folders = [d for d in BLOG_DIR.iterdir() if d.is_dir() and (d / "index.md").exists()]
    
    print(f"Found {len(blog_folders)} blog post folders")
    print(f"Blog directory: {BLOG_DIR}")
    print(f"Static uploads: {STATIC_UPLOADS}")
    print()
    
    total_copied = 0
    
    for post_folder in sorted(blog_folders):
        post_name = post_folder.name
        print(f"Processing: {post_name}")
        
        copied = copy_images_for_post(post_folder)
        total_copied += copied
    
    print()
    print("=" * 60)
    print(f"Complete! Copied {total_copied} images")
    print("=" * 60)

if __name__ == "__main__":
    main()
