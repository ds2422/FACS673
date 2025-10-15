from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation

# Download necessary NLTK data (silently)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


def extract_text_from_url(url):
    """Fetch and extract readable text from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.extract()

        # Get visible text
        text = ' '.join(soup.stripped_strings)
        return text
    except Exception as e:
        return None


@csrf_exempt
def summarize_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            url = data.get('url', '')

            # If a URL is provided, fetch its content
            if url:
                fetched_text = extract_text_from_url(url)
                if not fetched_text:
                    return JsonResponse({'success': False, 'message': 'Unable to fetch content from the provided URL'}, status=400)
                text = fetched_text

            # If neither text nor URL provided
            if not text.strip():
                return JsonResponse({'success': False, 'message': 'No text or URL provided'}, status=400)

            # Tokenize sentences
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return JsonResponse({'success': False, 'message': 'Text too short to summarize'}, status=400)

            # Tokenize words and calculate word frequencies
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words("english") + list(punctuation))
            word_frequencies = {}
            for word in words:
                if word not in stop_words:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1

            # Normalize frequencies
            max_freq = max(word_frequencies.values())
            for word in word_frequencies:
                word_frequencies[word] /= max_freq

            # Score sentences
            sentence_scores = {}
            for sentence in sentences:
                for word in word_tokenize(sentence.lower()):
                    if word in word_frequencies:
                        sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]

            # Select top 30% sentences
            summary_length = max(1, int(len(sentences) * 0.3))
            sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
            summary = ' '.join(sorted_sentences[:summary_length])

            return JsonResponse({
                'success': True,
                'original_length': len(sentences),
                'summary_length': summary_length,
                'summary': summary
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON input'}, status=400)

    return JsonResponse({'success': False, 'message': 'Only POST method is allowed'}, status=405)
