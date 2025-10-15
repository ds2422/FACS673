from django.db import models
from django.utils import timezone
from django.conf import settings

class UploadedContent(models.Model):
    """Model to store uploaded URLs and their summaries."""
    CONTENT_TYPES = [
        ('youtube', 'YouTube Video'),
        ('article', 'Web Article'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    url = models.URLField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=500)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Uploaded Content'
        verbose_name_plural = 'Uploaded Contents'
    
    def __str__(self):
        return f"{self.content_type.upper()}: {self.title}"
