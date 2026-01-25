from django.db import models
from django.contrib.auth.models import User
import os
from django.dispatch import receiver
from django.db.models.signals import post_delete

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.JSONField(default=dict)  # Stores calculated stats
    processed_data = models.JSONField(default=list)  # Stores the parsed CSV rows

    def __str__(self):
        return f"Upload {self.id} by {self.user.username} - {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']

@receiver(post_delete, sender=UploadedFile)
def submission_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `UploadedFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
