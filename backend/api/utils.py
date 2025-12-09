import requests
from bs4 import BeautifulSoup
import re
from pytubefix import YouTube 
from pytubefix.cli import on_progress
# NEW IMPORTS FOR PDF
import base64
import io
from pypdf import PdfReader

def extract_text_from_pdf(base64_content):
    try:
        # 1. Decode the Base64 string back to binary
        # Frontend might send "data:application/pdf;base64,JVBER..."
        if "," in base64_content:
            base64_content = base64_content.split(",")[1]
            
        pdf_bytes = base64.b64decode(base64_content)
        
        # 2. Read the PDF from memory
        reader = PdfReader(io.BytesIO(pdf_bytes))
        
        text = ""
        # 3. Extract text page by page
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return f"PDF Content:\n{text[:15000]}" # Limit to ~15k chars to fit context window
        
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

# ... (Keep extract_text_from_youtube and extract_text_from_url exactly as they were) ...
def extract_text_from_youtube(url):
    # ... your existing code ...
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        caption = yt.captions.get_by_language_code('en')
        if not caption:
            caption = yt.captions.get_by_language_code('a.en')
        if not caption:
            return f"Error: No English captions found for this video ({url})."
        xml_text = caption.xml_captions
        clean_text = re.sub(r'<[^>]+>', ' ', xml_text)
        clean_text = re.sub(r'&[^;]+;', '', clean_text)
        clean_text = " ".join(clean_text.split())
        return f"YouTube Transcript ({url}):\n{clean_text[:15000]}"
    except Exception as e:
        return f"Error extracting YouTube ({url}): {str(e)}"

def extract_text_from_url(url):
    # ... your existing code ...
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
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
        elif inputType == 'pdf':  # <--- NEW CHECK
            final_content.append(extract_text_from_pdf(val))
        else:
            final_content.append(f"User Text Input:\n{val}")
            
    return "\n\n".join(final_content)