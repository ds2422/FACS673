import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import re

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

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
        raise Exception(f"Error extracting text from URL: {str(e)}")

def preprocess_text(text):
    """Preprocess text by tokenizing, removing stopwords, and lemmatizing."""
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return tokens

def compare_documents(doc1, doc2):
    """Compare two documents and return similarities and differences."""
    # Tokenize and preprocess documents
    tokens1 = preprocess_text(doc1)
    tokens2 = preprocess_text(doc2)
    
    # Calculate word frequencies
    freq1 = defaultdict(int)
    for word in tokens1:
        freq1[word] += 1
        
    freq2 = defaultdict(int)
    for word in tokens2:
        freq2[word] += 1
    
    # Find common words and differences
    common_words = set(freq1.keys()) & set(freq2.keys())
    unique_to_doc1 = set(freq1.keys()) - set(freq2.keys())
    unique_to_doc2 = set(freq2.keys()) - set(freq1.keys())
    
    # Calculate similarity score (Jaccard similarity)
    similarity = len(common_words) / len(set(freq1.keys()) | set(freq2.keys())) if (set(freq1.keys()) | set(freq2.keys())) else 0
    
    return {
        'similarity_score': similarity,
        'common_keywords': list(common_words)[:20],  # Return top 20 common keywords
        'unique_to_doc1': list(unique_to_doc1)[:20],  # Top 20 unique to doc1
        'unique_to_doc2': list(unique_to_doc2)[:20],  # Top 20 unique to doc2
    }

def clean_keyword(keyword):
    """Clean and format a single keyword."""
    # Remove numbers and special characters, but keep meaningful ones
    cleaned = ''.join(c if c.isalnum() or c in '-_ ' else ' ' for c in str(keyword))
    # Remove extra spaces and title case
    return ' '.join(cleaned.split()).title()

def categorize_keywords(keywords):
    """Categorize keywords into meaningful groups."""
    categories = {
        'technical': [],
        'concepts': [],
        'methods': [],
        'other': []
    }
    
    # Simple categorization logic - can be enhanced with more sophisticated NLP
    tech_terms = {'api', 'framework', 'algorithm', 'model', 'system', 'data', 'analysis'}
    method_terms = {'method', 'approach', 'technique', 'process', 'strategy'}
    
    for kw in keywords:
        kw_lower = str(kw).lower()
        if any(term in kw_lower for term in tech_terms):
            categories['technical'].append(clean_keyword(kw))
        elif any(term in kw_lower for term in method_terms):
            categories['methods'].append(clean_keyword(kw))
        elif len(str(kw).split()) > 1:  # Multi-word terms often represent concepts
            categories['concepts'].append(clean_keyword(kw))
        else:
            categories['other'].append(clean_keyword(kw))
    
    return categories

def generate_comparison_summary(comparison_result, source1_type, source2_type):
    """
    Generate a well-structured, meaningful summary of the document comparison.
    """
    similarity = comparison_result['similarity_score'] * 100
    
    # Categorize keywords
    common_cats = categorize_keywords(comparison_result['common_keywords'])
    doc1_cats = categorize_keywords(comparison_result['unique_to_doc1'])
    doc2_cats = categorize_keywords(comparison_result['unique_to_doc2'])
    
    # Get document names for display
    doc1_name = "Document 1" if source1_type.lower() == "text" else "URL 1"
    doc2_name = "Document 2" if source2_type.lower() == "text" else "URL 2"
    
    # Build the summary
    summary_parts = [
        "# 📝 Document Comparison Summary\n",
        "## 📊 Similarity Analysis",
        f"- **Similarity Score**: {similarity:.1f}% ({"High" if similarity > 70 else "Moderate" if similarity > 40 else "Low"} Similarity)",
        f"- **Relationship**: {"Documents are closely related" if similarity > 70 else "Documents share some common themes" if similarity > 40 else "Documents have limited overlap in content"}",
        "---\n"
    ]
    
    # Add common themes section
    summary_parts.append("## 🔍 Key Similarities")
    has_common = False
    if common_cats['technical']:
        summary_parts.append("- **Common Technical Terms**: " + ", ".join(common_cats['technical'][:5]))
        has_common = True
    if common_cats['concepts']:
        summary_parts.append("- **Shared Concepts**: " + ", ".join(common_cats['concepts'][:5]))
        has_common = True
    if common_cats['methods']:
        summary_parts.append("- **Common Methods**: " + ", ".join(common_cats['methods'][:5]))
        has_common = True
    if not has_common:
        summary_parts.append("- No significant similarities found in key categories.")
    
    # Function to get top terms from categories with more context
    def get_top_terms(categories, max_terms=5):
        terms = []
        # Get more terms from each category
        for cat in ['technical', 'concepts', 'methods', 'other']:
            terms.extend(categories[cat][:max_terms])
        return terms[:max_terms]
    
    # Function to generate detailed document insights
    def get_document_insights(categories, unique_terms):
        insights = []
        
        # Add technical focus if available
        if categories['technical']:
            insights.append(f"**Technical Focus**: {', '.join(categories['technical'][:3])}")
        
        # Add key concepts if available
        if categories['concepts']:
            insights.append(f"**Key Concepts**: {', '.join(categories['concepts'][:3])}")
        
        # Add methodologies if available
        if categories['methods']:
            insights.append(f"**Methodologies**: {', '.join(categories['methods'][:2])}")
        
        # Fallback to unique terms if no categories found
        if not insights and unique_terms:
            unique_display = [clean_keyword(t) for t in unique_terms[:5] if t and len(str(t).strip()) > 2]
            if unique_display:
                insights.append("**Key Terms**: " + ", ".join(unique_display))
        
        return insights or ["*No specific focus areas identified*"]
    
    # Document sections with detailed insights
    doc_sections = [
        ("📄", doc1_name, doc1_cats, comparison_result['unique_to_doc1']),
        ("📑", doc2_name, doc2_cats, comparison_result['unique_to_doc2'])
    ]
    
    # Add detailed document sections
    for emoji, doc_name, categories, unique_terms in doc_sections:
        summary_parts.append(f"\n## {emoji} {doc_name}: Detailed Analysis")
        
        # Get and add detailed insights
        insights = get_document_insights(categories, unique_terms)
        for insight in insights:
            summary_parts.append(f"- {insight}")
        
        # Add additional context if available
        top_terms = get_top_terms(categories)
        if top_terms and len(top_terms) > 3:  # Only add if we have enough terms
            summary_parts.append(f"\n**Additional Key Terms**: {', '.join(top_terms[3:])}")
    
    # Enhanced summary of differences with context
    doc1_terms = get_top_terms(doc1_cats) or [clean_keyword(t) for t in comparison_result['unique_to_doc1'][:3] if t and len(str(t).strip()) > 2]
    doc2_terms = get_top_terms(doc2_cats) or [clean_keyword(t) for t in comparison_result['unique_to_doc2'][:3] if t and len(str(t).strip()) > 2]
    
    # Add comprehensive summary section
    summary_parts.extend([
        "\n## 📌 Comprehensive Comparison",
        f"### {doc1_name} Key Characteristics:",
        f"- Primary Focus: {', '.join(doc1_terms[:5]) if doc1_terms else 'Various topics'}",
        f"- Technical Aspects: {', '.join(doc1_cats['technical'][:3]) if doc1_cats['technical'] else 'Not specified'}",
        f"- Main Concepts: {', '.join(doc1_cats['concepts'][:3]) if doc1_cats['concepts'] else 'General discussion'}",
        f"\n### {doc2_name} Key Characteristics:",
        f"- Primary Focus: {', '.join(doc2_terms[:5]) if doc2_terms else 'Various topics'}",
        f"- Technical Aspects: {', '.join(doc2_cats['technical'][:3]) if doc2_cats['technical'] else 'Not specified'}",
        f"- Main Concepts: {', '.join(doc2_cats['concepts'][:3]) if doc2_cats['concepts'] else 'General discussion'}",
        "\n### Overall Analysis:",
        f"- **Similarity Level**: {'High' if similarity > 70 else 'Moderate' if similarity > 40 else 'Low'}",
        f"- **Key Differences**: {doc1_name} appears to focus more on {', '.join(doc1_terms[:2]) if doc1_terms else 'its specific topics'}, "
        f"while {doc2_name} emphasizes {', '.join(doc2_terms[:2]) if doc2_terms else 'different aspects'}",
        "\n*Note: This analysis is based on automated text processing and keyword extraction. "
        "The actual content relationship might be more nuanced than what's captured here.*"
    ])
    
    return "\n".join(str(part) for part in summary_parts)
