# ScamShield - Solution Pitch

Great Indian AI Internship Challenge 2026 | Ashik E, IIT Kanpur

Live app: https://scamshield-ashike24.streamlit.app
Code: https://github.com/ashike24/scamshield

## The problem
Scam callers pressure people in the language they speak at home, using urgency, fake authority and requests for OTPs or money. Blocklists and keyword filters miss new scripts and non-English calls, and the listener has little time to think.

## The solution
ScamShield listens to one call at a time in an Indian language, translates it to English, scores how likely it is to be a scam, highlights the risky sentences in red and explains why each one is risky.

## How it works
1. Gnani Prisma v3.0 detects the language (indic-auto) and transcribes the call in that same language.
2. Sarvam-105B makes one call that returns the English translation, a 0-100 risk score, the risky sentences and a reason for each.
3. Gnani Timbre reads the English translation aloud, but only when the user presses a button after the call. Nothing plays during the call.

Gnani handles everything it can. Sarvam is used only for translation and scam reasoning, because Gnani's API has no translation endpoint and its Evon model has no hosted endpoint.

## What makes it different
- It judges intent and tactics with an LLM, not a fixed list of words.
- Every flagged line comes with a reason, so the user can decide for themselves.
- Works across the 10 languages Gnani Prisma supports: Hindi, English, Bengali, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Tamil and Telugu.

## Honest limitations
- The risk percentage is an AI estimate, not a calibrated probability.
- Clips are limited to 30 seconds, and calls are analysed one at a time.
- Only the 10 supported languages work; other languages show a warning.
- Tested on synthetic, scripted calls only (Hindi so far). No real calls or personal data are used.

## Next steps
Live streaming analysis with Gnani's WebSocket API, testing on a larger synthetic set in every supported language, and adding languages as Gnani supports them.
