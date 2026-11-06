"""MediaLingo - Streamlit entry point.

Flow: profile setup -> lesson generation -> quiz -> lesson -> transcript.
Presentation is delegated to ui.py so the logic below stays readable.
"""

import re
from html import escape

import spacy
import streamlit as st

import ui
from audio_transcriber import get_transcript_from_youtube
from context_analyzer import extract_domain_keywords
from diagnostic_quiz import run_diagnostic_test
from flashcards import render_flashcards
from learner_model import filter_vocabulary
from lesson_formatter import extract_quiz_and_rest, parse_quiz
from lesson_generator import generate_lesson
from pdf_generator import generate_pdf
from vocab_extractor import extract_vocabulary

st.set_page_config(
    page_title="MediaLingo",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.inject_styles()


@st.cache_resource
def load_model():
    return spacy.load("en_core_web_md")


nlp_model = load_model()

# ---------------------------
# Session state
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
    "quiz_answers": {},
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

notice = st.session_state.pop("notice", None)

ui.brand_header()

if notice:
    st.toast(notice)

# ---------------------------
# Onboarding
# ---------------------------
if not st.session_state.onboarding_complete:
    _, middle, _ = st.columns([1, 1.6, 1])

    with middle:
        with st.container(border=True):
            st.markdown('<p class="ml-eyebrow">Getting started</p>', unsafe_allow_html=True)
            st.markdown('<h2 class="ml-h2">Set up your profile</h2>', unsafe_allow_html=True)
            st.markdown(
                '<p class="ml-copy">Your level decides which vocabulary and how much '
                "difficulty each lesson works with.</p>",
                unsafe_allow_html=True,
            )

            name = st.text_input("Your name", placeholder="Type your name")

            if name:
                st.session_state.user_name = name.strip()

                mode = st.radio(
                    "Level setup",
                    ["Select my level", "Take a level test"],
                    horizontal=True,
                )

                if mode == "Select my level":
                    level = st.selectbox(
                        "English level",
                        ["A1", "A2", "B1", "B2", "C1", "C2"],
                        index=2,
                    )
                    if st.button("Continue", type="primary", use_container_width=True):
                        st.session_state.user_level = level
                        st.session_state.onboarding_complete = True
                        st.rerun()
                else:
                    run_diagnostic_test()

    st.stop()

# ---------------------------
# Navigation
# ---------------------------
tabs = ["Home", "Lesson", "Transcript"]
selected_tab = st.radio(
    "Navigation",
    tabs,
    index=st.session_state.active_tab,
    horizontal=True,
    key=f"nav_{st.session_state.nav_seed}",
    label_visibility="collapsed",
)
st.session_state.active_tab = tabs.index(selected_tab)

user_name = st.session_state.user_name or "there"

# ---------------------------
# Home
# ---------------------------
if selected_tab == "Home":
    st.markdown(f'<h2 class="ml-h2">Good to see you, {escape(user_name)}</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ml-copy">Start from a media link or a piece of text. Your level '
        "and the words you have already practised shape what the lesson focuses on.</p>",
        unsafe_allow_html=True,
    )

    ui.stats(
        [
            (st.session_state.user_level, "Current level"),
            (len(st.session_state.learned_words), "Words learned"),
            (st.session_state.topic or "Not set", "Current focus"),
        ]
    )

    with st.expander("Vocabulary history"):
        if st.session_state.learned_words:
            for index, word in enumerate(sorted(st.session_state.learned_words), 1):
                st.write(f"{index}. {word}")
        else:
            st.write("Words you unlock in a quiz appear here.")

    ui.section("New lesson", "Choose where the material comes from.")

    with st.container(border=True):
        input_mode = st.selectbox("Source material", ["Media link", "Paste text"])

        youtube_url = st.session_state.youtube_url
        user_text = st.session_state.user_text

        if input_mode == "Media link":
            youtube_url = st.text_input(
                "Media link",
                value=st.session_state.youtube_url,
                placeholder="Paste a link from YouTube, SoundCloud, TikTok and more",
            )
            with st.expander("Supported platforms"):
                st.markdown(
                    "**Video**  YouTube, Vimeo, TikTok, Dailymotion  \n"
                    "**Audio**  SoundCloud, Mixcloud, Bandcamp, Apple Podcasts  \n"
                    "**Social**  X, Instagram, Facebook, Reddit"
                )
                st.caption("Any public link with accessible audio works.")
        else:
            user_text = st.text_area(
                "Text",
                value=st.session_state.user_text,
                height=220,
                placeholder="Paste an article, transcript or your own notes",
            )

        generate = st.button("Create lesson", type="primary", use_container_width=True)

    if generate:
        if input_mode == "Paste text" and not user_text.strip():
            st.warning("Add some text before creating a lesson.")
            st.stop()

        if input_mode == "Media link" and not youtube_url.strip():
            st.warning("Add a link before creating a lesson.")
            st.stop()

        error_message = None

        with st.spinner("Building your lesson"):
            text = (
                user_text
                if input_mode == "Paste text"
                else get_transcript_from_youtube(youtube_url)
            )

            if text.startswith("Error"):
                error_message = text
            else:
                st.session_state.raw_text = text

                try:
                    topic, keywords = extract_domain_keywords(text)
                    vocab = extract_vocabulary(
                        text, keywords, st.session_state.user_level, nlp_model
                    )

                    fresh_vocab = [
                        item
                        for item in vocab
                        if (item[0] if isinstance(item, tuple) else item)
                        not in st.session_state.learned_words
                    ]
                    if len(fresh_vocab) < 3:
                        fresh_vocab = vocab

                    profile = {
                        "level": st.session_state.user_level,
                        "known_words": st.session_state.learned_words,
                        "weak_areas": [],
                    }
                    personalised = (
                        filter_vocabulary(fresh_vocab, profile, keywords)
                        or fresh_vocab[:3]
                    )

                    st.session_state.lesson = generate_lesson(
                        personalised, st.session_state.user_level
                    )
                    st.session_state.vocab = personalised
                    st.session_state.topic = topic
                    st.session_state.keywords = keywords
                    st.session_state.quiz_submitted = False
                except RuntimeError as error:
                    error_message = str(error)
                except Exception as error:  # noqa: BLE001 - surfaced to the user
                    error_message = f"Lesson generation failed: {error}"

        if error_message:
            st.error(error_message)
            st.stop()

        st.session_state.active_tab = 1
        st.session_state.generated = True
        st.session_state.nav_seed += 1
        st.session_state.notice = "Lesson ready"
        st.rerun()

# ---------------------------
# Lesson
# ---------------------------
elif selected_tab == "Lesson":
    if not st.session_state.generated:
        ui.empty(
            "No lesson yet",
            "Create a lesson from the Home tab and it will appear here.",
        )
    else:
        vocab = st.session_state.vocab or []
        clean_vocab = [word[0] if isinstance(word, tuple) else word for word in vocab]

        st.markdown(
            f'<h2 class="ml-h2">{escape(st.session_state.topic or "Lesson")}</h2>',
            unsafe_allow_html=True,
        )
        ui.chips(st.session_state.keywords or [])
        ui.stats(
            [
                (st.session_state.user_level, "Level"),
                (len(clean_vocab), "New words"),
                (len(st.session_state.learned_words), "Words learned"),
            ]
        )

        ui.section("Key vocabulary")
        ui.chips(clean_vocab, learned=st.session_state.learned_words)

        num_questions = 3 if len(vocab) < 3 else 5
        quiz_text, rest_text = extract_quiz_and_rest(
            st.session_state.lesson, num_questions=num_questions
        )
        rest_text = re.sub(r"(?i)pre[- ]?lesson quiz.*", "", rest_text).strip()

        if quiz_text:
            ui.section("Lesson quiz", "Answer every question to unlock the lesson.")
            quiz = parse_quiz(quiz_text)[:num_questions]

            with st.container(border=True):
                for index, question in enumerate(quiz):
                    clean_question = re.sub(r"^\d+[\.\)]\s*", "", question["question"])
                    ui.question_label(index + 1, len(quiz), clean_question)

                    st.session_state.quiz_answers[index] = st.radio(
                        f"Question {index + 1}",
                        question["options"],
                        key=f"q_{st.session_state.nav_seed}_{index}",
                        label_visibility="collapsed",
                    )

                if not st.session_state.quiz_submitted:
                    if st.button(
                        "Unlock lesson content",
                        type="primary",
                        use_container_width=True,
                    ):
                        correct = sum(
                            1
                            for index, question in enumerate(quiz)
                            if st.session_state.quiz_answers.get(index, "")[:1].lower()
                            == question["answer"][:1].lower()
                        )
                        st.session_state.quiz_score = correct
                        st.session_state.quiz_total = len(quiz)
                        st.session_state.quiz_submitted = True

                        for word in clean_vocab:
                            st.session_state.learned_words.add(word)

                        st.rerun()
                else:
                    ui.score(
                        st.session_state.quiz_score, st.session_state.quiz_total
                    )

            sections = re.split(
                r"(definitions|examples|practice|writing task)",
                rest_text,
                flags=re.IGNORECASE,
            )
            definitions_text, remaining_text = "", rest_text

            for index in range(len(sections)):
                if "definition" in sections[index].lower() and index + 1 < len(sections):
                    definitions_text = sections[index + 1]
                    remaining_text = "".join(sections[index + 2:])
                    break

            if st.session_state.quiz_submitted:
                if definitions_text:
                    ui.section("Flashcards", "Select a card to reveal its meaning.")
                    render_flashcards(definitions_text, nlp_model)

                ui.section("Lesson")
                ui.lesson_body(remaining_text)

                ui.section("Export", "Keep a copy of the lesson and your result.")
                quiz_data = [
                    {
                        "question": question["question"],
                        "options": question["options"],
                        "correct": question["answer"],
                        "user": st.session_state.quiz_answers.get(index),
                    }
                    for index, question in enumerate(quiz)
                ]
                pdf_path = generate_pdf(
                    rest_text,
                    st.session_state.user_level,
                    f"{st.session_state.quiz_score}/{st.session_state.quiz_total}",
                    quiz_data,
                )

                with open(pdf_path, "rb") as handle:
                    st.download_button(
                        "Download PDF",
                        handle,
                        file_name=f"MediaLingo_{st.session_state.topic}.pdf",
                        use_container_width=True,
                    )
        else:
            ui.empty(
                "Lesson locked",
                "No quiz was generated for this material, so the lesson stays locked. "
                "Try creating the lesson again.",
            )

# ---------------------------
# Transcript
# ---------------------------
elif selected_tab == "Transcript":
    if st.session_state.raw_text:
        ui.section("Source transcript", "The material this lesson was built from.")
        with st.container(border=True):
            st.text_area(
                "Transcript",
                value=st.session_state.raw_text,
                height=460,
                label_visibility="collapsed",
            )
    else:
        ui.empty(
            "Nothing here yet",
            "Load a media link or paste text on the Home tab to see the full transcript.",
        )
