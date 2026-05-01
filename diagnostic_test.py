def run_diagnostic_test():
    st.subheader("🧪 Quick Level Test")

    score = 0

    q1 = st.radio(
        "Choose the correct sentence:",
        ["She go to school.", "She goes to school.", "She going school."]
    )
    if q1 == "She goes to school.":
        score += 1

    q2 = st.radio(
        "What does 'improve' mean?",
        ["Make better", "Make worse", "Stop working"]
    )
    if q2 == "Make better":
        score += 1

    q3 = st.radio(
        "Select the advanced word:",
        ["big", "huge", "enormous"]
    )
    if q3 == "enormous":
        score += 1

    if st.button("Submit Test"):
        if score <= 1:
            level = "A2"
        elif score == 2:
            level = "B1"
        else:
            level = "B2"

        st.session_state.user_level = level
        st.session_state.onboarding_complete = True

        st.success(f"Your level is estimated as: {level}")