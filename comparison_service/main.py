from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import googleapiclient.discovery
from collections import Counter
import re

# Initialize FastAPI app
app = FastAPI(
    title="Document Comparison Service",
    description="Microservice that compares documents or URLs and generates smart summaries.",
    version="2.0.0"
)

load_dotenv()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Models
# ----------------------------
class ComparisonRequest(BaseModel):
    source1_content: str
    source2_content: str
    user_id: Optional[str] = None

class ComparisonResult(BaseModel):
    comparison_id: str
    similarity_score: float
    common_keywords: List[str]
    unique_to_source1: List[str]
    unique_to_source2: List[str]
    summary: str
    created_at: str

# In-memory storage (can be replaced with DB)
comparisons = {}

# ----------------------------
# Helper Functions
# ----------------------------

def is_url(text: str) -> bool:
    """Check if the given text is a URL."""
    return text.startswith("http://") or text.startswith("https://")


async def extract_text_from_url(url: str) -> str:
    """Extracts text from a YouTube link or webpage."""
    try:
        # Handle YouTube URLs
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = None
            if 'youtube.com/watch' in url:
                parsed_url = urlparse(url)
                video_id = parse_qs(parsed_url.query).get('v', [''])[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[-1].split('?')[0]

            if not video_id:
                raise ValueError("Could not extract video ID from YouTube URL")

            youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY")
            )
            request = youtube.videos().list(part="snippet", id=video_id)
            response = request.execute()

            if not response.get('items'):
                raise ValueError("Video not found or access denied")

            video_info = response['items'][0]['snippet']
            return f"{video_info['title']} {video_info['description']}"

        # Handle regular web pages
        async with httpx.AsyncClient() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unnecessary tags
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text(separator=' ', strip=True)
            return text

    except Exception as e:
        error_detail = str(e)
        if 'No transcripts were found' in error_detail:
            error_detail = "No English captions available for this YouTube video."
        elif 'Video unavailable' in error_detail:
            error_detail = "The YouTube video is unavailable or private."
        raise HTTPException(status_code=400, detail=f"Error extracting content: {error_detail}")


def compare_texts(text1: str, text2: str) -> Dict[str, Any]:
    """Compare two texts using a simple keyword-based similarity."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    common = list(words1.intersection(words2))
    unique1 = list(words1 - words2)
    unique2 = list(words2 - words1)

    similarity = len(common) / (len(words1.union(words2)) or 1)

    return {
        "similarity_score": similarity,
        "common_keywords": common[:20],
        "unique_to_source1": unique1[:20],
        "unique_to_source2": unique2[:20],
    }

# ---------- NEW SMART SUMMARY HELPERS ----------

def clean_and_tokenize(text: str) -> list:
    """Clean text and return a list of words."""
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return [word for word in text.split() if len(word) > 3]

def extract_top_keywords(text: str, n: int = 5) -> List[str]:
    """Extract top frequent keywords."""
    words = clean_and_tokenize(text)
    common = [w for w, _ in Counter(words).most_common(n)]
    return common

def summarize_text(text: str) -> str:
    """Create a short topic summary based on keywords."""
    keywords = extract_top_keywords(text)
    if not keywords:
        return "general information"
    return ", ".join(keywords)

def generate_summary(text1: str, text2: str, comparison_result: dict) -> str:
    """Generate a human-like summary describing both sources."""
    topic1 = summarize_text(text1)
    topic2 = summarize_text(text2)

    similarity = comparison_result["similarity_score"]
    common_words = comparison_result["common_keywords"][:10]

    if similarity > 0.7:
        relation = "Both sources discuss very similar topics with overlapping details."
    elif similarity > 0.4:
        relation = "The sources cover related topics but have different focuses."
    else:
        relation = "The sources appear to discuss different subjects with minimal overlap."

    summary = (
        f"Source 1 mainly discusses topics such as {topic1}. "
        f"Source 2 focuses on {topic2}. "
        f"{relation} They share common keywords like: {', '.join(common_words)}. "
        f"The calculated similarity score is {similarity:.2f}."
    )
    return summary

# ----------------------------
# API Endpoints
# ----------------------------

@app.post("/api/compare", response_model=ComparisonResult)
async def compare_documents(comparison: ComparisonRequest):
    """Compare two sources — can be plain text or URLs."""
    try:
        # Automatically detect URLs vs. text
        if is_url(comparison.source1_content):
            text1 = await extract_text_from_url(comparison.source1_content)
        else:
            text1 = comparison.source1_content

        if is_url(comparison.source2_content):
            text2 = await extract_text_from_url(comparison.source2_content)
        else:
            text2 = comparison.source2_content

        # Compare
        comparison_result = compare_texts(text1, text2)

        # Smart natural summary
        summary = generate_summary(text1, text2, comparison_result)

        # Store the result
        comparison_id = f"comp_{len(comparisons) + 1}"
        result = {
            "comparison_id": comparison_id,
            **comparison_result,
            "summary": summary,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": comparison.user_id  # Store user_id for history filtering
        }

        comparisons[comparison_id] = result
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compare/{comparison_id}", response_model=ComparisonResult)
async def get_comparison(comparison_id: str):
    """Fetch a past comparison by ID."""
    if comparison_id not in comparisons:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comparisons[comparison_id]


@app.get("/api/history")
async def get_comparison_history(user_id: str = None, page: int = 1, page_size: int = 10):
    """Get comparison history for a user with pagination."""
    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # Filter comparisons by user_id (simulated - in real app this would be database query)
    user_comparisons = [
        comp for comp_id, comp in comparisons.items() 
        if comp.get("user_id") == user_id
    ]
    
    # Sort by most recent (using ID as proxy for timestamp)
    user_comparisons.sort(key=lambda x: x.get("id", ""), reverse=True)
    
    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_comparisons = user_comparisons[start:end]
    
    return {
        "results": paginated_comparisons,
        "count": len(user_comparisons),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(user_comparisons) + page_size - 1) // page_size,
        "has_next": end < len(user_comparisons),
        "has_previous": page > 1
    }

@app.delete("/api/history/{comparison_id}")
async def delete_comparison_from_history(comparison_id: str, user_id: str = None):
    """Delete a comparison from user's history."""
    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    if comparison_id not in comparisons:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    comparison = comparisons[comparison_id]
    if comparison.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Comparison not found in your history")
    
    # Delete the comparison
    del comparisons[comparison_id]
    
    return {"message": "Comparison deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "comparison-service"}


# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
