import requests
from bs4 import BeautifulSoup
import re
# We use pytubefix now, which avoids your previous file conflict
from pytubefix import YouTube 
from pytubefix.cli import on_progress

def extract_text_from_youtube(url):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        
        # 1. Try to get official English captions
        caption = yt.captions.get_by_language_code('en')
        
        # 2. If not found, try auto-generated English captions ('a.en')
        if not caption:
            caption = yt.captions.get_by_language_code('a.en')
            
        if not caption:
            return f"Error: No English captions found for this video ({url})."
            
        # 3. Get XML format and strip HTML tags to get pure text
        xml_text = caption.xml_captions
        
        # Regex to remove XML tags like <p>, <br>, etc.
        clean_text = re.sub(r'<[^>]+>', ' ', xml_text)
        
        # Regex to clean up HTML entities (like &amp;) and extra spaces
        clean_text = re.sub(r'&[^;]+;', '', clean_text)
        clean_text = " ".join(clean_text.split())
        
        return f"YouTube Transcript ({url}):\n{clean_text[:15000]}" # Limit length
        
    except Exception as e:
        return f"Error extracting YouTube ({url}): {str(e)}"

def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Failed to load page {url} (Status: {response.status_code})"

        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        text = re.sub(r'\s+', ' ', text).strip()
        
        return f"Web Page Content ({url}):\n{text[:10000]}"
    except Exception as e:
        return f"Error extracting URL ({url}): {str(e)}"

def process_inputs(inputs):
    final_content = []
    
    for item in inputs:
        val = item.get('value', '').strip()
        if not val:
            continue
            
        inputType = item.get('type')
        
        if inputType == 'youtube':
            final_content.append(extract_text_from_youtube(val))
        elif inputType == 'url':
            final_content.append(extract_text_from_url(val))
        else:
            final_content.append(f"User Text Input:\n{val}")
            
    return "\n\n".join(final_content)