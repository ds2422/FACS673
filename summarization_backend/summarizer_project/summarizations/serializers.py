from rest_framework import serializers
from .models import Summary
import os

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['id', 'title', 'original_text', 'summary_text', 'created_at', 'is_public']
        read_only_fields = ['id', 'created_at']

class SummaryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['title', 'original_text', 'is_public']

class SummaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['title', 'summary_text', 'is_public']
        extra_kwargs = {
            'title': {'required': False},
            'summary_text': {'required': False},
            'is_public': {'required': False},
        }


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload endpoint."""
    file = serializers.FileField(required=True)
    is_public = serializers.BooleanField(default=False, required=False)
    
    def validate_file(self, value):
        """
        Check that the file is a valid document type.
        """
        valid_extensions = ['.pdf', '.docx', '.doc', '.txt']
        ext = os.path.splitext(value.name)[1].lower()
        
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                'Unsupported file type. Supported types are: .pdf, .docx, .doc, .txt'
            )
            
        # Limit file size to 10MB
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File size should not exceed 10MB. Current size: {value.size/1024/1024:.2f}MB'
            )
            
        return value
