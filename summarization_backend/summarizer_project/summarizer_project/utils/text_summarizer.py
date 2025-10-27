def summarize_large_text(text: str) -> str:
    """Simple rule-based text summarizer for local use."""
    if not text or len(text.split()) < 20:
        return text.strip()
    sentences = text.split('.')
    summary = '. '.join(sentences[:2] + sentences[-2:])[:400] + '...'
    return summary
