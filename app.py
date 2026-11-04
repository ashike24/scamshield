import html
import os
import tempfile

import streamlit as st

import analysis
import gnani

LANGS = {
    "hi-IN": "Hindi", "en-IN": "English", "bn-IN": "Bengali",
    "gu-IN": "Gujarati", "kn-IN": "Kannada", "ml-IN": "Malayalam",
    "mr-IN": "Marathi", "pa-IN": "Punjabi", "ta-IN": "Tamil", "te-IN": "Telugu",
}

st.set_page_config(page_title="ScamShield")
st.title("ScamShield")
st.caption(
    "Checks a phone call for scam signs in 10 Indian languages. "
    "Use only synthetic, scripted calls - never real calls or personal data."
)


def highlight(text, sentences):
    out = html.escape(text)
    for s in sentences:
        s_esc = html.escape(s.strip())
        if s_esc and s_esc in out:
            out = out.replace(
                s_esc,
                '<span style="color:#d00000;font-weight:bold">' + s_esc + "</span>",
                1,
            )
    return out


recorded = st.audio_input("Record the call")
uploaded = st.file_uploader(
    "Or upload a clip (max 30 seconds)",
    type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
)
audio = recorded or uploaded

if st.button("Analyze call", type="primary", disabled=audio is None):
    ext = os.path.splitext(getattr(audio, "name", "audio.wav"))[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(audio.getvalue())
        path = tmp.name
    try:
        with st.spinner("Transcribing the call..."):
            transcript, lang = gnani.transcribe(path)
        if not transcript.strip():
            st.session_state.pop("result", None)
            st.warning("No speech was detected. Please try again.")
        else:
            with st.spinner("Translating and checking for scam signs..."):
                result = analysis.analyze(transcript, lang)
            st.session_state["result"] = {
                "language": lang,
                "transcript": transcript,
                "result": result,
            }
            st.session_state.pop("voice", None)
    except Exception as e:
        st.session_state.pop("result", None)
        st.error("Something went wrong: " + str(e))
    finally:
        os.remove(path)

data = st.session_state.get("result")
if data:
    result = data["result"]
    lang_name = LANGS.get(data["language"])
    if lang_name:
        st.write("Detected language: **" + lang_name + "**")
    else:
        st.warning("This language may not be supported, so results may be unreliable.")

    score = result["risk_score"]
    st.metric("Scam risk (estimate)", str(score) + "%")
    st.progress(score / 100)
    st.write("**Risk level:** " + str(result.get("risk_level", "")).capitalize())
    st.write(result["summary"])

    flagged = result["flagged_sentences"]
    st.subheader("English translation")
    sentences = [f.get("sentence", "") for f in flagged]
    st.markdown(
        highlight(result["english_translation"], sentences),
        unsafe_allow_html=True,
    )

    st.subheader("Why these lines are risky")
    if flagged:
        for f in flagged:
            st.markdown("- **" + f.get("sentence", "") + "**  \n  " + f.get("reason", ""))
    else:
        st.write("No risky lines were found.")

    with st.expander("Original transcript"):
        st.write(data["transcript"])

    st.divider()
    if st.button("Play English voice"):
        try:
            with st.spinner("Generating voice..."):
                st.session_state["voice"] = gnani.speak_english(
                    result["english_translation"]
                )
        except Exception as e:
            st.error("Could not generate voice: " + str(e))
    if "voice" in st.session_state:
        st.audio(st.session_state["voice"], format="audio/wav")
