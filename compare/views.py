from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def index(request):
    if request.method == 'POST':
        data = request.POST.get('data', None)
        return JsonResponse({"message": "POST request received", "data": data})
    elif request.method == 'GET':
        return JsonResponse({"message": "Compare app is working!"})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
