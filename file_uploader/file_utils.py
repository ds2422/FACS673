import io
import PyPDF2
import logging
from docx import Document
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file in the storage
        
    Returns:
        str: Extracted text from the PDF, or empty string if extraction fails
    """
    try:
        with default_storage.open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.
    
    Args:
        file_path (str): Path to the DOCX file in the storage
        
    Returns:
        str: Extracted text from the DOCX file, or empty string if extraction fails
    """
    try:
        with default_storage.open(file_path, 'rb') as file:
            doc = Document(io.BytesIO(file.read()))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_file(file_path):
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path (str): Path to the file in the storage
        
    Returns:
        tuple: (success: bool, result: str or dict)
               On success: (True, extracted_text)
               On failure: (False, error_message)
    """
    text = ""
    try:
        if not file_path:
            return False, "No file path provided"
            
        if file_path.endswith('.txt'):
            try:
                # First try with binary read and decode
                with default_storage.open(file_path, 'rb') as file:
                    content = file.read()
                    # Try common encodings
                    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']:
                        try:
                            text = content.decode(encoding).strip()
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        return False, "Could not decode text file with common encodings"
            except Exception as e:
                return False, f"Error reading text file: {str(e)}"
                
        elif file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            if not text:
                return False, "Could not extract text from PDF"
                
        elif file_path.endswith(('.doc', '.docx')):
            text = extract_text_from_docx(file_path)
            if not text:
                return False, "Could not extract text from Word document"
        else:
            return False, "Unsupported file format. Please upload .txt, .pdf, or .docx files"
            
        if not text:
            return False, "File is empty"
        return True, text
            
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return False, f"Error processing file: {str(e)}"