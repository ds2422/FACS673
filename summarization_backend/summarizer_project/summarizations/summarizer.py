import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.text_rank import TextRankSummarizer

def summarize_text(text, sentences_count=5):
    """
    Generate a summary of the given text using LSA (Latent Semantic Analysis).
    
    Args:
        text (str): The text to summarize
        sentences_count (int): Number of sentences in the summary
        
    Returns:
        str: The generated summary
    """
    try:
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        
        # Initialize the parser and tokenizer
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        
        # Initialize the summarizer
        summarizer = TextRankSummarizer(Stemmer("english"))
        summarizer.stop_words = get_stop_words("english")
        
        # Generate summary
        summary_sentences = summarizer(parser.document, sentences_count)
        
        # Join the sentences to form the final summary
        summary = ' '.join(str(sentence) for sentence in summary_sentences)
        
        return summary.strip()
    except Exception as e:
        raise ValueError(f"Error generating summary: {str(e)}")

def summarize_large_text(text, max_chunk_size=1000, sentences_per_chunk=2):
    """
    Summarize large texts by breaking them into chunks.
    
    Args:
        text (str): The text to summarize
        max_chunk_size (int): Maximum size of each chunk
        sentences_per_chunk (int): Number of sentences per chunk summary
        
    Returns:
        str: The generated summary
    """
    # Split text into sentences
    sentences = nltk.sent_tokenize(text)
    
    if not sentences:
        return ""
    
    # If text is small, summarize directly
    if len(sentences) <= 10:
        return summarize_text(text, min(5, len(sentences)))
    
    # Break into chunks and summarize each chunk
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    # Summarize each chunk
    chunk_summaries = []
    for chunk in chunks:
        summary = summarize_text(chunk, sentences_per_chunk)
        chunk_summaries.append(summary)
    
    # Combine chunk summaries and summarize again
    combined_summary = " ".join(chunk_summaries)
    final_summary = summarize_text(combined_summary, sentences_count=5)
    
    return final_summary
