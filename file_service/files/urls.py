from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File upload endpoint
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    
    # List all files for the authenticated user
    path('', views.FileListView.as_view(), name='file-list'),
    
    # File detail, update, delete endpoints
    path('<int:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    
    # Download file endpoint (optional, can be implemented later)
    # path('<int:pk>/download/', views.FileDownloadView.as_view(), name='file-download'),
]
