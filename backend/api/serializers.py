from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'uploaded_at', 'summary', 'processed_data', 'username']
        read_only_fields = ['summary', 'processed_data', 'username']
