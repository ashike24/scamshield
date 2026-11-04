import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"

SYSTEM_PROMPT = """You are a fraud analyst for phone calls in India.
You receive the transcript of ONE phone call (possibly in an Indian language).

Do two things:
1. Translate the whole transcript faithfully into English. Do not add, remove or summarise anything.
2. Judge how likely the call is a scam, by reasoning about the caller's INTENT and tactics,
   not by matching keywords. Consider: impersonating a bank, police, courier, government or
   company; creating urgency or fear; threats of arrest or account closure; asking for OTP, PIN,
   passwords, card or account details, or remote access; asking for money or gift cards; secrecy
   requests; prizes or offers that are too good to be true. A genuine call can mention a bank or
   an OTP without being a scam (for example, a warning never to share an OTP), so judge the
   context and what is actually being asked of the listener.

Return ONLY valid JSON, with no other text and no markdown fences, in exactly this shape:
{
  "english_translation": "the full English translation",
  "risk_score": 0-100 (integer; your estimate of how likely this call is a scam),
  "risk_level": "low" or "medium" or "high",
  "summary": "2-3 sentences explaining the overall verdict",
  "flagged_sentences": [
    {"sentence": "an EXACT copy of a risky sentence taken from english_translation",
     "reason": "why this sentence is risky"}
  ]
}
If nothing is risky, return an empty flagged_sentences list and a low score."""


def _parse_json(text):
    if not text:
        raise ValueError("Sarvam returned no content - the reply may have been cut off")
    if "</think>" in text:
        text = text.split("</think>")[-1]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return JSON: " + text[:200])
    return json.loads(text[start:end + 1])


def analyze(transcript, language_code=None):
    """Translate the transcript to English and score it for scam risk (Sarvam-105B)."""
    api_key = os.getenv("SARVAM_API_KEY")
    user_msg = "Detected language: " + str(language_code) + "\n\nTranscript:\n" + transcript
    r = requests.post(
        CHAT_URL,
        headers={"api-subscription-key": api_key, "Content-Type": "application/json"},
        json={
            "model": "sarvam-105b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.2,
            "reasoning_effort": None, "max_tokens": 3000,
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError("Sarvam error " + str(r.status_code) + ": " + r.text)
    content = r.json()["choices"][0]["message"]["content"]
    result = _parse_json(content)
    result["risk_score"] = max(0, min(100, int(result.get("risk_score", 0))))
    result.setdefault("english_translation", "")
    result.setdefault("flagged_sentences", [])
    result.setdefault("summary", "")
    return result

