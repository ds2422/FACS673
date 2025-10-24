from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .models import DocumentComparison

@api_view(['POST'])
def compare_documents_view(request):
    """
    API endpoint to compare two documents
    Expected JSON payload:
    {
        "source1_type": "url|text|file",
        "source1_content": "content or URL",
        "source2_type": "url|text|file",
        "source2_content": "content or URL",
        "user_id": "optional_user_id"
    }
    """
    try:
        data = request.data
        
        # Create a new comparison record
        comparison = DocumentComparison.objects.create(
            user_id=data.get('user_id'),
            source1_type=data['source1_type'],
            source1_content=data['source1_content'],
            source2_type=data['source2_type'],
            source2_content=data['source2_content'],
            # These would be populated by your comparison logic
            summary="Summary will be generated here",
            similarities="Similarities will be listed here",
            differences="Differences will be listed here"
        )
        
        # TODO: Add your document comparison logic here
        # For now, we'll just return the ID of the created comparison
        
        return Response({
            'comparison_id': comparison.id,
            'status': 'pending',
            'message': 'Comparison started. Check back later for results.'
        }, status=status.HTTP_202_ACCEPTED)
        
    except KeyError as e:
        return Response(
            {'error': f'Missing required field: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_comparison(request, comparison_id):
    """Retrieve the results of a comparison"""
    try:
        comparison = get_object_or_404(DocumentComparison, id=comparison_id)
        
        return Response({
            'id': comparison.id,
            'status': 'completed',  # or 'pending', 'failed' based on your logic
            'summary': comparison.summary,
            'similarities': comparison.similarities,
            'differences': comparison.differences,
            'created_at': comparison.created_at,
            'updated_at': comparison.updated_at
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
