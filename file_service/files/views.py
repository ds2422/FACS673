import os
import logging
import mimetypes
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .authentication import JWTAuthentication
from .models import UploadedFile
from .serializers import UploadedFileSerializer, FileUploadSerializer


logger = logging.getLogger(__name__)


class FileUploadView(APIView):
    """API endpoint for uploading files."""
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle file upload."""
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            file_obj = request.FILES['file']
            
            # Create a new UploadedFile instance
            uploaded_file = UploadedFile(
                file=file_obj,
                uploaded_by=request.user,
                description=serializer.validated_data.get('description', ''),
                is_public=serializer.validated_data.get('is_public', False)
            )
            
            # Save the file
            uploaded_file.save()
            
            # Analyze the file content if it's a supported file type
            analysis = {}
            supported_types = ['txt', 'md', 'csv', 'json', 'py', 'js', 'html', 'css', 'docx', 'pdf']
            if uploaded_file.file_type.lower() in supported_types:
                try:
                    file_type = uploaded_file.file_type.lower()
                    
                    # For .docx files, read in binary mode
                    if file_type == 'docx':
                        try:
                            with uploaded_file.file.open('rb') as f:
                                content = f.read()
                            if content:
                                analysis = self.analyze_text_content(content, uploaded_file.original_filename, file_type='docx')
                        except Exception as e:
                            logger.warning(f"Could not read .docx file: {str(e)}")
                    
                    # For PDF files, extract text
                    elif file_type == 'pdf':
                        try:
                            import PyPDF2
                            from io import BytesIO
                            
                            with uploaded_file.file.open('rb') as f:
                                pdf_reader = PyPDF2.PdfReader(f)
                                text_content = []
                                
                                # Extract text from each page (limit to first 10 pages for performance)
                                for page_num in range(min(10, len(pdf_reader.pages))):
                                    page = pdf_reader.pages[page_num]
                                    text = page.extract_text()
                                    if text:
                                        text_content.append(text)
                                
                                content = '\n'.join(text_content)
                                if content:
                                    analysis = self.analyze_text_content(
                                        content, 
                                        uploaded_file.original_filename, 
                                        file_type='pdf'
                                    )
                        except Exception as e:
                            logger.warning(f"Could not read PDF file: {str(e)}")
                            analysis = {
                                'error': 'Could not extract text from PDF',
                                'details': str(e)
                            }
                    else:
                        # For text files, try different encodings
                        encodings = ['utf-8', 'latin-1', 'cp1252']
                        content = None
                        
                        for encoding in encodings:
                            try:
                                # Read as binary first, then decode
                                with uploaded_file.file.open('rb') as f:
                                    file_content = f.read()
                                content = file_content.decode(encoding)
                                if content:
                                    analysis = self.analyze_text_content(content, uploaded_file.original_filename)
                                    break
                            except (UnicodeDecodeError, Exception) as e:
                                continue
                                
                        if content is None:
                            logger.warning("Could not read file with any supported encoding")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze file content: {str(e)}")
                    analysis = {
                        'error': 'Could not analyze file content',
                        'details': str(e)
                    }
            
            # Get the serialized file data
            file_serializer = UploadedFileSerializer(
                uploaded_file,
                context={'request': request}
            )
            
            # Get the serialized data
            serialized_data = file_serializer.data
            
            # Ensure the description is included
            if not serialized_data.get('description'):
                serialized_data['description'] = uploaded_file.description or ''
            
            # Create the base response data
            response_data = {
                'status': 'success',
                'message': 'File uploaded successfully',
                'data': serialized_data
            }
            
            # Add analysis to the response data if available
            if analysis:
                if 'error' in analysis:
                    response_data['data']['analysis_error'] = analysis
                else:
                    response_data['data']['analysis'] = analysis
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'status': 'error',
                'message': 'File upload failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def analyze_text_content(self, content, filename, file_type=None, encoding='utf-8'):
        """Analyze the content of a file and return a summary."""
        try:
            # For .docx files, we'll get the content as a list of paragraphs
            if file_type and file_type.lower() == 'docx':
                try:
                    import docx
                    from io import BytesIO
                    
                    # Read the .docx file content
                    doc = docx.Document(BytesIO(content))
                    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    
                    if not paragraphs:
                        return {
                            'error': 'Empty document',
                            'details': 'The document appears to be empty'
                        }
                        
                    content = '\n'.join(paragraphs)
                    
                    # Basic analysis for .docx
                    lines = [p for p in paragraphs if p.strip()]  # Non-empty paragraphs as lines
                    word_count = sum(len(p.split()) for p in paragraphs)
                    char_count = sum(len(p) for p in paragraphs)
                    line_count = len(paragraphs)
                    
                    # Get document properties if available
                    doc_properties = {}
                    if hasattr(doc.core_properties, 'title') and doc.core_properties.title:
                        doc_properties['title'] = doc.core_properties.title
                    if hasattr(doc.core_properties, 'author') and doc.core_properties.author:
                        doc_properties['author'] = doc.core_properties.author
                except ImportError:
                    return {
                        'error': 'python-docx library not installed',
                        'details': 'Please install python-docx to analyze .docx files'
                    }
            else:
                # For text-based files
                lines = content.split('\n')
                word_count = len(content.split())
                char_count = len(content)
                line_count = len(lines)
            
            # Set document type based on file extension
            doc_type = "text"
            if not file_type:
                file_type = ''
                
            file_type = file_type.lower()
            
            if file_type == 'docx':
                doc_type = "Word Document"
            elif file_type == 'pdf':
                doc_type = "PDF Document"
            elif any(ext in filename.lower() for ext in ['.py']):
                doc_type = "Python code"
            elif any(ext in filename.lower() for ext in ['.js']):
                doc_type = "JavaScript code"
            elif any(ext in filename.lower() for ext in ['.html']):
                doc_type = "HTML document"
            elif any(ext in filename.lower() for ext in ['.css']):
                doc_type = "CSS stylesheet"
            elif any(ext in filename.lower() for ext in ['.json']):
                doc_type = "JSON data"
            
            # Try to extract a summary for text files
            summary = None
            if doc_type == "text" and line_count > 10:
                # Take first 3 non-empty lines as a simple summary for text files
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                if non_empty_lines:
                    summary = '\n'.join(non_empty_lines[:3])
                    if len(summary) > 200:  # Truncate if too long
                        summary = summary[:197] + '...'
            
            # Get file size in KB
            file_size_kb = len(content.encode('utf-8')) / 1024.0
            
            return {
                'type': doc_type,
                'word_count': word_count,
                'char_count': char_count,
                'line_count': line_count,
                'file_size_kb': round(file_size_kb, 2),
                'summary': summary,
                'content_preview': (content[:500] if content and len(content) > 500 else content) if content else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file content: {str(e)}", exc_info=True)
            return {
                'error': 'Could not analyze file content',
                'details': str(e)
            }


class FileListView(APIView):
    """API endpoint for listing files."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """List all files for the authenticated user."""
        files = UploadedFile.objects.filter(uploaded_by=request.user)
        serializer = UploadedFileSerializer(
            files, 
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'status': 'success',
                'data': serializer.data
            }
        )


class FileDetailView(APIView):
    """API endpoint for retrieving, updating and deleting files."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        """Get the file object or return None."""
        try:
            return UploadedFile.objects.get(pk=pk, uploaded_by=user)
        except UploadedFile.DoesNotExist:
            return None
    
    def get(self, request, pk, *args, **kwargs):
        """Retrieve a file."""
        file_obj = self.get_object(pk, request.user)
        
        if not file_obj:
            return Response(
                {'status': 'error', 'message': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UploadedFileSerializer(file_obj, context={'request': request})
        return Response(
            {
                'status': 'success',
                'data': serializer.data
            }
        )

    
    def delete(self, request, pk, *args, **kwargs):
        """Delete a file."""
        file_obj = self.get_object(pk, request.user)
        
        if not file_obj:
            return Response(
                {'status': 'error', 'message': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        file_obj.delete()
        
        return Response(
            {'status': 'success', 'message': 'File deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

def health(request):
    return JsonResponse({"status": "healthy"})