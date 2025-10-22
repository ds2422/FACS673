from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class DocumentComparison(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('url', 'URL'),
        ('text', 'Text'),
        ('file', 'File')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    source1_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES)
    source1_content = models.TextField()
    source2_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES)
    source2_content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    similarities = models.TextField(blank=True, null=True)
    differences = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comparison {self.id} - {self.created_at}"
