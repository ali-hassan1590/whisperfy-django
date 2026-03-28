from django.urls import path
from .views import HealthCheckView, TranscribeVideoView

urlpatterns = [
    path("health/",     HealthCheckView.as_view(),     name="transcription-health"),
    path("transcribe/", TranscribeVideoView.as_view(), name="transcribe-video"),
]