import os
import PyPDF2
import docx2txt
from pathlib import Path

def extract_text_from_file(file_path):
    """Extract text from different file formats."""
    file_extension = Path(file_path.name).suffix.lower()
    
    try:
        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return file_path.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise ValueError(f"Error extracting text from file: {str(e)}")

def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file."""
    try:
        # Save the uploaded file temporarily
        temp_path = 'temp_file.docx'
        with open(temp_path, 'wb+') as temp_file:
            for chunk in file_path.chunks():
                temp_file.write(chunk)
        
        # Extract text and clean up
        text = docx2txt.process(temp_path)
        os.remove(temp_path)
        
        return text.strip()
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise ValueError(f"Error reading DOCX file: {str(e)}")
