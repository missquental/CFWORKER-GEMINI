"""
Configuration settings for the blog system.
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration class for blog system."""
    
    # Gemini AI settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.9
    GEMINI_MAX_TOKENS: int = 8192
    
    # Bing Image settings
    MAX_IMAGES_PER_POST: int = 3
    IMAGE_SEARCH_TIMEOUT: int = 30
    
    # Content generation settings
    MIN_ARTICLE_LENGTH: int = 1000
    DEFAULT_LANGUAGE: str = "id"  # Indonesian
    
    # Cloudflare Worker settings
    WORKER_SCRIPT_TIMEOUT: int = 60
    
    def __post_init__(self):
        """Load environment variables after initialization."""
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', self.GEMINI_API_KEY)
