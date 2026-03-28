import os
import uuid

from django.conf import settings
from django.http import FileResponse
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import cleanup_file, extract_audio

VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".webm",
    ".flv", ".wmv", ".mpeg", ".mpg", ".3gp", ".m4v", ".ts",
}
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg",
    ".flac", ".wma", ".opus", ".aiff", ".amr",
}
ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


class HealthCheckView(APIView):

    @extend_schema(
        tags=["Extraction"],
        summary="Health check",
        description="Returns the extractor service status and all supported formats.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "app":    {"type": "string", "example": "Whisperfy - Extractor"},
                    "supported_video_formats": {"type": "array", "items": {"type": "string"}},
                    "supported_audio_formats": {"type": "array", "items": {"type": "string"}},
                },
            }
        },
    )
    def get(self, request):
        return Response({
            "status": "ok",
            "app":    "Whisperfy - Extractor",
            "supported_video_formats": sorted(VIDEO_EXTENSIONS),
            "supported_audio_formats": sorted(AUDIO_EXTENSIONS),
        })


class ExtractAudioView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["Extraction"],
        summary="Extract audio from a video or convert audio to WAV",
        description="""
Upload any video or audio file and download the audio as a `.wav` file.

**How it works:**
1. File is uploaded and saved temporarily
2. Audio track is extracted using MoviePy
3. A `.wav` file is returned as a direct binary download
4. All temporary files are immediately deleted

**Video input** → extracts the audio track → returns `.wav`
**Audio input** → converts to WAV format → returns `.wav`

**Supported video formats:** MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG, 3GP, M4V, TS
**Supported audio formats:** MP3, WAV, M4A, AAC, OGG, FLAC, WMA, OPUS, AIFF, AMR
        """,
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "The video or audio file to extract audio from (max 500 MB)",
                    }
                },
                "required": ["file"],
            }
        },
        responses={
            200: {
                "description": "WAV audio file — downloads automatically in the browser",
                "content": {
                    "audio/wav": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            400: {"description": "No file provided or unsupported file type"},
            413: {"description": "File exceeds 500 MB size limit"},
            422: {"description": "Video file has no audio track"},
            500: {"description": "Internal processing error"},
        },
        examples=[
            OpenApiExample(
                "Successful extraction",
                description="Returns a binary .wav file as a direct download",
                response_only=True,
                value="<binary .wav file>",
            ),
        ],
    )
    def post(self, request):
        input_path = None

        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided. Use form-data with key 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = request.FILES["file"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {
                    "error": f"File type '{ext}' is not supported.",
                    "supported_video_formats": sorted(VIDEO_EXTENSIONS),
                    "supported_audio_formats": sorted(AUDIO_EXTENSIONS),
                },
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
            audio_path = extract_audio(input_path, is_audio_file=is_audio)

            original_name = os.path.splitext(uploaded_file.name)[0]
            return FileResponse(
                open(audio_path, "rb"),
                content_type="audio/wav",
                as_attachment=True,
                filename=f"{original_name}_audio.wav",
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            cleanup_file(input_path)