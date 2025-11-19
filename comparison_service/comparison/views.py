from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .models import DocumentComparison
from django.core.paginator import Paginator
from django.db.models import Q

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

@api_view(['GET'])
def comparison_history(request):
    """
    Get the current user's comparison history with pagination.
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    """
    try:
        # Get user_id from query params (from JWT token in real implementation)
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 10)), 100)
        
        # Filter comparisons by user and order by most recent
        comparisons = DocumentComparison.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = Paginator(comparisons, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize the data
        comparison_data = []
        for comparison in page_obj:
            comparison_data.append({
                'id': comparison.id,
                'source1_type': comparison.source1_type,
                'source2_type': comparison.source2_type,
                'summary': comparison.summary,
                'created_at': comparison.created_at.isoformat(),
                'updated_at': comparison.updated_at.isoformat() if hasattr(comparison, 'updated_at') else None
            })
        
        return Response({
            'results': comparison_data,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_comparison_from_history(request, comparison_id):
    """
    Delete a specific comparison from user's history.
    """
    try:
        # Get user_id from query params (from JWT token in real implementation)
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the comparison belonging to this user
        comparison = DocumentComparison.objects.filter(
            id=comparison_id,
            user_id=user_id
        ).first()
        
        if not comparison:
            return Response(
                {'error': 'Comparison not found in your history'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        comparison.delete()
        
        return Response({
            'message': 'Comparison deleted successfully'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
