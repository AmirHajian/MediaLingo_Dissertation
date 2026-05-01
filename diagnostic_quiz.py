import streamlit as st
import time

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
        {"q": "The report ______ the need for urgent action.", "options": ["highlights", "tells", "says"], "correct": "highlights", "level": "C2"}
    ]

def calculate_cefr_level(score):
    """Assigns level based on cumulative proficiency logic."""
    if score <= 2: return "A1"
    elif score <= 4: return "A2"
    elif score <= 6: return "B1"
    elif score <= 8: return "B2"
    elif score <= 10: return "C1"
    else: return "C2"

def run_diagnostic_test():
    st.subheader("🧪 CEFR-Aligned Diagnostic Test")
    st.info("Complete these 12 questions to personalise your learning experience.")

    questions = get_diagnostic_questions()
    score = 0

    # Render questions in a clean format
    for i, item in enumerate(questions):
            # Enhanced Question Header
            st.markdown(f"""
                <div style="margin-top: 30px; margin-bottom: 5px;">
                    <span style="color: #60a5fa; font-weight: 800; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                        Question {i+1} of {len(questions)}
                    </span>
                    <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: var(--text-color); line-height: 1.4;">
                        {item['q']}
                    </h2>
                </div>
            """, unsafe_allow_html=True)

            # The radio buttons for options
            user_choice = st.radio(
                "Select the correct answer:", 
                options=item["options"],
                index=None,
                key=f"cefr_q_{i}",
                label_visibility="collapsed" 
            )
            
            if user_choice == item["correct"]:
                score += 1
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()

    if st.button("Submit Assessment", use_container_width=True):
        if any(st.session_state.get(f"cefr_q_{i}") is None for i in range(len(questions))):
            st.warning("Please answer all questions before submitting.")
        else:
            level = calculate_cefr_level(score)
            
            # Save to session state
            st.session_state.user_level = level
            st.session_state.onboarding_complete = True

            with st.spinner("Analyzing your proficiency..."):
                time.sleep(2)
                st.success(f"Assessment Complete! Your estimated level is: **{level}**")
                time.sleep(1.5)
                st.rerun()