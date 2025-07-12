"""
Bing image scraper for downloading relevant images.
This module handles searching and downloading images from Bing without using Selenium.
"""

import os
import requests
import time
import random
import json
import urllib.parse
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image
import logging
from utils import clean_filename, is_valid_image_url
from config import Config

class BingImageScraper:
    """Scraper for Bing image search using requests and BeautifulSoup."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with appropriate headers."""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_soup(self, url):
        """Get BeautifulSoup object from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            self.logger.error(f"Error getting soup from {url}: {str(e)}")
            return None
    
    def search_images(self, query, max_images=10):
        """
        Search for images on Bing.
        
        Args:
            query (str): Search query
            max_images (int): Maximum number of images to find
            
        Returns:
            list: List of image URLs
        """
        try:
            # Format query for URL
            query_encoded = '+'.join(query.split())
            search_url = f"https://www.bing.com/images/search?q={query_encoded}&form=HDRSC2&first=1&tsc=ImageBasicHover"
            
            self.logger.info(f"Searching for images: {query}")
            
            # Get the search page
            soup = self.get_soup(search_url)
            if not soup:
                return []
            
            # Find image elements with JSON data
            image_elements = soup.find_all("a", {"class": "iusc"})
            
            image_urls = []
            for element in image_elements[:max_images * 2]:  # Get more to filter out invalid ones
                try:
                    # Extract JSON data from the element
                    m_attr = element.get("m")
                    if m_attr:
                        m_data = json.loads(m_attr)
                        img_url = m_data.get("murl")  # Main image URL
                        
                        if img_url and is_valid_image_url(img_url):
                            # Skip data URLs and very small images
                            if not img_url.startswith('data:') and 'base64' not in img_url:
                                image_urls.append(img_url)
                                
                                if len(image_urls) >= max_images:
                                    break
                                    
                except Exception as e:
                    self.logger.debug(f"Error extracting image URL: {str(e)}")
                    continue
            
            self.logger.info(f"Found {len(image_urls)} image URLs")
            return image_urls
            
        except Exception as e:
            self.logger.error(f"Error searching images: {str(e)}")
            return []
    
    def download_image(self, url, filename):
        """
        Download a single image.
        
        Args:
            url (str): Image URL
            filename (str): Local filename to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if the response is actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                self.logger.warning(f"URL doesn't return image content: {url}")
                return False
            
            # Save the image
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify the image is valid and resize if needed
            try:
                with Image.open(filename) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Resize if too large
                    max_size = (1200, 800)
                    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        img.save(filename, 'JPEG', quality=85)
                        self.logger.info(f"Resized image: {filename}")
                    
                    self.logger.info(f"Downloaded image: {filename} ({img.size[0]}x{img.size[1]})")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Error processing image {filename}: {str(e)}")
                # Remove invalid image file
                try:
                    os.remove(filename)
                except:
                    pass
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading image from {url}: {str(e)}")
            return False
    
    def get_image_urls(self, query, max_images=3):
        """
        Get image URLs for a given query without downloading.
        
        Args:
            query (str): Search query
            max_images (int): Maximum number of images to get
            
        Returns:
            list: List of image URLs for hotlinking
        """
        try:
            # Search for images
            image_urls = self.search_images(query, max_images * 2)  # Get more URLs to ensure we get enough valid images
            
            if not image_urls:
                self.logger.warning(f"No images found for query: {query}")
                return []
            
            # Filter and validate URLs
            valid_urls = []
            for url in image_urls:
                if len(valid_urls) >= max_images:
                    break
                    
                if is_valid_image_url(url):
                    valid_urls.append(url)
                    self.logger.info(f"Found valid image URL: {url[:100]}...")
            
            self.logger.info(f"Found {len(valid_urls)} valid image URLs for query: {query}")
            return valid_urls
            
        except Exception as e:
            self.logger.error(f"Error in get_image_urls: {str(e)}")
            return []

    def download_images(self, query, max_images=3):
        """
        Download images for a given query.
        
        Args:
            query (str): Search query
            max_images (int): Maximum number of images to download
            
        Returns:
            list: List of downloaded image file paths
        """
        # Search for images
        image_urls = self.search_images(query, max_images * 3)  # Get more URLs to ensure we get enough valid images
        
        if not image_urls:
            self.logger.warning(f"No images found for query: {query}")
            return []
        
        # Create images directory if it doesn't exist
        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Download images
        downloaded_paths = []
        query_clean = clean_filename(query)
        
        for i, url in enumerate(image_urls):
            if len(downloaded_paths) >= max_images:
                break
                
            try:
                # Generate filename
                url_path = urlparse(url).path
                extension = os.path.splitext(url_path)[1].lower()
                if not extension or extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    extension = '.jpg'
                
                filename = f"{query_clean}_{i+1}{extension}"
                filepath = os.path.join(images_dir, filename)
                
                # Download the image
                if self.download_image(url, filepath):
                    downloaded_paths.append(filepath)
                    self.logger.info(f"Successfully downloaded: {filepath}")
                else:
                    self.logger.warning(f"Failed to download image {i+1}")
                    
            except Exception as e:
                self.logger.error(f"Error downloading image {i+1}: {str(e)}")
                continue
        
        self.logger.info(f"Downloaded {len(downloaded_paths)} images for query: {query}")
        return downloaded_paths
    
    def close(self):
        """Close the session."""
        try:
            self.session.close()
            self.logger.info("Image scraper session closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing session: {str(e)}")
