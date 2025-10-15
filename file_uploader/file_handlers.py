import io
import logging
import nltk
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image, ImageFilter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

# -------------------------------
# 🧠 NLTK Setup
# -------------------------------
def download_nltk_data():
    for resource in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

download_nltk_data()

# -------------------------------
# 📄 File Extraction Functions
# -------------------------------

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file (fallback to OCR for scanned PDFs)."""
    try:
        with default_storage.open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text() or ""
                text += extracted
            if text.strip():
                return text.strip()

        # Fallback OCR (for scanned PDFs)
        try:
            from pdf2image import convert_from_path
            temp_path = default_storage.path(file_path)
            images = convert_from_path(temp_path)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            return ocr_text.strip()
        except Exception as e:
            logger.warning(f"OCR fallback failed for PDF: {str(e)}")
            return text.strip()

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        with default_storage.open(file_path, 'rb') as file:
            doc = Document(io.BytesIO(file.read()))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""


def extract_text_from_image(file_path):
    """Extract text from PNG/JPG image using OCR with preprocessing."""
    try:
        with default_storage.open(file_path, 'rb') as file:
            img_bytes = file.read()

        # Load image safely from memory
        image = Image.open(io.BytesIO(img_bytes))
        image = image.convert("RGB")  # ensure compatibility
        image = image.convert("L")    # grayscale

        # Preprocess for clarity
        image = image.point(lambda x: 0 if x < 140 else 255, '1')  # threshold
        w, h = image.size
        if w < 800:
            image = image.resize((w * 2, h * 2))  # upscale small images
        image = image.filter(ImageFilter.SHARPEN)

        # OCR extraction
        text = pytesseract.image_to_string(image, lang="eng").strip()

        if not text:
            logger.warning("OCR returned no text — image may be unclear.")
            return "Could not extract readable text from this image. Try a clearer one."

        return text

    except Exception as e:
        logger.error(f"Error reading image: {str(e)}")
        return f"Error reading image: {str(e)}"


# -------------------------------
# 📤 File Processing Logic
# -------------------------------

def process_uploaded_file(file_obj):
    """Save file temporarily, extract text, and clean up."""
    if not file_obj:
        return False, "No file provided"

    try:
        saved_path = default_storage.save(file_obj.name, file_obj)
        text = ""

        # Detect file type and extract accordingly
        if saved_path.endswith('.txt'):
            with default_storage.open(saved_path, 'rb') as f:
                try:
                    text = f.read().decode('utf-8', errors='ignore').strip()
                except UnicodeDecodeError:
                    text = f.read().decode('latin-1', errors='ignore').strip()
        elif saved_path.endswith('.pdf'):
            text = extract_text_from_pdf(saved_path)
        elif saved_path.endswith(('.doc', '.docx')):
            text = extract_text_from_docx(saved_path)
        elif saved_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = extract_text_from_image(saved_path)
        else:
            default_storage.delete(saved_path)
            return False, "Unsupported file format. Please upload .txt, .pdf, .docx, or image files"

        # Cleanup temp file
        default_storage.delete(saved_path)

        if not text.strip():
            return False, "File is empty or unreadable"

        return True, text

    except Exception as e:
        logger.error(f"Error processing file {file_obj.name}: {str(e)}")
        return False, f"Error processing file: {str(e)}"


# -------------------------------
# 🧾 Summarization Logic
# -------------------------------

def generate_summary(text, num_sentences=5):
    """Generate a simple NLTK-based extractive summary."""
    try:
        sentences = sent_tokenize(text)
        if len(sentences) <= num_sentences:
            return " ".join(sentences)

        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w.isalnum() and w not in stop_words]

        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1

        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for w in word_tokenize(sentence.lower()):
                if w in word_freq:
                    sentence_scores[i] = sentence_scores.get(i, 0) + word_freq[w]

        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        top_sentences = sorted([i[0] for i in top_sentences])

        return " ".join(sentences[i] for i in top_sentences)

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary"


# -------------------------------
# 🚀 Handle File Upload (Main Function)
# -------------------------------

def handle_file_upload(request):
    """Handle uploaded file and return extracted + summarized content."""
    try:
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return {"success": False, "message": "No file uploaded"}

        success, content_or_error = process_uploaded_file(uploaded_file)
        if not success:
            return {"success": False, "message": content_or_error}

        summary = generate_summary(content_or_error)
        return {"success": True, "summary": summary}

    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        return {"success": False, "message": f"Error processing file: {str(e)}"}
