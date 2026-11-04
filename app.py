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

st.set_page_config(
    page_title="ScamShield - Scam Call Detector",
    page_icon=":shield:",
    layout="centered",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 920px;}
.hero {background: linear-gradient(135deg,#0f172a 0%,#1e3a8a 55%,#2563eb 100%);
  border-radius: 22px; padding: 2.2rem 2rem; color: #ffffff; margin-bottom: 1.2rem;
  box-shadow: 0 10px 30px rgba(30,58,138,.25);}
.hero-title {font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em; color: #ffffff;}
.hero p {color: #dbeafe; font-size: 1.05rem; margin: .5rem 0 1rem 0;}
.chip {display: inline-block; background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.3); color: #ffffff; border-radius: 999px;
  padding: .25rem .85rem; font-size: .8rem; margin: 0 .4rem .4rem 0;}
.chip-lang {display: inline-block; background: #eef2ff; border: 1px solid #c7d2fe;
  color: #3730a3; border-radius: 999px; padding: .2rem .7rem; font-size: .78rem;
  margin: 0 .3rem .3rem 0;}
.steps {display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-bottom: 1.2rem;}
@media (max-width: 640px) {.steps {grid-template-columns: repeat(2, 1fr);}}
.step {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: .9rem; box-shadow: 0 2px 8px rgba(15,23,42,.04); color: #0f172a;}
.step-ico {font-size: 1.4rem;}
.step-t {font-weight: 700; margin-top: .2rem;}
.step-d {font-size: .78rem; color: #64748b; margin-top: .15rem;}
.card {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
  padding: 1.2rem 1.3rem; box-shadow: 0 2px 10px rgba(15,23,42,.05);
  margin-bottom: 1rem; color: #0f172a;}
.card h3 {margin: 0 0 .7rem 0; font-size: 1.05rem; color: #0f172a;}
.gauge {width: 150px; height: 150px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; margin: .2rem auto;}
.gauge-in {width: 116px; height: 116px; border-radius: 50%; background: #ffffff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;}
.gauge-in b {font-size: 2.1rem; line-height: 1;}
.gauge-in small {color: #64748b; font-size: .68rem; text-transform: uppercase; letter-spacing: .06em;}
.badge {display: inline-block; font-weight: 700; border-radius: 999px;
  padding: .3rem .9rem; font-size: .9rem; margin-right: .5rem;}
.summary {margin: .8rem 0 0 0; line-height: 1.55; color: #334155;}
.trans {font-size: 1.05rem; line-height: 1.75; color: #0f172a;}
.hl {color: #b91c1c; background: #fee2e2; font-weight: 700; padding: 1px 5px; border-radius: 5px;}
.legend {margin-top: .8rem; font-size: .8rem; color: #64748b;}
.reason {border-left: 4px solid #dc2626; background: #fef2f2; border-radius: 10px;
  padding: .7rem .9rem; margin-bottom: .6rem;}
.reason-s {font-weight: 700; color: #991b1b;}
.reason-r {color: #475569; margin-top: .25rem; font-size: .92rem;}
.muted {color: #64748b;}
.foot {text-align: center; color: #94a3b8; font-size: .78rem; margin-top: 2rem; line-height: 1.6;}
</style>
""", unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def level_of(score):
    if score < 30:
        return "Low risk", "#16a34a", "#dcfce7"
    if score < 60:
        return "Medium risk", "#d97706", "#fef3c7"
    return "High risk", "#dc2626", "#fee2e2"


def highlight(text, sentences):
    out = html.escape(text)
    for s in sentences:
        s_esc = html.escape(s.strip())
        if s_esc and s_esc in out:
            out = out.replace(s_esc, '<span class="hl">' + s_esc + "</span>", 1)
    return out.replace("\n", "<br>")


with st.sidebar:
    st.markdown("### About ScamShield")
    st.write(
        "ScamShield listens to a call, translates it to English and shows how "
        "likely it is to be a scam, with the exact lines that look risky and why."
    )
    st.markdown("**Supported languages**")
    st.markdown(
        "".join('<span class="chip-lang">' + n + "</span>" for n in LANGS.values()),
        unsafe_allow_html=True,
    )
    st.markdown("**Privacy**")
    st.write(
        "Use only synthetic, scripted calls. This app does not save your audio; "
        "it is sent to the Gnani and Sarvam APIs for processing."
    )

st.markdown(
    '<div class="hero">'
    '<div class="hero-title">&#128737; ScamShield</div>'
    "<p>Understand any suspicious call in seconds. Speak or upload a call in an "
    "Indian language and get an English translation, a scam-risk score and the "
    "exact lines that look risky.</p>"
    '<span class="chip">10 Indian languages</span>'
    '<span class="chip">AI reasoning, not keyword matching</span>'
    '<span class="chip">Powered by Gnani.ai</span>'
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="steps">'
    '<div class="step"><div class="step-ico">&#127908;</div><div class="step-t">Listen</div>'
    '<div class="step-d">Gnani Prisma detects the language and transcribes</div></div>'
    '<div class="step"><div class="step-ico">&#127760;</div><div class="step-t">Translate</div>'
    '<div class="step-d">Converted to English by Sarvam AI</div></div>'
    '<div class="step"><div class="step-ico">&#128269;</div><div class="step-t">Analyze</div>'
    '<div class="step-d">An LLM scores the risk and explains why</div></div>'
    '<div class="step"><div class="step-ico">&#128266;</div><div class="step-t">Speak</div>'
    '<div class="step-d">Gnani Timbre reads it aloud on demand</div></div>'
    "</div>",
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("**Add the call recording**")
    tab_rec, tab_up = st.tabs(["Record", "Upload a clip"])
    with tab_rec:
        recorded = st.audio_input("Record the call (max 30 seconds)")
    with tab_up:
        uploaded = st.file_uploader(
            "Upload an audio clip (max 30 seconds)",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
        )
    audio = recorded or uploaded
    analyze = st.button("Analyze call", type="primary", disabled=audio is None)

if analyze:
    ext = os.path.splitext(getattr(audio, "name", "audio.wav"))[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(audio.getvalue())
        path = tmp.name
    try:
        with st.spinner("Listening to the call..."):
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
    score = result["risk_score"]
    label, color, bg = level_of(score)
    lang_name = LANGS.get(data["language"])
    if lang_name:
        lang_chip = '<span class="chip-lang">Detected: ' + lang_name + "</span>"
    else:
        lang_chip = '<span class="chip-lang">Language not supported - results may be unreliable</span>'

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            '<div class="card" style="text-align:center">'
            '<div class="gauge" style="background:conic-gradient('
            + color + " " + str(score) + '%, #e5e7eb 0)">'
            '<div class="gauge-in"><b style="color:' + color + '">' + str(score)
            + "%</b><small>scam risk</small></div></div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="card"><span class="badge" style="color:' + color
            + ";background:" + bg + '">' + label + "</span>" + lang_chip
            + '<p class="summary">' + esc(result["summary"]) + "</p></div>",
            unsafe_allow_html=True,
        )

    flagged = result["flagged_sentences"]
    sentences = [f.get("sentence", "") for f in flagged]
    st.markdown(
        '<div class="card"><h3>&#127760; English translation</h3>'
        '<div class="trans">' + highlight(result["english_translation"], sentences)
        + '</div><div class="legend"><span class="hl">Red</span> '
        "marks wording the AI found risky. The score is an estimate, not a guarantee."
        "</div></div>",
        unsafe_allow_html=True,
    )

    parts = ['<div class="card"><h3>&#9888; Why these lines are risky</h3>']
    if flagged:
        for f in flagged:
            parts.append(
                '<div class="reason"><div class="reason-s">' + esc(f.get("sentence", ""))
                + '</div><div class="reason-r">' + esc(f.get("reason", "")) + "</div></div>"
            )
    else:
        parts.append('<p class="muted">No risky lines were found.</p>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

    with st.expander("Original transcript"):
        st.write(data["transcript"])

    with st.container(border=True):
        st.markdown("**&#128266; Hear it in English**", unsafe_allow_html=True)
        st.caption("Kept silent during the call. Plays only when you press the button.")
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

st.markdown(
    '<div class="foot">Built for the Great Indian AI Internship Challenge 2026<br>'
    "Powered by Gnani.ai (speech) and Sarvam AI (translation and reasoning)<br>"
    "Use only synthetic, scripted calls.</div>",
    unsafe_allow_html=True,
)
