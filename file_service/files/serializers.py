import os
from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    """Serializer for the UploadedFile model."""
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedFile
        fields = [
            'id',
            'file',
            'file_url',
            'file_name',
            'file_extension',
            'original_filename',
            'file_size',
            'file_type',
            'uploaded_at',
            'updated_at',
            'is_public',
            'description'
        ]
        read_only_fields = [
            'id', 'file_url', 'file_name', 'file_extension', 
            'original_filename', 'file_size', 'file_type',
            'uploaded_at', 'updated_at'
        ]
    
    def get_file_url(self, obj):
        """Get the absolute URL of the file."""
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_name(self, obj):
        """Get just the filename without path."""
        if obj.file:
            return os.path.basename(obj.file.name)
        return None
    
    def get_file_extension(self, obj):
        """Get the file extension."""
        if obj.file:
            return os.path.splitext(obj.file.name)[1][1:].lower()
        return None

class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload."""
    file = serializers.FileField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """Validate the uploaded file."""
        # Get file size in bytes
        file_size = value.size
        max_size = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size:
            raise serializers.ValidationError("File size should not exceed 50MB.")
            
        # Validate file type
        allowed_types = [
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
        ]
        
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError("File type not supported.")
            
        return value
