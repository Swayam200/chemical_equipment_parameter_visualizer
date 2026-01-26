from django.urls import path
from .views import FileUploadView, HistoryView, PDFReportView, LoginView, RegisterView, ThresholdSettingsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:pk>/', PDFReportView.as_view(), name='pdf-report'),
    path('thresholds/', ThresholdSettingsView.as_view(), name='thresholds'),
]
