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
    ai_summary_text = models.TextField(blank=True, null=True) # AI generated insights
    user_upload_index = models.PositiveIntegerField(blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.user_upload_index:
            # simple auto-increment logic scoped to the user
            max_index = UploadedFile.objects.filter(user=self.user).aggregate(models.Max('user_upload_index'))['user_upload_index__max']
            self.user_upload_index = (max_index or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Upload {self.user_upload_index} by {self.user.username} - {self.uploaded_at}"

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


class UserThresholdSettings(models.Model):
    """
    Per-user threshold settings for health status classification.
    If a user doesn't have custom settings, falls back to .env or hardcoded defaults.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='threshold_settings')
    warning_percentile = models.FloatField(
        default=0.75,
        help_text="Percentile for warning status (0.5-0.95). Equipment above this = Warning."
    )
    outlier_iqr_multiplier = models.FloatField(
        default=1.5,
        help_text="IQR multiplier for outliers (0.5-3.0). Q3 + multiplier*IQR = Critical."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Threshold Settings"
        verbose_name_plural = "User Threshold Settings"

    def __str__(self):
        return f"Thresholds for {self.user.username}: warning={self.warning_percentile}, outlier={self.outlier_iqr_multiplier}"

    def clean(self):
        """Validate threshold ranges."""
        from django.core.exceptions import ValidationError
        if not (0.5 <= self.warning_percentile <= 0.95):
            raise ValidationError({'warning_percentile': 'Must be between 0.5 and 0.95'})
        if not (0.5 <= self.outlier_iqr_multiplier <= 3.0):
            raise ValidationError({'outlier_iqr_multiplier': 'Must be between 0.5 and 3.0'})
