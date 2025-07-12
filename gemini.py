"""
Gemini AI content generator using official API.
This module handles interaction with Gemini AI using Google's official API.
"""

import os
import logging
from langdetect import detect, DetectorFactory
from langcodes import Language
import google.generativeai as genai
from config import Config

# Pastikan deteksi bahasa konsisten
DetectorFactory.seed = 0

class GeminiScraper:
    """Scraper for Gemini AI using official API."""
    
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.api_key = api_key
        self.model = None
        self._setup_gemini()
    
    def _read_api_keys(self, filename="apikey.txt"):
        """Read API keys from file."""
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as file:
                    keys = [line.strip() for line in file if line.strip() and not line.startswith('#')]
                return keys
            return []
        except Exception as e:
            self.logger.error(f"Error reading API keys from {filename}: {str(e)}")
            return []
    
    def _setup_gemini(self):
        """Setup Gemini AI API."""
        try:
            # Get API key from multiple sources
            if not self.api_key:
                self.api_key = os.getenv('GEMINI_API_KEY')
            
            # If still no API key, try to read from file
            if not self.api_key:
                api_keys = self._read_api_keys()
                if api_keys:
                    self.api_key = api_keys[0]  # Use first API key
                    self.logger.info("Using API key from apikey.txt file")
            
            if not self.api_key:
                raise ValueError("Gemini API key not found. Please:\n"
                               "1. Set GEMINI_API_KEY environment variable, or\n"
                               "2. Provide via --api-key parameter, or\n"
                               "3. Create apikey.txt file with your API key")
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Setup generation config
            generation_config = {
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
            
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                generation_config=generation_config
            )
            
            self.logger.info("Gemini API initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise
    
    def detect_language(self, subject):
        """Detect language of the subject."""
        try:
            lang_code = detect(subject)
            lang_name = Language.get(lang_code).display_name()
            return lang_name
        except:
            return "English"  # Default ke bahasa Inggris jika terjadi error
    
    def generate_title(self, subject, language):
        """Generate title for the article."""
        try:
            title_prompt = (
                f"Forget previous instructions. You are a professional clickbait-style blog title writer in {language}. "
                f"Come up with 1 unique, emotional, and curiosity-driven blog title for the topic: \"{subject}\". "
                f"The title must be under 60 characters, avoid clichés, and spark reader curiosity. "
                f"Use metaphor, emotion, or an unexpected twist. Do not repeat the subject word exactly."
            )
            
            response = self.model.generate_content(title_prompt)
            title = response.text.strip().replace('"', '').replace("**", "").replace("##", "")
            
            self.logger.info(f"Generated title: {title}")
            return title
            
        except Exception as e:
            self.logger.error(f"Error generating title: {str(e)}")
            return subject  # Fallback to original subject

    def generate_article(self, topic, language="id"):
        """
        Generate article content using Gemini AI.
        
        Args:
            topic (str): The topic for the article
            language (str): Language code (id=Indonesian, en=English)
            
        Returns:
            str: Generated article content or None if failed
        """
        try:
            # Detect language automatically
            detected_lang = self.detect_language(topic)
            
            # Generate title first
            title = self.generate_title(topic, detected_lang)
            
            # Create the prompt based on language
            if language == "id":
                article_prompt = f"""Buatkan artikel lengkap tentang "{title}" dalam bahasa Indonesia dengan struktur sebagai berikut:

1. Judul yang menarik dan SEO-friendly
2. Pendahuluan yang engaging (100-150 kata)
3. Isi artikel yang informatif dengan beberapa subheading (minimal 5 subheading)
4. Kesimpulan yang kuat dan actionable (100-150 kata)
5. Panjang total minimal 1000 kata

Pastikan artikel:
- Berkualitas tinggi dan informatif
- Menggunakan gaya penulisan yang profesional namun mudah dipahami
- Mengandung informasi yang akurat dan up-to-date
- Terstruktur dengan baik menggunakan heading dan subheading
- Menggunakan bullet points atau numbered lists jika perlu
- Menarik untuk dibaca dan memberikan value kepada pembaca

Gunakan format markdown untuk heading dan formatting."""
            else:
                article_prompt = f"""Write a comprehensive article about "{title}" in English with the following structure:

1. Engaging and SEO-friendly title
2. Compelling introduction (100-150 words)
3. Informative content with multiple subheadings (minimum 5 subheadings)
4. Strong and actionable conclusion (100-150 words)
5. Total length minimum 1000 words

Ensure the article:
- Is high-quality and informative
- Uses professional yet accessible writing style
- Contains accurate and up-to-date information
- Is well-structured with proper headings and subheadings
- Uses bullet points or numbered lists when appropriate
- Is engaging to read and provides value to readers

Use markdown format for headings and formatting."""
            
            # Generate the article
            response = self.model.generate_content(article_prompt)
            article_content = response.text.strip()
            
            if article_content and len(article_content) > 200:
                self.logger.info(f"Successfully generated article content ({len(article_content)} characters)")
                return article_content
            else:
                self.logger.warning("Generated content is too short or empty")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating article: {str(e)}")
            return None
    
    def close(self):
        """Close the API connection (no cleanup needed for API)."""
        self.logger.info("Gemini API connection closed")
