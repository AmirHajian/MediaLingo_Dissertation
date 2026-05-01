import spacy
import streamlit as st
import time
import re

from vocab_extractor import extract_vocabulary
from learner_model import filter_vocabulary
from lesson_generator import generate_lesson
from context_analyzer import extract_domain_keywords
from audio_transcriber import get_transcript_from_youtube
from lesson_formatter import split_lesson_sections
from lesson_formatter import parse_quiz
from lesson_formatter import extract_quiz_and_rest
from pdf_generator import generate_pdf
from flashcards import render_flashcards
from diagnostic_quiz import run_diagnostic_test

# ---------------------------
# Load NLP Model (cached)
# ---------------------------
@st.cache_resource
def load_model():
    return spacy.load("en_core_web_md")

nlp_model = load_model()

# ---------------------------
# UI Helpers
# ---------------------------
def render_styled_lesson(text):
    lines = text.split("\n")
    for line in lines:
        clean = line.strip()
        if not clean: continue
        clean = re.sub(r"^#+\s*", "", clean)
        clean = re.sub(r"^\d+[\.\)]\s*", "", clean)
        clean = re.sub(r"\*\*(\w+)\*\*", r"<b>\1</b>", clean)
        if clean in ["—", "-", "•", "• —"]: continue
        clean = re.sub(r"_{3,}", "______", clean)
        lower = clean.lower()

        if any(word in lower for word in ["definition", "definitions", "example", "examples", "practice", "writing task"]):
            st.markdown(f"### 📘 {clean}", unsafe_allow_html=True)
        elif clean.startswith("-") or clean.startswith("•"):
            content = clean.lstrip("-•").strip()
            if content: st.markdown(f"• {content}", unsafe_allow_html=True)
        else:
            st.markdown(clean, unsafe_allow_html=True)
    st.divider()

def central_toast(message, duration=2):
    empty_space, main_col, empty_space_2 = st.columns([1, 2, 1])
    with main_col:
        container = st.empty()
        container.markdown(
            f"""
            <div style="background-color: #0E1117; padding: 40px; border-radius: 15px; 
            border: 2px solid #ff4b4b; text-align: center;">
                <h1 style="color: white; font-size: 40px;">{message}</h1>
            </div>
            """, unsafe_allow_html=True
        )
        time.sleep(duration)
        container.empty()

# ---------------------------
# Session State Initialization
# ---------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "nav_seed" not in st.session_state:
    st.session_state.nav_seed = 0

state_defaults = {
    "user_name": "",
    "learned_words": set(),
    "user_level": None,
    "onboarding_complete": False,
    "generated": False,
    "lesson": None,
    "raw_text": "",
    "vocab": None,
    "topic": None,
    "keywords": None,
    "user_text": "",
    "youtube_url": "",
    "quiz_submitted": False,
    "quiz_answers": {}
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------
# Page Styling
# ---------------------------
st.set_page_config(page_title="MediaLingo AI", layout="wide")

st.markdown("""
<style>
div[role="radiogroup"] { justify-content: center !important; display: flex !important; width: 100% !important; gap: 15px !important; }
div[role="radiogroup"] label {
    font-size: 18px !important; font-weight: 700 !important; padding: 10px 24px !important;
    border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.3) !important;
    background-color: var(--secondary-background-color) !important;
}
div[role="radiogroup"] label:has(input:checked) { background-color: #1d4ed8 !important; border-color: #1d4ed8 !important; color: white !important; }
div[role="radiogroup"] [data-testid="stWidgetCustomControl"] { display: none !important; }
div[role="radiogroup"] label:has(input:checked) p { color: white !important; -webkit-text-fill-color: white !important; }

.input-card {
    background-color: var(--secondary-background-color);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid rgba(128, 128, 128, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}
.stSelectbox label p {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: var(--primary-color) !important;
}
div[data-testid="stNotification"] {
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(29, 78, 216, 0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Navigation Logic
# ---------------------------
tabs = ["🏠 Home", "📚 Lesson", "🧾 Transcript"]

def sync_tabs():
    # Update active_tab based on the radio selection
    for i, tab_name in enumerate(tabs):
        if st.session_state.main_nav == tab_name:
            st.session_state.active_tab = i

st.markdown("# 📚 MediaLingo")

if not st.session_state.onboarding_complete:
    st.title("👋 Welcome")
    name = st.text_input("What is your name?")
    if name:
        st.session_state.user_name = name
        opt = st.radio("Level Setup:", ["Manually Select", "Take a Test"])
        if opt == "Manually Select":
            lvl = st.selectbox("Your English Level:", ["A1", "A2", "B1", "B2", "C1", "C2"])
            if st.button("Continue"):
                st.session_state.user_level = lvl
                st.session_state.onboarding_complete = True
                st.rerun()
        else:
            run_diagnostic_test()
    st.stop()


# Render Tabs with Sync
selected_tab = st.radio(
    "", 
    tabs, 
    index=st.session_state.active_tab, 
    horizontal=True, 
    key=f"steady_nav_{st.session_state.nav_seed}" 
)

# Sync state if user clicks manually (backup)
if selected_tab == "🏠 Home": st.session_state.active_tab = 0
elif selected_tab == "📚 Lesson": st.session_state.active_tab = 1
elif selected_tab == "🧾 Transcript": st.session_state.active_tab = 2

st.divider()

# --- TAB 1: HOME ---
if selected_tab == "🏠 Home":
    st.session_state.active_tab = 0
    st.markdown(f"## 👋 Welcome, {st.session_state.user_name}!")
    st.markdown("### 📊 Your Progress")
    p_col1, p_col2 = st.columns([1, 3])
    with p_col1:
        st.metric("Level", st.session_state.user_level)
    with p_col2:
        st.metric("Words Learned", len(st.session_state.learned_words))
    
    with st.expander("📜 Vocabulary History"):
        if st.session_state.learned_words:
            for i, word in enumerate(sorted(list(st.session_state.learned_words)), 1):
                st.write(f"{i}. {word}")
        else:
            st.write("Complete a lesson to see words here!")

    st.divider()

    st.subheader("🚀 Generate New Lesson")

    # Using a native Streamlit container with a border gives
    with st.container(border=True):
        input_mode = st.selectbox("**Select your Source Material:**", ["Media Link", "Paste Text"])

        if input_mode == "Media Link":
            youtube_url = st.text_input("🔗 Paste your link here:", 
                                    value=st.session_state.youtube_url, 
                                    placeholder="YouTube, SoundCloud, TikTok, etc...")
            
            with st.expander("ℹ️ Supported Platforms"):
                st.markdown("### 🚀 Works with 100+ Sites")
                st.write("Our AI can transcribe content from almost anywhere on the web:")
                
                st.markdown("""
                - **Video:** YouTube, Vimeo, TikTok, DailyMotion
                - **Audio:** SoundCloud, Mixcloud, Bandcamp, Apple Podcasts
                - **Social:** Twitter (X), Instagram, Facebook, Reddit
                """)
                
                st.divider()
                st.caption("✨ Plus over 100 other platforms. If it's a public link, you can likely learn from it!")

            # Clean spacer
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        
        else:
            user_text = st.text_area("📝 Paste your text here:", value=st.session_state.user_text, height=200, placeholder="Enter an article, transcript, or notes...")

    # Button stays outside for prominence
    if st.button("✨ Create My Lesson", use_container_width=True):
        # logic...
    #if st.button("🚀 Generate Lesson"):
        if (input_mode == "Paste Text" and not user_text.strip()) or (input_mode == "Media Link" and not youtube_url):
            st.warning("Please provide content first.")
            st.stop()

        with st.spinner("Creating your lesson..."):
            text = user_text if input_mode == "Paste Text" else get_transcript_from_youtube(youtube_url)
            if text.startswith("Error"): st.error(text); st.stop()
            
            st.session_state.raw_text = text
            topic, keywords = extract_domain_keywords(text)
            vocab = extract_vocabulary(text, keywords, st.session_state.user_level, nlp_model)
            
            # Filter history
            clean_v = [v for v in vocab if (v[0] if isinstance(v, tuple) else v) not in st.session_state.learned_words]
            if len(clean_v) < 3: clean_v = vocab
            
            profile = {"level": st.session_state.user_level, "known_words": st.session_state.learned_words, "weak_areas": []}
            personalised_vocab = filter_vocabulary(clean_v, profile, keywords) or clean_v[:3]

            st.session_state.lesson = generate_lesson(personalised_vocab, st.session_state.user_level)
            st.session_state.vocab = personalised_vocab
            st.session_state.topic = topic
            st.session_state.keywords = keywords
            st.session_state.quiz_submitted = False

        st.session_state.active_tab = 1
        st.session_state.generated = True
        st.session_state.nav_seed += 1
        central_toast("Lesson Ready! 📚",1)
        st.rerun()

# --- TAB 2: LESSON ---
elif selected_tab == "📚 Lesson":
    st.session_state.active_tab = 1
    if not st.session_state.generated:
        st.info("Go to the Home tab to generate a lesson first.")
    else:
        st.subheader("📝 Lesson Overview")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Topic**")
            st.write(st.session_state.topic)
        with c2:
            st.markdown("**Keywords**")
            st.write(", ".join(st.session_state.keywords))
        
        st.divider()
        st.subheader("📖 Key Vocabulary")
        # Extract just the words if they are tuples
        clean_vocab = [w[0] if isinstance(w, tuple) else w for w in st.session_state.vocab]

        vcols = st.columns(3)
        for i, word in enumerate(clean_vocab):
            with vcols[i % 3]:
                # Logic: If learned, strikethrough. If new, blue box.
                if word in st.session_state.learned_words:
                    st.markdown(
                        f"""
                        <div style="
                            height: 45px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            margin-bottom: 10px;
                            border: 1px dashed rgba(128, 128, 128, 0.3);
                            border-radius: 8px;
                        ">
                            <span style="font-size: 18px; color: #808080; text-decoration: line-through; font-weight: 500;">
                                {word}
                            </span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    st.info(f"**{word}**")

        st.divider()
        num_q = 3 if len(st.session_state.vocab) < 3 else 5
        quiz_text, rest_text = extract_quiz_and_rest(st.session_state.lesson, num_questions=num_q)
        
        rest_text = re.sub(r"(?i)pre[- ]?lesson quiz.*", "", rest_text).strip()

        if quiz_text:
            st.subheader("🧪 Lesson Quiz")
            quiz = parse_quiz(quiz_text)[:num_q]
            for i, q in enumerate(quiz):
                # Styling the question to be Bold and clear
                clean_q = re.sub(r"^\d+[\.\)]\s*", "", q["question"])
                st.markdown(f"**Question {i+1}: {clean_q}**") # Bold font
                
                st.session_state.quiz_answers[i] = st.radio(
                    "Choose the correct answer:", 
                    q["options"], 
                    key=f"q_radio_{st.session_state.nav_seed}_{i}"
                )
            if not st.session_state.quiz_submitted:
                if st.button("Unlock Lesson Content"):
                    score = sum(1 for i, q in enumerate(quiz) if st.session_state.quiz_answers.get(i, "")[:1].lower() == q["answer"][:1].lower())
                    st.session_state.quiz_score, st.session_state.quiz_total = score, len(quiz)
                    st.session_state.quiz_submitted = True
                    for word in clean_vocab: st.session_state.learned_words.add(word)
                    st.rerun()
            else:
                st.success(f"Score: {st.session_state.quiz_score}/{st.session_state.quiz_total}")
                st.divider()

                # FLASHCARDS AND CONTENT
                sections = re.split(r"(definitions|examples|practice|writing task)", rest_text, flags=re.IGNORECASE)
                defs_text, rem_text = "", rest_text
                for i in range(len(sections)):
                    if "definition" in sections[i].lower() and i+1 < len(sections):
                        defs_text = sections[i+1]
                        rem_text = "".join(sections[i+2:])
                        break
                
                if defs_text:
                    st.subheader("🃏 Flashcards")
                    render_flashcards(defs_text, nlp_model)
                
                render_styled_lesson(rem_text)

                # PDF DOWNLOAD RESTORED
                st.subheader("📥 Export")
                quiz_data = [{"question": q["question"], "options": q["options"], "correct": q["answer"], "user": st.session_state.quiz_answers.get(i)} for i, q in enumerate(quiz)]
                pdf_path = generate_pdf(rest_text, st.session_state.user_level, f"{st.session_state.quiz_score}/{st.session_state.quiz_total}", quiz_data)
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download PDF", f, file_name=f"MediaLingo_{st.session_state.topic}.pdf")
        else:
            st.info("🔒 Complete the quiz to unlock the lesson.")

# --- TAB 3: TRANSCRIPT ---
elif selected_tab == "🧾 Transcript":
    st.session_state.active_tab = 2
    if st.session_state.raw_text:
        st.text_area("Full Source Text", value=st.session_state.raw_text, height=500)
    else:
        st.info("No content available yet.")