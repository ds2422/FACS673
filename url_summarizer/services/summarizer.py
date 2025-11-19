import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import nltk
import logging
from collections import defaultdict
import heapq
import string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class URLSummarizer:
    def __init__(self):
        self.user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.stop_words = set(nltk.corpus.stopwords.words('english'))

    def _get_youtube_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return ""
                
            if parsed.hostname == 'youtu.be':
                return parsed.path[1:] or ""
                
            if parsed.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed.path == '/watch' and 'v' in parse_qs(parsed.query):
                    return parse_qs(parsed.query)['v'][0] or ""
                if parsed.path.startswith(('/embed/', '/v/')):
                    parts = parsed.path.split('/')
                    return parts[2] if len(parts) > 2 else ""
            return ""
        except Exception as e:
            logger.error(f"Error extracting YouTube video ID: {e}")
            return ""

    async def _get_youtube_transcript(self, video_id: str) -> str:
        """Get transcript for a YouTube video"""
        try:
            if not video_id:
                return ""
                
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            return ' '.join([entry['text'] for entry in transcript])
        except Exception as e:
            logger.warning(f"Could not get transcript: {e}")
            return ""

    async def _get_webpage_content(self, url: str) -> str:
        """Extract main content from a webpage"""
        try:
            response = requests.get(url, headers=self.user_agent, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
                
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            return text if text.strip() else "No readable content found"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return f"Error fetching content: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing webpage: {e}")
            return f"Error processing content: {str(e)}"

    def _summarize_text(self, text: str, num_sentences: int = 20) -> str:
        """Generate a summary from the given text using basic frequency analysis"""
        try:
            # Tokenize into sentences
            sentences = nltk.sent_tokenize(text)
            if len(sentences) <= num_sentences:
                return text
                
            # Tokenize and clean words
            words = [
                word.lower() for word in nltk.word_tokenize(text)
                if word.lower() not in self.stop_words 
                and word not in string.punctuation
                and word.isalnum()
            ]
            
            # Calculate word frequencies
            word_freq = defaultdict(int)
            for word in words:
                word_freq[word] += 1
                
            # Score sentences
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                words_in_sentence = [
                    word.lower() for word in nltk.word_tokenize(sentence)
                    if word.lower() not in self.stop_words 
                    and word not in string.punctuation
                    and word.isalnum()
                ]
                score = sum(word_freq[word] for word in words_in_sentence) / (len(words_in_sentence) + 1)
                sentence_scores.append((score, i, sentence))
            
            # Get top sentences
            top_sentences = heapq.nlargest(
                num_sentences,
                sentence_scores,
                key=lambda x: x[0]
            )
            
            # Sort by original position
            top_sentences.sort(key=lambda x: x[1])
            
            # Join the sentences
            return ' '.join(sentence for _, _, sentence in top_sentences)
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return "Error generating summary."

    async def summarize(self, url: str, summary_length: int = 20) -> dict:
        """Main method to summarize content from a URL"""
        try:
            logger.info(f"Processing URL: {url}")
            
            # Validate input
            if not url or not isinstance(url, str) or not url.strip():
                raise ValueError("URL cannot be empty")
                
            if not isinstance(summary_length, int) or summary_length < 1:
                summary_length = 50
                
            # Check if it's a YouTube URL
            video_id = self._get_youtube_video_id(url)
            if video_id:
                logger.info(f"Processing YouTube video: {video_id}")
                content = await self._get_youtube_transcript(video_id)
                if not content:
                    return {"url": url, "summary": "No transcript available for this video."}
            else:
                logger.info("Processing as regular web page")
                content = await self._get_webpage_content(url)
                if not content or content.startswith("Error"):
                    return {"url": url, "summary": "Could not extract content from this URL."}
            
            # Generate and return summary
            summary = self._summarize_text(content, summary_length)
            return {"url": url, "summary": summary}
            
        except Exception as e:
            logger.error(f"Error in summarize: {e}")
            return {"url": url, "error": str(e)}