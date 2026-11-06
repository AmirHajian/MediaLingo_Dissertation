from html import escape

import streamlit as st


def get_diagnostic_questions():
    """Returns the research-backed 12-question set."""
    return [
        {"q": "Hello, what ______ your name?", "options": ["is", "are", "am"], "correct": "is", "level": "A1"},
        {"q": "I have two ______.", "options": ["brother", "brothers", "brotheres"], "correct": "brothers", "level": "A1"},
        {"q": "She ______ to the gym every morning.", "options": ["go", "goes", "going"], "correct": "goes", "level": "A2"},
        {"q": "I’m tired. I want to ______ to bed.", "options": ["go", "do", "get"], "correct": "go", "level": "A2"},
        {"q": "I ______ her for five years.", "options": ["know", "have known", "am knowing"], "correct": "have known", "level": "B1"},
        {"q": "If I ______ more money, I would buy a car.", "options": ["have", "had", "will have"], "correct": "had", "level": "B1"},
        {"q": "If I ______ you, I’d take the job.", "options": ["was", "am", "were"], "correct": "were", "level": "B2"},
        {"q": "The movie was so ______ that I fell asleep.", "options": ["bored", "boring", "bore"], "correct": "boring", "level": "B2"},
        {"q": "The meeting was ______ off because of the snow.", "options": ["put", "called", "set"], "correct": "called", "level": "C1"},
        {"q": "I wish I ______ harder when I was at school.", "options": ["studied", "had studied", "would study"], "correct": "had studied", "level": "C1"},
        {"q": "No sooner ______ the house than it started raining.", "options": ["I had left", "had I left", "did I left"], "correct": "had I left", "level": "C2"},
        {"q": "The report ______ the need for urgent action.", "options": ["highlights", "tells", "says"], "correct": "highlights", "level": "C2"},
    ]


def calculate_cefr_level(score):
    """Assigns level based on cumulative proficiency logic."""
    if score <= 2:
        return "A1"
    elif score <= 4:
        return "A2"
    elif score <= 6:
        return "B1"
    elif score <= 8:
        return "B2"
    elif score <= 10:
        return "C1"
    else:
        return "C2"


def run_diagnostic_test():
    st.markdown('<p class="ml-eyebrow">Level test</p>', unsafe_allow_html=True)
    st.markdown('<h3 class="ml-h3">Answer 12 questions</h3>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ml-copy">The result sets the vocabulary and difficulty of your '
        "lessons. You can retake it at any time.</p>",
        unsafe_allow_html=True,
    )

    questions = get_diagnostic_questions()
    score = 0

    for index, item in enumerate(questions):
        st.markdown(
            f'<div class="ml-q">'
            f'<span class="ml-q-count">Question {index + 1} of {len(questions)}</span>'
            f"<p>{escape(item['q'])}</p></div>",
            unsafe_allow_html=True,
        )

        user_choice = st.radio(
            "Answer",
            options=item["options"],
            index=None,
            key=f"cefr_q_{index}",
            label_visibility="collapsed",
        )

        if user_choice == item["correct"]:
            score += 1

    if st.button("Submit assessment", type="primary", use_container_width=True):
        if any(
            st.session_state.get(f"cefr_q_{index}") is None
            for index in range(len(questions))
        ):
            st.warning("Answer every question before submitting.")
        else:
            level = calculate_cefr_level(score)

            st.session_state.user_level = level
            st.session_state.onboarding_complete = True
            st.session_state.notice = f"Your level is {level}"

            st.rerun()
