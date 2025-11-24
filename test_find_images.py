#!/usr/bin/env python3
from pathlib import Path
import re
from urllib.parse import unquote

def find_images_in_content(content):
    images = []
    md_pattern = r'!\[.*?\]\((.*?)\)'
    hugo_pattern = r'\{\{<\s*figure\s+src="([^"]+)"'
    html_pattern = r'<img[^>]+src="([^"]+)"'
    
    for pattern in [md_pattern, hugo_pattern, html_pattern]:
        matches = re.findall(pattern, content)
        images.extend(matches)
    
    return images

# Test with qfield-3-2
md_file = Path('content/blog/qfield-3-2-congo-making-your-life-easier.md')
if md_file.exists():
    content = md_file.read_text()
    images = find_images_in_content(content)
    print(f'Found {len(images)} images:')
    for img in images:
        print(f'  - {img}')
else:
    print(f'File not found: {md_file}')
