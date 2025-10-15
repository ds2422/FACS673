from django.contrib import admin
from django.urls import path, include
from file_uploader.views import summarize_text

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/summarizer/', include('summarizer.urls')),
    path('api/compare/', include('compare.urls')),
    path('api/file_uploader/', include('file_uploader.urls')),
]
