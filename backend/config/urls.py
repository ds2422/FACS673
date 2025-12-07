from django.contrib import admin
from django.urls import path
from api.views import SummarizeView, HistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/summarize/', SummarizeView.as_view()),
    path('api/history/', HistoryView.as_view()),
]