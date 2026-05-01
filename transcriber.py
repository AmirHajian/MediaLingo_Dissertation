import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url):
    pattern = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_youtube_transcript(url):
    try:
        video_id = extract_video_id(url)

        if not video_id:
            return "Error: Invalid YouTube URL"

        # Try multiple approaches
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en', 'en-US', 'en-GB']
            )

        if not transcript:
            return "Error: Empty transcript received."

        text = " ".join([entry["text"] for entry in transcript])

        return text

    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."

    except NoTranscriptFound:
        return "Error: No transcript available."

    except Exception as e:
        return f"Error: {str(e)}"