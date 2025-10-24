import os
from django.db import models
from django.conf import settings
from django.utils import timezone


def upload_to(instance, filename):
    """Return the upload path for the file.
    
    Format: files/year/month/day/filename
    """
    now = timezone.now()
    return os.path.join(
        'files',
        str(now.year),
        f"{now.month:02d}",
        f"{now.day:02d}",
        filename
    )

class UploadedFile(models.Model):
    """Model to store information about uploaded files."""
    file = models.FileField(upload_to=upload_to)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_public = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        """Meta class for UploadedFile model."""
        ordering = ['-uploaded_at']
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'

    def __str__(self):
        """Return string representation of the model."""
        return self.original_filename

    def delete(self, *args, **kwargs):
        """Delete the file from the filesystem when the model instance is deleted."""
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Set the original filename and file size before saving."""
        if not self.pk:  # Only on create
            self.original_filename = os.path.basename(self.file.name)
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)
