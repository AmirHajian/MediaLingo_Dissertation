import yt_dlp
import whisper
import os
import ssl
import certifi

# Configure SSL contexts using certifi to ensure secure connections
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
# Configure yt-dlp to extract the highest quality audio stream
def download_audio(youtube_url, output_path="audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return output_path

# Initialise the Whisper ASR model (base version for speed/efficiency)
def transcribe_audio(file_path):
    model = whisper.load_model("base")

    result = model.transcribe(file_path)

    return result["text"]


def get_transcript_from_youtube(url):
    try:
        audio_file = download_audio(url)

        text = transcribe_audio(audio_file)

        # Remove temporary audio file to free up local disk space
        if os.path.exists(audio_file):
            os.remove(audio_file)

        return text

    except Exception as e:
        return f"Error: {str(e)}"