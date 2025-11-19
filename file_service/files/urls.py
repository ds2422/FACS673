from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File upload endpoint
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    
    # List all files for the authenticated user
    path('', views.FileListView.as_view(), name='file-list'),
    
    # File history endpoint with pagination
    path('history/', views.FileHistoryView.as_view(), name='file-history'),
    
    # File detail, update, delete endpoints
    path('<int:pk>/', views.FileDetailView.as_view(), name='file-detail'),

    # Health check endpoint
    path('health/', views.health, name='health'),
]
