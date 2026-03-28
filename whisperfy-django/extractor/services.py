import os
import uuid
from moviepy import VideoFileClip, AudioFileClip
from django.conf import settings

# Ensure ffmpeg is findable
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"


def extract_audio(input_path: str, is_audio_file: bool = False) -> str:
    """
    Extract or convert audio from any video or audio file.

    - Video file  → extracts audio track → saves as .wav
    - Audio file  → loads and converts   → saves as .wav

    Returns the full path to the output .wav file.
    """
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = os.path.join(settings.TEMP_DIR, audio_filename)

    if is_audio_file:
        # Handle audio files (mp3, aac, flac, etc.)
        clip = AudioFileClip(input_path)
        clip.write_audiofile(audio_path, logger=None)
        clip.close()
    else:
        # Handle video files (mp4, avi, mov, etc.)
        clip = VideoFileClip(input_path)

        if clip.audio is None:
            clip.close()
            raise ValueError("This video file has no audio track.")

        clip.audio.write_audiofile(audio_path, logger=None)
        clip.close()

    return audio_path


def cleanup_file(path: str):
    """Delete a single temp file safely."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass