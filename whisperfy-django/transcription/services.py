import os
import uuid
import whisper
from moviepy import VideoFileClip, AudioFileClip
from django.conf import settings


# Tell ffmpeg/moviepy exactly where ffmpeg is
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
# Whisper model loaded once at server start
_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print(f"Loading Whisper model '{settings.WHISPER_MODEL}' ...")
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        print("Whisper model ready.")
    return _whisper_model


def extract_audio_for_transcription(
    input_path: str,
    is_audio_file: bool = False
) -> str:
    """
    Extract or convert audio from any video or audio file.

    - Video file  → extracts audio track → saves as .wav
    - Audio file  → loads and converts   → saves as .wav

    Returns path to the .wav file.
    """
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = os.path.join(settings.TEMP_DIR, audio_filename)

    if is_audio_file:
        # Audio files: mp3, aac, flac, ogg, etc.
        clip = AudioFileClip(input_path)
        clip.write_audiofile(audio_path, logger=None)
        clip.close()
    else:
        # Video files: mp4, avi, mov, etc.
        clip = VideoFileClip(input_path)

        if clip.audio is None:
            clip.close()
            raise ValueError("This video file has no audio track.")

        clip.audio.write_audiofile(audio_path, logger=None)
        clip.close()

    return audio_path


def transcribe_audio(audio_path: str) -> dict:
    """
    Run Whisper on a .wav file.
    Returns full text, detected language, and timestamped segments.
    """
    model = get_whisper_model()
    result = model.transcribe(audio_path)

    return {
        "text": result["text"].strip(),
        "language": result.get("language"),
        "segments": [
            {
                "start": round(seg["start"], 2),
                "end":   round(seg["end"], 2),
                "text":  seg["text"].strip(),
            }
            for seg in result.get("segments", [])
        ],
    }


def cleanup_files(*paths):
    """Delete multiple temp files safely."""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass