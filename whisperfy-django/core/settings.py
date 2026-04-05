from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url # Added: helps parse the DATABASE_URL from Render

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG = os.getenv("DEBUG", "False") == "True"

# Updated: Added Render's automatic environment variable for the domain
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "extractor",
    "transcription",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← add this
    "whitenoise.middleware.WhiteNoiseMiddleware", # Static file handler
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Updated: Uses DATABASE_URL for Render/Neon, defaults to local SQLite for your PC
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files — WhiteNoise serves Swagger CSS/JS
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Updated: Modern way to handle storage for WhiteNoise 6.0+
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Allow anyone to call the API (open for portfolio)
CORS_ALLOW_ALL_ORIGINS = True

# Whisperfy settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 500))
TEMP_DIR = os.path.join(BASE_DIR, os.getenv("TEMP_DIR", "temp"))
os.makedirs(TEMP_DIR, exist_ok=True)

# ffmpeg — Ensure this is installed via Render's build script or Dockerfile
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Whisperfy API",
    "DESCRIPTION": """
## Whisperfy — AI Audio Transcription & Extraction API
... (description kept same) ...
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
    },
    "TAGS": [
        {
            "name": "Transcription",
            "description": "Upload any video or audio file — get back full text with timestamps.",
        },
        {
            "name": "Extraction",
            "description": "Upload any video — download the extracted audio track as a .wav file.",
        },
    ],
}