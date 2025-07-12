"""
Utility functions for the blog system.
"""

import re
import os
import logging
from urllib.parse import urlparse
from typing import List, Optional

def clean_filename(filename: str) -> str:
    """Clean filename for safe file operations."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('.')
    return filename[:100]  # Limit length

def is_valid_image_url(url: str) -> bool:
    """Check if URL is a valid image URL."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for common image extensions
        path = parsed.path.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # Check if URL ends with image extension or contains image indicators
        has_extension = any(path.endswith(ext) for ext in image_extensions)
        has_image_indicator = any(indicator in url.lower() for indicator in ['image', 'img', 'photo', 'pic'])
        
        return has_extension or has_image_indicator
        
    except Exception:
        return False

def setup_logging(level=logging.INFO) -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('blog_system.log')
        ]
    )
    return logging.getLogger(__name__)

def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'

def extract_excerpt_from_content(content: str, max_length: int = 200) -> str:
    """Extract excerpt from article content."""
    # Remove HTML tags
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Get first paragraph or first few sentences
    sentences = clean_content.split('.')
    excerpt = ""
    
    for sentence in sentences:
        if len(excerpt + sentence) < max_length:
            excerpt += sentence + "."
        else:
            break
    
    return excerpt.strip() or clean_content[:max_length] + "..."

def generate_post_id(title: str) -> str:
    """Generate URL-friendly post ID from title."""
    # Convert to lowercase and replace spaces with hyphens
    post_id = title.lower()
    post_id = re.sub(r'[^\w\s-]', '', post_id)  # Remove special characters
    post_id = re.sub(r'[-\s]+', '-', post_id)   # Replace spaces and multiple hyphens
    post_id = post_id.strip('-')                # Remove leading/trailing hyphens
    
    return post_id[:50]  # Limit length
