from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Summary
from .serializers import SummarySerializer, SummaryCreateSerializer, SummaryUpdateSerializer
from summarizer_project.utils.jwt_verify import verify_jwt_token
from summarizer_project.utils.text_summarizer import summarize_large_text
  # ✅ your summarizer function
# from summarizations.utils.file_utils import extract_text_from_file  # Uncomment if used


def get_user_from_token(request):
    """Extract and verify JWT token manually."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, Response({"detail": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    if not payload:
        return None, Response({"detail": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Return decoded payload with user info
    return payload, None


class SummaryListView(APIView):
    """GET: list summaries for authenticated user, POST: create summary"""
    permission_classes = [permissions.AllowAny]  # We handle JWT manually

    def get(self, request):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")
        summaries = Summary.objects.filter(user_id=user_id)
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")
        serializer = SummaryCreateSerializer(data=request.data)
        if serializer.is_valid():
            original_text = serializer.validated_data.get('original_text', '')

            # ✅ Generate summary text
            summary_text = summarize_large_text(original_text)

            # ✅ Save summary linked by user_id (microservice pattern)
            summary = serializer.save(
                user_id=user_id,
                summary_text=summary_text
            )

            return Response(SummarySerializer(summary).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SummaryDetailView(APIView):
    """GET, PUT, DELETE summary by ID"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")
        summary = get_object_or_404(Summary, pk=pk, user_id=user_id)
        serializer = SummarySerializer(summary)
        return Response(serializer.data)

    def put(self, request, pk):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")
        summary = get_object_or_404(Summary, pk=pk, user_id=user_id)
        serializer = SummaryUpdateSerializer(summary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")
        summary = get_object_or_404(Summary, pk=pk, user_id=user_id)
        summary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicSummaryListView(APIView):
    """List all public summaries (no authentication needed)."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        public_summaries = Summary.objects.filter(is_public=True)
        serializer = SummarySerializer(public_summaries, many=True)
        return Response(serializer.data)


class FileUploadView(APIView):
    """Upload files, extract text, and generate summaries."""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        payload, error = get_user_from_token(request)
        if error:
            return error

        user_id = payload.get("user_id")

        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        try:
            # ✅ Extract text (assuming you’ve defined extract_text_from_file)
            extracted_text = extract_text_from_file(uploaded_file)
            if not extracted_text.strip():
                return Response(
                    {'error': 'No text could be extracted from the file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Generate summary text
            summary_text = summarize_large_text(extracted_text)

            # ✅ Save record
            summary = Summary.objects.create(
                user_id=user_id,
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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
