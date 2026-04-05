from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/",                admin.site.urls),
    path("api/v1/extractor/",     include("extractor.urls")),
    path("api/v1/transcription/", include("transcription.urls")),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(),   name="schema"),

    # Swagger UI
    path("api/docs/",
         SpectacularSwaggerView.as_view(url_name="schema"),
         name="swagger-ui"),
    # http://127.0.0.1:8000/api/docs/
    
    
    # ReDoc
    path("api/redoc/",
         SpectacularRedocView.as_view(url_name="schema"),
         name="redoc"),

    # http://127.0.0.1:8000/api/redoc/
]