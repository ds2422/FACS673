from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('compare/', views.compare_documents_view, name='compare_documents'),
    path('comparison/<int:comparison_id>/', views.get_comparison, name='get_comparison'),
]
