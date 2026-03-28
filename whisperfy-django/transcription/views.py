import os
import uuid
import traceback    # ← add this line

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    cleanup_files,
    extract_audio_for_transcription,
    transcribe_audio,
)

ALLOWED_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".webm",
    ".flv", ".wmv", ".mpeg", ".mpg", ".3gp",
    ".m4v", ".ts", ".mp3", ".wav", ".m4a",
    ".aac", ".ogg", ".flac", ".wma", ".opus",
    ".aiff", ".amr",
}
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg",
    ".flac", ".wma", ".opus", ".aiff", ".amr",
}


class HealthCheckView(APIView):

    @extend_schema(
        tags=["Transcription"],
        summary="Health check",
        description="Returns service status and the currently loaded Whisper model name.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "app":    {"type": "string", "example": "Whisperfy - Transcription"},
                    "model":  {"type": "string", "example": "base"},
                },
            }
        },
    )
    def get(self, request):
        return Response({
            "status": "ok",
            "app":    "Whisperfy - Transcription",
            "model":  settings.WHISPER_MODEL,
        })


class TranscribeVideoView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["Transcription"],
        summary="Transcribe a video or audio file",
        description="""
Upload any video or audio file and receive a complete text transcription.

**How it works:**
1. File is uploaded and saved temporarily
2. Audio is extracted from the video (if a video file)
3. OpenAI Whisper runs speech recognition on the audio
4. Full text + timestamped segments are returned as JSON
5. All temporary files are immediately deleted after processing

**Supported formats:**
MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG, 3GP, M4V, TS,
MP3, WAV, M4A, AAC, OGG, FLAC, WMA, OPUS, AIFF, AMR
        """,
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "The video or audio file to transcribe (max 500 MB)",
                    }
                },
                "required": ["file"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status":    {"type": "string", "example": "success"},
                    "filename":  {"type": "string", "example": "lecture.mp4"},
                    "file_type": {"type": "string", "example": "video"},
                    "transcription": {
                        "type": "object",
                        "properties": {
                            "text":     {"type": "string", "example": "Hello and welcome to today's lecture..."},
                            "language": {"type": "string", "example": "en"},
                            "segments": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "number", "example": 0.0},
                                        "end":   {"type": "number", "example": 3.5},
                                        "text":  {"type": "string", "example": "Hello and welcome"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
            400: {"description": "No file provided or unsupported file type"},
            413: {"description": "File exceeds 500 MB size limit"},
            422: {"description": "Video file has no audio track"},
            500: {"description": "Internal processing error"},
        },
        examples=[
            OpenApiExample(
                "Successful transcription response",
                value={
                    "status": "success",
                    "filename": "lecture.mp4",
                    "file_type": "video",
                    "transcription": {
                        "text": "Hello and welcome to today's lecture on machine learning.",
                        "language": "en",
                        "segments": [
                            {"start": 0.0, "end": 3.5, "text": "Hello and welcome"},
                            {"start": 3.5, "end": 7.2, "text": "to today's lecture on machine learning."},
                        ],
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        input_path = None
        audio_path = None

        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided. Use form-data with key 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = request.FILES["file"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {"error": f"File type '{ext}' is not supported.", "allowed": list(ALLOWED_EXTENSIONS)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            return Response(
                {"error": f"File too large ({size_mb:.1f} MB).", "max_allowed_mb": settings.MAX_FILE_SIZE_MB},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            input_filename = f"{uuid.uuid4()}{ext}"
            input_path = os.path.join(settings.TEMP_DIR, input_filename)

            with open(input_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            is_audio = ext in AUDIO_EXTENSIONS
            audio_path = extract_audio_for_transcription(input_path, is_audio_file=is_audio)
            result = transcribe_audio(audio_path)

            return Response({
                "status":        "success",
                "filename":      uploaded_file.name,
                "file_type":     "audio" if is_audio else "video",
                "transcription": result,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            traceback.print_exc()    # ← add this line
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            cleanup_files(input_path, audio_path)