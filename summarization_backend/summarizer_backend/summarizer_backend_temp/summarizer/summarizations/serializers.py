from rest_framework import serializers
from .models import Summary

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['id', 'title', 'original_text', 'summary_text', 'created_at', 'updated_at', 'is_public']
        read_only_fields = ['id', 'created_at', 'updated_at']

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
