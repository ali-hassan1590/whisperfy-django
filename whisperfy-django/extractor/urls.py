from django.urls import path
from .views import ExtractAudioView, HealthCheckView

urlpatterns = [
    path("health/",  HealthCheckView.as_view(),  name="extractor-health"),
    path("extract/", ExtractAudioView.as_view(), name="extract-audio"),
]