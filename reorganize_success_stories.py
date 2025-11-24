#!/usr/bin/env python3
"""
Reorganize success stories into page bundles and copy images for optimization
"""

import os
import re
import shutil
from pathlib import Path

# Configuration
CONTENT_DIR = Path(__file__).parent / "content" / "success-stories"
STATIC_IMAGES = Path(__file__).parent / "static" / "images" / "ss"

def extract_slug_from_filename(filename):
    """Extract slug from filename (remove .md extension)"""
    return filename.replace('.md', '')

def find_images_in_content(content):
    """Find all image references in markdown content"""
    images = set()
    
    # Markdown images: ![alt](/images/ss/image.jpg) or ![alt](image.jpg)
    md_pattern = r'!\[.*?\]\(([^)]+)\)'
    for match in re.findall(md_pattern, content):
        images.add(match)
    
    # Front matter image field: image: "/images/ss/salamander-1.png"
    fm_pattern = r'(?:image|ogImage|cover_image):\s*["\']?([^"\'\n]+)["\']?'
    for match in re.findall(fm_pattern, content):
        images.add(match)
    
    # Hugo figure shortcode: {{< figure src="/images/ss/image.jpg" >}}
    figure_pattern = r'{{\s*<\s*figure[^>]*src\s*=\s*["\']([^"\']+)["\']'
    for match in re.findall(figure_pattern, content):
        images.add(match)
    
    return images

def get_image_local_path(image_ref, static_images):
    """Get local path for an image reference"""
    # Skip external URLs
    if image_ref.startswith(('http://', 'https://', '//')):
        return None
    
    # Handle /images/ss/ paths
    if '/images/ss/' in image_ref:
        filename = os.path.basename(image_ref)
        source_path = static_images / filename
        if source_path.exists():
            return source_path
    
    # Handle direct filenames
    filename = os.path.basename(image_ref)
    source_path = static_images / filename
    if source_path.exists():
        return source_path
    
    return None

def update_image_references(content, images_to_update):
    """Update image paths to be relative filenames"""
    updated_content = content
    
    for old_path in images_to_update:
        filename = os.path.basename(old_path)
        
        # Update markdown images
        updated_content = re.sub(
            r'!\[(.*?)\]\(' + re.escape(old_path) + r'\)',
            r'![\1](' + filename + ')',
            updated_content
        )
        
        # Update front matter images
        updated_content = re.sub(
            r'((?:image|ogImage|cover_image):\s*["\']?)' + re.escape(old_path) + r'(["\']?)',
            r'\1' + filename + r'\2',
            updated_content
        )
        
        # Update figure shortcodes
        updated_content = re.sub(
            r'({{<\s*figure[^>]*src\s*=\s*["\'])' + re.escape(old_path) + r'(["\'])',
            r'\1' + filename + r'\2',
            updated_content
        )
    
    return updated_content

def reorganize_success_story(md_file, static_images):
    """Reorganize a single success story into a page bundle"""
    slug = extract_slug_from_filename(md_file.name)
    
    # Skip _index.md
    if slug == '_index':
        return False
    
    print(f"\nProcessing: {md_file.name}")
    
    # Read the content
    content = md_file.read_text(encoding='utf-8')
    
    # Find all images
    all_images = find_images_in_content(content)
    
    # Create the folder
    folder_path = CONTENT_DIR / slug
    folder_path.mkdir(exist_ok=True)
    
    # Copy images and collect paths to update
    images_to_update = []
    copied_count = 0
    
    for image_ref in all_images:
        source_path = get_image_local_path(image_ref, static_images)
        
        if source_path and source_path.exists():
            filename = source_path.name
            dest_path = folder_path / filename
            
            if not dest_path.exists():
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"  ✓ Copied: {filename}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ✗ Error copying {filename}: {e}")
            
            images_to_update.append(image_ref)
    
    # Update image references in content
    if images_to_update:
        content = update_image_references(content, images_to_update)
        print(f"  ✓ Updated {len(images_to_update)} image references")
    
    # Write index.md
    index_path = folder_path / "index.md"
    index_path.write_text(content, encoding='utf-8')
    print(f"  ✓ Created: {index_path.relative_to(CONTENT_DIR.parent)}")
    
    return True

def main():
    print("=" * 60)
    print("Success Stories Reorganization Script")
    print("=" * 60)
    print()
    
    # Find all markdown files (excluding _index.md)
    md_files = [f for f in CONTENT_DIR.glob("*.md") if f.name != '_index.md']
    
    print(f"Found {len(md_files)} success stories to process")
    print(f"Content directory: {CONTENT_DIR}")
    print(f"Static images: {STATIC_IMAGES}")
    print()
    
    if not STATIC_IMAGES.exists():
        print(f"Warning: Static images directory not found: {STATIC_IMAGES}")
        print("Images will not be copied, but paths will be updated.")
        print()
    
    response = input("Proceed with reorganization? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    processed = 0
    for md_file in sorted(md_files):
        if reorganize_success_story(md_file, STATIC_IMAGES):
            processed += 1
            # Remove the original file after successful reorganization
            try:
                md_file.unlink()
                print(f"  ✓ Removed original: {md_file.name}")
            except Exception as e:
                print(f"  ✗ Error removing original {md_file.name}: {e}")
    
    print()
    print("=" * 60)
    print(f"Reorganization complete!")
    print(f"Processed: {processed} success stories")
    print("=" * 60)

if __name__ == "__main__":
    main()
