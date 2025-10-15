from django.urls import path
from django.views.generic import RedirectView
from .views import upload_multipart, upload_binary, summarize_text

urlpatterns = [
    path('upload/multipart/', upload_multipart, name='upload_multipart'),
    path('upload/binary/', upload_binary, name='upload_binary'),
    path('upload/', RedirectView.as_view(pattern_name='upload_multipart', permanent=False)),
    path('summarize/', summarize_text, name='summarize_text'),
]