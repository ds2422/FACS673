from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import os
import PyPDF2
import docx

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    try:
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        file_path = os.path.join('media', file_obj.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        extracted_text = ""
        if file_obj.name.endswith('.pdf'):
            with open(file_path, 'rb') as pdf:
                reader = PyPDF2.PdfReader(pdf)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
        elif file_obj.name.endswith('.docx'):
            doc = docx.Document(file_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs])
        elif file_obj.name.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            return Response({"error": "Unsupported file type"}, status=400)

        return Response({
            "filename": file_obj.name,
            "extracted_text": extracted_text[:500] + "..."  # limit for display
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)
