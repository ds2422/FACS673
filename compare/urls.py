from django.urls import path
from . import views

app_name = 'compare'  # Add this line to set the app namespace

urlpatterns = [
    path('', views.index, name='index'),  # This is the index view
    path('compare/', views.compare_documents_view, name='compare_documents'),
    path('comparison/<int:comparison_id>/', views.get_comparison, name='get_comparison'),
]