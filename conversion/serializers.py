from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document', 'uploaded_at', 'pdf_file']  # expose fields in API
        read_only_fields = ['uploaded_at', 'pdf_file'] 