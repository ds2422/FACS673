from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import re
import os
import json
from datetime import datetime

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

app = FastAPI(
    title="Document Comparison Service",
    description="Microservice for comparing documents and text content",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ComparisonRequest(BaseModel):
    source1_type: str  # 'text' or 'url' or 'file_id'
    source1_content: str
    source2_type: str  # 'text' or 'url' or 'file_id'
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

def extract_text_from_url(url):
    """Extract text content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse only if content is HTML
        if 'text/html' in response.headers.get('content-type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        else:
            # For non-HTML content, return as is
            return response.text
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from URL: {str(e)}")

def preprocess_text(text):
    """Preprocess text by tokenizing, removing stopwords, and lemmatizing."""
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens

def compare_documents(doc1, doc2):
    """Compare two documents and return similarities and differences."""
    # Preprocess both documents
    tokens1 = preprocess_text(doc1)
    tokens2 = preprocess_text(doc2)
    
    # Calculate term frequencies
    freq1 = defaultdict(int)
    for token in tokens1:
        freq1[token] += 1
        
    freq2 = defaultdict(int)
    for token in tokens2:
        freq2[token] += 1
    
    # Find common and unique terms
    all_terms = set(freq1.keys()).union(set(freq2.keys()))
    common_terms = set(freq1.keys()).intersection(set(freq2.keys()))
    unique_terms1 = set(freq1.keys()) - common_terms
    unique_terms2 = set(freq2.keys()) - common_terms
    
    # Calculate similarity score (Jaccard similarity)
    similarity = len(common_terms) / len(all_terms) if all_terms else 0
    
    return {
        'similarity_score': similarity,
        'common_keywords': sorted(list(common_terms), key=lambda x: freq1.get(x, 0) + freq2.get(x, 0), reverse=True)[:50],
        'unique_to_doc1': sorted(list(unique_terms1), key=lambda x: freq1[x], reverse=True)[:50],
        'unique_to_doc2': sorted(list(unique_terms2), key=lambda x: freq2[x], reverse=True)[:50]
    }

def generate_comparison_summary(comparison_result, source1_type, source2_type):
    """Generate a summary of the comparison results."""
    similarity = comparison_result.get('similarity_score', 0) * 100
    common_count = len(comparison_result.get('common_keywords', []))
    unique1_count = len(comparison_result.get('unique_to_doc1', []))
    unique2_count = len(comparison_result.get('unique_to_doc2', []))
    
    summary = (
        f"## Document Comparison Summary\n\n"
        f"### Similarity Score: {similarity:.1f}%\n\n"
        f"### Key Statistics:\n"
        f"- **Common Terms**: {common_count} shared terms\n"
        f"- **Unique to Source 1**: {unique1_count} terms\n"
        f"- **Unique to Source 2**: {unique2_count} terms\n\n"
        f"### Analysis:\n"
    )
    
    if similarity > 70:
        summary += "The documents are very similar, with significant overlap in content and terminology.\n"
    elif similarity > 40:
        summary += "The documents share some common themes but have distinct content.\n"
    else:
        summary += "The documents are quite different, with limited overlap in content.\n"
    
    if common_count > 0:
        common_terms = ', '.join(comparison_result['common_keywords'][:10])
        summary += f"\n**Common Terms**: {common_terms}...\n"
    
    return summary

# In-memory storage (replace with database in production)
comparisons = {}

# API Endpoints
@app.post("/api/compare", response_model=ComparisonResult)
async def compare_documents_endpoint(comparison: ComparisonRequest):
    try:
        # Extract text from sources
        if comparison.source1_type == 'url':
            text1 = extract_text_from_url(comparison.source1_content)
        else:  # text or file_id
            text1 = comparison.source1_content
            
        if comparison.source2_type == 'url':
            text2 = extract_text_from_url(comparison.source2_content)
        else:  # text or file_id
            text2 = comparison.source2_content
        
        # Compare the documents
        comparison_result = compare_documents(text1, text2)
        
        # Generate summary
        summary = generate_comparison_summary(
            comparison_result,
            comparison.source1_type,
            comparison.source2_type
        )
        
        # Create and store the comparison
        comparison_id = f"comp_{len(comparisons) + 1}"
        result = {
            "comparison_id": comparison_id,
            "similarity_score": comparison_result['similarity_score'],
            "common_keywords": comparison_result['common_keywords'],
            "unique_to_source1": comparison_result['unique_to_doc1'],
            "unique_to_source2": comparison_result['unique_to_doc2'],
            "summary": summary,
            "created_at": datetime.utcnow().isoformat()
        }
        
        comparisons[comparison_id] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compare/{comparison_id}", response_model=ComparisonResult)
async def get_comparison(comparison_id: str):
    if comparison_id not in comparisons:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comparisons[comparison_id]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "comparison-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
