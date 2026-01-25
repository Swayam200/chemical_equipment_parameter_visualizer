from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'file', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['user__username', 'file']
    readonly_fields = ['uploaded_at', 'summary', 'processed_data']
    ordering = ['-uploaded_at']
