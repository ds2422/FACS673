import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self, api_key=None):
        """Initialize YouTube API client.
        
        Args:
            api_key (str, optional): YouTube Data API v3 key. If not provided,
                will try to get from YOUTUBE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def get_video_info(self, video_id):
        """Get video information using YouTube Data API.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video information including title, description, etc.
            None: If video not found or error occurred
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.warning(f"No video found with ID: {video_id}")
                return None
                
            item = response['items'][0]
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            
            return {
                'id': video_id,
                'title': snippet.get('title', 'No title available'),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'thumbnails': snippet.get('thumbnails', {}),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'duration': item.get('contentDetails', {}).get('duration', '')
            }
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            logger.error(f"YouTube API error: {error_details}")
            return None
        except Exception as e:
            logger.error(f"Error fetching YouTube video info: {str(e)}")
            return None
    
    def get_transcript(self, video_id):
        """Get video transcript if available.
        Note: This requires additional handling and may not work for all videos.
        """
        try:
            transcript_list = YouTubeAPI.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            return transcript.fetch()
        except Exception as e:
            logger.warning(f"Could not fetch transcript: {str(e)}")
            return None

# Helper function to get a YouTube API client instance
def get_youtube_client():
    """Get an instance of YouTubeAPI with API key from settings."""
    from django.conf import settings
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    return YouTubeAPI(api_key=api_key)
