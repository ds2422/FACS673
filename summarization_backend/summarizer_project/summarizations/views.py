from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Summary
from .serializers import SummarySerializer, SummaryCreateSerializer, SummaryUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SummaryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        summaries = Summary.objects.filter(user=request.user)
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SummaryCreateSerializer(data=request.data)
        if serializer.is_valid():
            summary = serializer.save(user=request.user)
            return Response(SummarySerializer(summary).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SummaryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        return get_object_or_404(Summary, pk=pk, user=user)
    
    def get(self, request, pk):
        summary = self.get_object(pk, request.user)
        serializer = SummarySerializer(summary)
        return Response(serializer.data)
    
    def put(self, request, pk):
        summary = self.get_object(pk, request.user)
        serializer = SummaryUpdateSerializer(summary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        summary = self.get_object(pk, request.user)
        summary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PublicSummaryListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        public_summaries = Summary.objects.filter(is_public=True)
        serializer = SummarySerializer(public_summaries, many=True)
        return Response(serializer.data)

class FileUploadView(APIView):
    """API endpoint for uploading files and generating summaries."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        # Validate file upload
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        
        try:
            # Extract text from the uploaded file
            extracted_text = extract_text_from_file(uploaded_file)
            
            if not extracted_text.strip():
                return Response(
                    {'error': 'No text could be extracted from the file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate summary
            summary_text = summarize_large_text(extracted_text)
            
            # Create a new summary record
            summary = Summary.objects.create(
                user=request.user,
                title=uploaded_file.name,
                original_text=extracted_text[:1000] + ('...' if len(extracted_text) > 1000 else ''),
                summary_text=summary_text,
                is_public=serializer.validated_data.get('is_public', False)
            )
            
            return Response({
                'status': 'success',
                'message': 'File processed successfully',
                'summary_id': summary.id,
                'original_length': len(extracted_text.split()),
                'summary_length': len(summary_text.split()),
                'summary': summary_text
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
