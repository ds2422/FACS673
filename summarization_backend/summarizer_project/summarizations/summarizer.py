import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.text_rank import TextRankSummarizer

nltk.download('punkt', quiet=True)

def summarize_text(text, sentences_count=5):
    """
    Generate a short summary of text using TextRank.
    """
    if not text or len(text.split()) < 30:
        return text.strip()  # Skip summarizing very short text

    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer(Stemmer("english"))
        summarizer.stop_words = get_stop_words("english")

        summary_sentences = summarizer(parser.document, sentences_count)
        return ' '.join(str(sentence) for sentence in summary_sentences).strip()
    except Exception as e:
        raise ValueError(f"Error generating summary: {str(e)}")


def summarize_large_text(text, max_chunk_size=1000, sentences_per_chunk=2):
    """
    Summarize very large text efficiently and coherently.
    Splits large text into balanced chunks, summarizes each,
    then re-summarizes combined chunks for the final summary.
    """
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return ""

    # If text is small, summarize directly
    if len(sentences) <= 10:
        return summarize_text(text, min(5, len(sentences)))

    # Create balanced chunks of ~max_chunk_size words each
    chunks, current_chunk, current_length = [], [], 0
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
    for idx, chunk in enumerate(chunks):
        summary = summarize_text(chunk, sentences_per_chunk)
        if summary and summary not in chunk_summaries:  # Avoid duplicate summaries
            chunk_summaries.append(summary)

    # Combine chunk summaries into a single text
    combined_summary = " ".join(chunk_summaries)

    # Final pass: summarize again to refine and compress
    final_summary = summarize_text(combined_summary, sentences_count=5)

    # Optional: clean repetitive sentences (simple dedup)
    unique_lines = []
    for line in final_summary.split('. '):
        if line not in unique_lines:
            unique_lines.append(line)
    cleaned_summary = '. '.join(unique_lines)

    return cleaned_summary.strip()
