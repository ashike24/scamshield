import os
import requests
from dotenv import load_dotenv

load_dotenv()

STT_URL = "https://api.vachana.ai/stt/v3"


def transcribe(audio_path):
    """Send a short clip (max 30 s) to Gnani Prisma v3.0.
    Returns (transcript, detected_language_code)."""
    api_key = os.getenv("GNANI_API_KEY")
    with open(audio_path, "rb") as f:
        r = requests.post(
            STT_URL,
            headers={"X-API-Key-ID": api_key},
            files={"audio_file": (os.path.basename(audio_path), f)},
            data={
                "model": "prisma-v3.0",
                "language_code": "indic-auto",
                "format": "transcribe",
            },
            timeout=60,
        )
    body = r.json()
    if not body.get("success"):
        raise RuntimeError(f"Gnani STT error: {body}")
    return body.get("transcript", ""), body.get("detected_language_code")


TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"


def speak_english(text):
    """Turn English text into speech with Gnani Timbre. Returns WAV audio bytes."""
    api_key = os.getenv("GNANI_API_KEY")
    r = requests.post(
        TTS_URL,
        headers={"X-API-Key-ID": api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "voice": "Kaveri",
            "model": "timbre-v2.5",
            "language": "en-IN",
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 24000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        },
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Gnani TTS error {r.status_code}: {r.text}")
    return r.content
