import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import DocumentComparison
from .comparison_utils import extract_text_from_url, compare_documents, generate_comparison_summary

def index(request):
    """Simple index view for the compare app."""
    return JsonResponse({
        "status": "success",
        "message": "Document Comparison API is running",
        "endpoints": {
            "compare_documents": {
                "method": "POST",
                "url": "/api/compare/compare/",
                "description": "Compare two documents/URLs",
                "required_fields": {
                    "source1_type": "url|text|file",
                    "source1_content": "URL or text content",
                    "source2_type": "url|text|file",
                    "source2_content": "URL or text content"
                }
            },
            "get_comparison": {
                "method": "GET",
                "url": "/api/compare/comparison/<int:comparison_id>/",
                "description": "Get comparison results by ID"
            }
        }
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
@require_http_methods(["POST"])
def compare_documents_view(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
            
        # Get source types and content
        source1_type = data.get('source1_type')
        source1_content = data.get('source1_content')
        source2_type = data.get('source2_type')
        source2_content = data.get('source2_content')
        
        # Validate input
        if not all([source1_type, source1_content, source2_type, source2_content]):
            return JsonResponse({
                'error': 'Missing required fields. Required: source1_type, source1_content, source2_type, source2_content'
            }, status=400)
            
        # Extract text based on source types
        try:
            # Process first source
            if source1_type == 'url':
                doc1 = extract_text_from_url(source1_content)
            else:  # text or file content
                doc1 = source1_content
                
            # Process second source
            if source2_type == 'url':
                doc2 = extract_text_from_url(source2_content)
            else:  # text or file content
                doc2 = source2_content
                
            # Compare documents
            comparison_result = compare_documents(doc1, doc2)
            
            # Generate summary
            summary = generate_comparison_summary(
                comparison_result,
                source1_type.upper(),
                source2_type.upper()
            )
            
            # Save the comparison (optional)
            comparison = DocumentComparison.objects.create(
                source1_type=source1_type,
                source1_content=source1_content[:1000],  # Store first 1000 chars
                source2_type=source2_type,
                source2_content=source2_content[:1000],  # Store first 1000 chars
                summary=summary,
                similarities=str(comparison_result.get('common_keywords', [])),
                differences=str({
                    f'unique_to_source1': comparison_result.get('unique_to_doc1', []),
                    f'unique_to_source2': comparison_result.get('unique_to_doc2', [])
                })
            )
            
            return JsonResponse({
                'status': 'success',
                'comparison_id': comparison.id,
                'summary': summary,
                'similarity_score': comparison_result['similarity_score'],
                'common_keywords': comparison_result.get('common_keywords', []),
                'unique_to_source1': comparison_result.get('unique_to_doc1', []),
                'unique_to_source2': comparison_result.get('unique_to_doc2', []),
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def get_comparison(request, comparison_id):
    try:
        comparison = DocumentComparison.objects.get(id=comparison_id)
        return JsonResponse({
            'status': 'success',
            'comparison': {
                'id': comparison.id,
                'source1_type': comparison.source1_type,
                'source2_type': comparison.source2_type,
                'summary': comparison.summary,
                'similarities': comparison.similarities,
                'differences': comparison.differences,
                'created_at': comparison.created_at.isoformat(),
            }
        })
    except DocumentComparison.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Comparison not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
