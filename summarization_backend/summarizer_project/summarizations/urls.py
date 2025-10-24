from django.urls import path
from . import views

app_name = 'summarizations'

urlpatterns = [
    path('', views.SummaryListView.as_view(), name='summary-list'),
    path('public/', views.PublicSummaryListView.as_view(), name='public-summary-list'),
    path('<int:pk>/', views.SummaryDetailView.as_view(), name='summary-detail'),
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
]
