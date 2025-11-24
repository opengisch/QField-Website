#!/usr/bin/env python3
"""
Script to reorganize blog entries into subfolders with their associated images.
Each blog post will be moved to its own folder with an index.md file,
and images will be copied to the same folder with updated references.
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

# Configuration
BLOG_DIR = Path("content/blog")
STATIC_WP_CONTENT = Path("static/wp-content/uploads")
IGNORE_FILES = ["_index.md"]

def extract_slug_from_filename(filename):
    """Extract slug from filename (remove .md extension)"""
    return filename.replace('.md', '')

def find_images_in_content(content):
    """Find all image references in markdown content"""
    images = []
    
    # Pattern for markdown images: ![alt](/path/to/image.ext)
    md_pattern = r'!\[.*?\]\((.*?)\)'
    # Pattern for Hugo shortcodes: {{< figure src="path" >}}
    hugo_pattern = r'\{\{<\s*figure\s+src="([^"]+)"'
    # Pattern for HTML img tags
    html_pattern = r'<img[^>]+src="([^"]+)"'
    
    for pattern in [md_pattern, hugo_pattern, html_pattern]:
        matches = re.findall(pattern, content)
        images.extend(matches)
    
    return images

def get_image_local_path(image_url):
    """Convert image URL to local file path"""
    # Decode URL-encoded characters
    image_url = unquote(image_url)
    
    # Strip query parameters (like ?fit=664,443&ssl=1)
    if '?' in image_url:
        image_url = image_url.split('?')[0]
    
    # Handle /blog/wp-content/uploads/ paths
    if '/blog/wp-content/uploads/' in image_url:
        # Extract the path after /blog/wp-content/
        rel_path = image_url.split('/blog/wp-content/')[1]
        return Path("static/wp-content") / rel_path
    
    # Handle /wp-content/uploads/ paths
    if '/wp-content/uploads/' in image_url:
        rel_path = image_url.split('/wp-content/')[1]
        return Path("static/wp-content") / rel_path
    
    # Skip external URLs
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return None
    
    return None

def update_image_references(content, image_mapping):
    """Update image references in content to use new relative paths"""
    updated_content = content
    
    for old_path, new_name in image_mapping.items():
        # Escape the old path for regex
        old_pattern = re.escape(old_path)
        
        # Escape backslashes in the replacement string
        escaped_new_name = new_name.replace('\\', '\\\\')
        
        # Handle Hugo shortcodes
        updated_content = re.sub(
            f'(\\{{{{<\\s*figure\\s+src=")[^"]*{old_pattern}',
            f'\\g<1>{escaped_new_name}',
            updated_content
        )
        
        # Handle markdown images
        updated_content = re.sub(
            f'(\\!\\[.*?\\]\\()[^)]*{old_pattern}',
            f'\\g<1>{escaped_new_name}',
            updated_content
        )
        
        # Handle HTML img tags
        updated_content = re.sub(
            f'(<img[^>]+src=")[^"]*{re.escape(old_path)}',
            f'\\g<1>{escaped_new_name}',
            updated_content
        )
    
    return updated_content

def reorganize_blog_entry(md_file):
    """Reorganize a single blog entry into its own folder"""
    slug = extract_slug_from_filename(md_file.name)
    
    # Skip index files
    if md_file.name in IGNORE_FILES:
        print(f"Skipping {md_file.name}")
        return
    
    print(f"\nProcessing: {slug}")
    
    # Create new folder for this blog entry
    new_folder = BLOG_DIR / slug
    
    # Skip if already reorganized
    if new_folder.exists() and (new_folder / "index.md").exists():
        print(f"  Already reorganized, skipping...")
        return
    
    new_folder.mkdir(exist_ok=True)
    
    # Read the markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all images referenced in the content
    images = find_images_in_content(content)
    print(f"  Found {len(images)} image references")
    
    # Copy images and build mapping for path updates
    image_mapping = {}
    copied_count = 0
    
    for img_url in images:
        local_path = get_image_local_path(img_url)
        
        if local_path and local_path.exists():
            # Copy image to new blog folder
            img_name = local_path.name
            # Handle duplicate names by preserving some path info
            if img_name in [v for v in image_mapping.values()]:
                # Add parent folder to name to avoid conflicts
                img_name = f"{local_path.parent.name}_{img_name}"
            
            dest_path = new_folder / img_name
            
            if not dest_path.exists():
                shutil.copy2(local_path, dest_path)
                copied_count += 1
            
            image_mapping[img_url] = img_name
            print(f"    Copied: {local_path.name}")
        elif local_path:
            print(f"    Warning: Image not found: {local_path}")
        else:
            print(f"    Skipping external/unknown: {img_url[:50]}...")
    
    print(f"  Copied {copied_count} images")
    
    # Update content with new image paths
    updated_content = update_image_references(content, image_mapping)
    
    # Write the updated content to index.md in new folder
    index_file = new_folder / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"  Created: {index_file}")
    
    # Remove the old markdown file
    md_file.unlink()
    print(f"  Removed: {md_file}")

def main():
    """Main function to reorganize all blog entries"""
    print("=" * 60)
    print("Blog Reorganization Script")
    print("=" * 60)
    
    # Check if blog directory exists
    if not BLOG_DIR.exists():
        print(f"Error: Blog directory not found: {BLOG_DIR}")
        return
    
    # Get all markdown files in blog directory
    md_files = [f for f in BLOG_DIR.iterdir() if f.is_file() and f.suffix == '.md']
    
    print(f"\nFound {len(md_files)} markdown files to process")
    print(f"Blog directory: {BLOG_DIR.absolute()}")
    print(f"Static uploads: {STATIC_WP_CONTENT.absolute()}")
    
    response = input("\nProceed with reorganization? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Process each blog entry
    for md_file in md_files:
        try:
            reorganize_blog_entry(md_file)
        except Exception as e:
            print(f"  Error processing {md_file.name}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("Reorganization complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
