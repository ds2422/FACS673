from django.contrib import admin
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """Admin interface for UploadedFile model."""
    list_display = (
        'original_filename',
        'file_type',
        'file_size',
        'uploaded_by',
        'uploaded_at',
        'is_public'
    )
    list_filter = ('file_type', 'is_public', 'uploaded_at')
    search_fields = ('original_filename', 'description')
    readonly_fields = ('file_size', 'uploaded_at', 'updated_at')
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'original_filename', 'file_type', 'file_size')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at')
        }),
        ('Settings', {
            'fields': ('is_public', 'description')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set the uploaded_by field to the current user if it's a new file."""
        if not obj.pk:  # Only on create
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
