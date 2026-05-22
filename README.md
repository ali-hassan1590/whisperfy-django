# 🎙️ Whisperfy

A Django REST API for audio and video transcription powered by **OpenAI Whisper**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## Overview

Whisperfy is a backend service that accepts audio or video files and returns accurate transcriptions using OpenAI's Whisper speech recognition model. It exposes a clean REST API built with Django REST Framework, with auto-generated API docs via drf-spectacular.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0.3 |
| API | Django REST Framework 3.17.1 |
| Transcription | OpenAI Whisper |
| Video Processing | MoviePy 2.2.1 |
| ML Runtime | PyTorch 2.11.0 + Numba |
| API Docs | drf-spectacular (OpenAPI 3) |
| Database | PostgreSQL (via psycopg2) / SQLite (dev) |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| CORS | django-cors-headers |

---

## Prerequisites

- Python 3.10+
- pip
- ffmpeg (required by Whisper and MoviePy)
- PostgreSQL (for production) or SQLite (for development)

Install ffmpeg:

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/whisperfy.git
cd whisperfy
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

> ⚠️ PyTorch (`torch==2.11.0`) is a large package. Installation may take several minutes.

4. **Apply database migrations**

```bash
python manage.py migrate
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave empty to use SQLite in dev)
DATABASE_URL=postgres://user:password@localhost:5432/whisperfy

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

> The project uses `python-dotenv` and `dj-database-url` to load these automatically.

---

## Running the Project

**Development server:**

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

**API Documentation (Swagger UI):**

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

**ReDoc:**

```
http://127.0.0.1:8000/api/schema/redoc/
```

---

## API Documentation

Auto-generated OpenAPI 3 docs are provided by `drf-spectacular`. After running the server, visit the Swagger UI or ReDoc URLs above to explore all endpoints interactively.

---

## Deployment

This project is configured for deployment on **Vercel** or any WSGI-compatible platform.

**Production checklist:**

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

Make sure to set these environment variables in your deployment platform:

- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `ALLOWED_HOSTS`

> Static files are served by **WhiteNoise** — no separate static file server needed.

---

## Project Structure

```
whisperfy-django/
├── core/                   # Project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py               # Django management CLI
├── requirements.txt        # Python dependencies
├── db.sqlite3              # SQLite database (development only)
└── .env                    # Environment variables (not committed)
```

---

## Notes

- **Whisper model size**: By default, Whisper may download model weights on first run. Ensure your server has sufficient disk space and internet access.
- **GPU support**: If a CUDA-compatible GPU is available, Whisper will automatically use it for faster transcription.
- **Large files**: For long audio/video files, transcription may take significant time. Consider implementing async task queuing (e.g., Celery + Redis) for production workloads.

---

## License

MIT License — feel free to use and modify.
