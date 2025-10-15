import json
import logging
import re
import heapq
import nltk
import requests
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
from bs4 import BeautifulSoup
from .youtube_utils import get_youtube_client
from .models import UploadedContent
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .file_handlers import handle_file_upload
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

def download_nltk_data():
    for resource in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

download_nltk_data()

@csrf_exempt
def upload_multipart(request):
    if request.method != 'POST':
        return JsonResponse(
            {"success": False, "message": "Only POST method is allowed"},
            status=405
        )

    result = handle_file_upload(request)

    if isinstance(result, dict):
        status_code = 200 if result.get('success', False) else 400
        return JsonResponse(result, status=status_code)
    else:
        return JsonResponse(
            {"success": False, "message": str(result)},
            status=500
        )
    
@csrf_exempt
def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    logger.info(f"Extracting ID from URL: {url}")
    
    # Handle youtu.be/ID format
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        if len(video_id) == 11:  # Standard YouTube ID length
            logger.info(f"Extracted ID from youtu.be/: {video_id}")
            return video_id
    
    # Handle youtube.com/watch?v=ID format
    if 'youtube.com/watch' in url:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(url)
        video_id = parse_qs(parsed_url.query).get('v', [''])[0]
        if video_id and len(video_id) == 11:
            logger.info(f"Extracted ID from youtube.com/watch: {video_id}")
            return video_id
    
    # Handle youtube.com/embed/ID format
    if 'youtube.com/embed/' in url:
        video_id = url.split('youtube.com/embed/')[-1].split('?')[0].split('&')[0]
        if len(video_id) == 11:
            logger.info(f"Extracted ID from youtube.com/embed/: {video_id}")
            return video_id
    
    # Fallback to regex pattern matching
    patterns = [
        r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})',
        r'youtube\.com\/watch\?.*v=([^&]*)',
        r'youtu\.be\/([^?]*)',
        r'youtube\.com\/embed\/([^?]*)',
        r'youtube\.com\/v\/([^?]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match and match.group(1):
            video_id = match.group(1)
            if len(video_id) == 11:  # Validate ID length
                logger.info(f"Extracted ID using regex: {video_id}")
                return video_id
    
    logger.warning(f"Could not extract video ID from URL: {url}")
    return None

def get_youtube_video_info(video_id):
    """Fetch video information using YouTube Data API."""
    try:
        logger.info(f"Fetching info for video ID: {video_id}")
        
        youtube = get_youtube_client()
        video_info = youtube.get_video_info(video_id)
        
        if not video_info:
            logger.warning(f"Could not fetch video info for ID: {video_id}")
            return None
            
        logger.info(f"Successfully fetched video info for ID: {video_id}")
        return {
            'title': video_info.get('title', 'Untitled Video'),
            'description': video_info.get('description', ''),
            'thumbnail_url': video_info.get('thumbnails', {}).get('high', {}).get('url', ''),
            'author_name': video_info.get('channel_title', ''),
            'view_count': video_info.get('view_count', 0),
            'like_count': video_info.get('like_count', 0),
            'published_at': video_info.get('published_at', '')
        }
        
    except Exception as e:
        logger.error(f"Error in get_youtube_video_info: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error fetching YouTube video info: {str(e)}")
        return None

def upload_binary(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    body = request.body
    if not body:
        return JsonResponse({"success": False, "message": "Empty body"}, status=400)
    filename = request.headers.get('X-Filename') or 'uploaded.bin'
    saved = default_storage.save(filename, ContentFile(body))
    return JsonResponse({"success": True, "filename": saved, "mode": "raw-binary"})

@csrf_exempt
@require_http_methods(["POST"])
def summarize_text(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    text = data.get('text')
    url = data.get('url')
    num_sentences = int(data.get('num_sentences', 3))

    if not text and not url:
        return JsonResponse({"success": False, "message": "Provide either 'text' or 'url'"}, status=400)

    if url:
        if 'youtube.com' in url or 'youtu.be' in url:
            try:
                logger.info(f"Processing YouTube URL: {url}")
                video_id = extract_youtube_id(url)
                logger.info(f"Extracted video ID: {video_id}")
                
                if not video_id:
                    logger.error(f"Could not extract video ID from URL: {url}")
                    return JsonResponse({
                        "success": False, 
                        "message": "Could not extract video ID from the URL. Please check if it's a valid YouTube URL.",
                        "url": url
                    }, status=400)
                
                logger.info(f"Fetching video info for ID: {video_id}")
                video_info = get_youtube_video_info(video_id)
                
                if not video_info:
                    logger.warning(f"Could not fetch info for video ID: {video_id}")
                    # Try to get basic info from the page directly
                    try:
                        response = requests.get(
                            f'https://www.youtube.com/watch?v={video_id}',
                            headers={'User-Agent': 'Mozilla/5.0'},
                            timeout=10
                        )
                        if response.status_code == 200:
                            # Try to extract title from HTML
                            soup = BeautifulSoup(response.text, 'html.parser')
                            title = soup.find('title')
                            if title:
                                return JsonResponse({
                                    "success": True,
                                    "title": title.text.replace(' - YouTube', '').strip(),
                                    "message": "Limited information available. Full details require a public video.",
                                    "summary": f"Video: {title.text.replace(' - YouTube', '').strip()}\n\nFull description not available. The video might be private or age-restricted.",
                                    "source": "youtube"
                                })
                    except Exception as e:
                        logger.error(f"Error fetching video page: {str(e)}")
                    
                    return JsonResponse({
                        "success": False,
                        "message": "Could not fetch video information. The video might be private, unlisted, or unavailable in your region.",
                        "video_id": video_id
                    }, status=400)
                
                # Format the text with title and description
                text = f"{video_info.get('title', 'Untitled Video')}\n\n{video_info.get('description', '')}"
                if not text.strip():
                    text = f"Video: {video_info.get('title', 'Untitled Video')}\n\nNo description available. Please provide a text summary or use the video description."
            except Exception as e:
                logger.error(f"Error processing YouTube URL: {str(e)}")
                return JsonResponse({"success": False, "message": "Error processing YouTube video", "error": str(e)}, status=400)
        else:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.google.com/',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')
                for element in soup(["script", "style", "nav", "footer", "header", "iframe", "form", "button"]):
                    element.decompose()
                paragraphs = []
                for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section']):
                    paragraphs.append(tag.get_text(separator=' ', strip=True))
                text = ' '.join(paragraphs)
                text = re.sub(r'\s+', ' ', text).strip()
            except requests.exceptions.RequestException as e:
                return JsonResponse({"success": False, "message": "Failed to fetch URL. The website might be blocking automated requests.", "error": str(e)}, status=400)
            except Exception as e:
                return JsonResponse({"success": False, "message": "An error occurred while processing the URL", "error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def summarize_text(request):
    try:
        # Parse request data
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()
                if not data and request.body:
                    data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        # Get parameters
        text = data.get('text', '')
        url = data.get('url', '')
        title = data.get('title', 'Untitled')
        content_type = data.get('content_type', 'other')
        num_sentences = int(data.get('num_sentences', 3))

        if not text and not url:
            return JsonResponse({"success": False, "message": "Provide either 'text' or 'url'"}, status=400)

        # Process URL if provided
        if url:
            if 'youtube.com' in url or 'youtu.be' in url:
                content_type = 'youtube'
                try:
                    logger.info(f"Processing YouTube URL: {url}")
                    video_id = extract_youtube_id(url)
                    logger.info(f"Extracted video ID: {video_id}")
                    
                    if not video_id:
                        logger.error(f"Could not extract video ID from URL: {url}")
                        return JsonResponse({
                            "success": False, 
                            "message": "Could not extract video ID from the URL. Please check if it's a valid YouTube URL.",
                            "url": url
                        }, status=400)
                    
                    logger.info(f"Fetching video info for ID: {video_id}")
                    video_info = get_youtube_video_info(video_id)
                    
                    if not video_info:
                        logger.warning(f"Could not fetch info for video ID: {video_id}")
                        # Try to get basic info from the page directly
                        try:
                            response = requests.get(
                                f'https://www.youtube.com/watch?v={video_id}',
                                headers={'User-Agent': 'Mozilla/5.0'},
                                timeout=10
                            )
                            if response.status_code == 200:
                                # Try to extract title from HTML
                                soup = BeautifulSoup(response.text, 'html.parser')
                                title_tag = soup.find('title')
                                if title_tag:
                                    title = title_tag.text.replace(' - YouTube', '').strip()
                                    text = f"Video: {title}\n\nFull description not available. The video might be private or age-restricted."
                                    summary = text  # Use the same text as summary since we can't get more
                                    
                                    # Save to database
                                    save_to_database(request, url, title, content_type, text, summary)
                                    
                                    return JsonResponse({
                                        "success": True,
                                        "title": title,
                                        "summary": summary,
                                        "message": "Limited information available. Full details require a public video.",
                                        "source": "youtube",
                                        "saved_to_db": True
                                    })
                        except Exception as e:
                            logger.error(f"Error fetching video page: {str(e)}")
                        
                        return JsonResponse({
                            "success": False,
                            "message": "Could not fetch video information. The video might be private, unlisted, or unavailable in your region.",
                            "video_id": video_id
                        }, status=400)
                    
                    # Format the text with title and description
                    title = video_info.get('title', 'Untitled Video')
                    text = f"{title}\n\n{video_info.get('description', '')}"
                    if not text.strip():
                        text = f"Video: {title}\n\nNo description available. Please provide a text summary or use the video description."
                        
                except Exception as e:
                    logger.error(f"Error processing YouTube URL: {str(e)}")
                    return JsonResponse({"success": False, "message": "Error processing YouTube video", "error": str(e)}, status=400)
            else:
                content_type = 'article'
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Referer': 'https://www.google.com/',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get title if not provided
                    if not title or title == 'Untitled':
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.text.strip()
                    
                    # Clean up the document
                    for element in soup(["script", "style", "nav", "footer", "header", "iframe", "form", "button"]):
                        element.decompose()
                    
                    # Extract main content
                    paragraphs = []
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section']):
                        paragraphs.append(tag.get_text(separator=' ', strip=True))
                    
                    text = ' '.join(paragraphs)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                except requests.exceptions.RequestException as e:
                    return JsonResponse({
                        "success": False, 
                        "message": "Failed to fetch URL. The website might be blocking automated requests.", 
                        "error": str(e)
                    }, status=400)
                except Exception as e:
                    return JsonResponse({
                        "success": False, 
                        "message": "An error occurred while processing the URL", 
                        "error": str(e)
                    }, status=500)
        
        # At this point, we should have text to process
        if not text:
            return JsonResponse({"success": False, "message": "No content to summarize"}, status=400)
        
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        
        # If we have very few sentences, just return the text as is
        if len(sentences) <= num_sentences:
            summary = text
        else:
            # Tokenize words and build frequency table
            stop_words = set(stopwords.words('english'))
            word_frequencies = defaultdict(int)
            
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                for word in words:
                    if word not in stop_words and word.isalnum():
                        word_frequencies[word] += 1
            
            # Calculate sentence scores
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                sentence_scores[i] = 0
                words = word_tokenize(sentence.lower())
                for word in words:
                    if word in word_frequencies:
                        sentence_scores[i] += word_frequencies[word]
            
            # Get top N sentences
            top_sentences = heapq.nlargest(
                num_sentences, 
                sentence_scores, 
                key=sentence_scores.get
            )
            
            # Sort the sentences by their original order
            top_sentences.sort()
            
            # Create the summary
            summary = ' '.join([sentences[i] for i in top_sentences])
        
        # Save to database if URL is provided
        saved = False
        if url:
            try:
                saved = save_to_database(request, url, title, content_type, text, summary)
            except Exception as e:
                logger.error(f"Error saving to database: {str(e)}")
        
        return JsonResponse({
            "success": True,
            "title": title,
            "summary": summary,
            "original_length": len(sentences),
            "summary_length": len(sentences),
            "saved_to_db": saved
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in summarize_text: {str(e)}")
        return JsonResponse({
            "success": False,
            "message": "An unexpected error occurred",
            "error": str(e)
        }, status=500)

def save_to_database(request, url, title, content_type, content, summary):
    """Helper function to save content to database."""
    try:
        # Get the user (assuming you have user authentication)
        User = get_user_model()
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        # Create the record
        UploadedContent.objects.create(
            user=user,
            url=url,
            title=title,
            content_type=content_type,
            content=content,
            summary=summary
        )
        return True
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return False