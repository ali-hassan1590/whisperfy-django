from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG      = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".railway.app",
    ".up.railway.app",
]

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
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# Static files — WhiteNoise serves Swagger CSS/JS
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Allow anyone to call the API (open for portfolio)
CORS_ALLOW_ALL_ORIGINS = True

# Whisperfy settings
WHISPER_MODEL    = os.getenv("WHISPER_MODEL", "base")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 500))
TEMP_DIR         = os.path.join(BASE_DIR, os.getenv("TEMP_DIR", "temp"))
os.makedirs(TEMP_DIR, exist_ok=True)

# ffmpeg — Railway installs it via nixpacks automatically
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

A production REST API built with **Django** and powered by **OpenAI Whisper**.

### What you can do
- 🎙️ **Transcribe** any video or audio file into full text with timestamps
- 🎵 **Extract** audio from any video as a downloadable `.wav` file
- 🌍 Supports **99+ languages** and **22+ file formats**

### How to test
1. Click any endpoint below
2. Click the **Try it out** button
3. Upload your file using the file picker
4. Click **Execute**
5. See your result instantly — no signup needed

### Supported formats
**Video:** MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG, 3GP, M4V, TS

**Audio:** MP3, WAV, M4A, AAC, OGG, FLAC, WMA, OPUS, AIFF, AMR

### No authentication required — free and open
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking":            True,
        "persistAuthorization":   True,
        "displayOperationId":     False,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth":  1,
        "docExpansion":           "list",
        "filter":                 True,
    },
    "TAGS": [
        {
            "name":        "Transcription",
            "description": "Upload any video or audio file — get back full text with timestamps in 99+ languages.",
        },
        {
            "name":        "Extraction",
            "description": "Upload any video — download the extracted audio track as a .wav file.",
        },
    ],
}