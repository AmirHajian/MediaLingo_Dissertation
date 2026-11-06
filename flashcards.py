import re

import streamlit as st

_CSS = """
<style>
.ml-card {
    border-radius: 20px;
    padding: 22px 24px;
    min-height: 168px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.028));
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 18px 42px rgba(3, 6, 15, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(24px) saturate(160%);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.ml-card:hover {
    transform: translateY(-3px);
    border-color: rgba(76, 141, 255, 0.45);
}
.ml-card-back {
    background: linear-gradient(160deg, rgba(76, 141, 255, 0.22), rgba(111, 227, 255, 0.06));
    border-color: rgba(76, 141, 255, 0.4);
}
.ml-card-pos {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6FE3FF;
}
.ml-card-word {
    font-size: 23px;
    font-weight: 650;
    letter-spacing: -0.02em;
    line-height: 1.25;
    color: #FFFFFF;
}
.ml-card-def {
    font-size: 14.5px;
    line-height: 1.65;
    color: #E3E9F6;
}
.ml-card-hint {
    font-size: 12px;
    color: #96A3BE;
    font-style: italic;
    margin-top: auto;
}
</style>
"""


def render_flashcards(definitions_text, nlp):

    st.markdown(_CSS, unsafe_allow_html=True)

    lines = definitions_text.split("\n")
    pairs = []

    # ---------------------------
    # Step 1: Parse definitions
    # ---------------------------
    for line in lines:
        clean = line.strip()
        match = re.match(r"-\s*(.*?):\s*(.*)", clean)

        if match:
            word = match.group(1).strip()
            definition = match.group(2).strip()

            # ---------------------------
            # Step 2: POS / Phrase detection
            # ---------------------------
            doc = nlp(word)

            if len(doc) > 1:
                pos_label = "Phrase"
            else:
                token = doc[0]
                pos_map = {
                    "NOUN": "Noun",
                    "VERB": "Verb",
                    "ADJ": "Adjective",
                    "ADV": "Adverb",
                }
                pos_label = pos_map.get(token.pos_, "")

            pairs.append((word, definition, pos_label))

    # ---------------------------
    # Step 3: Empty handling
    # ---------------------------
    if not pairs:
        st.warning("No definitions were found in this lesson.")
        return

    # ---------------------------
    # Step 4: Layout
    # ---------------------------
    cols = st.columns(2)

    for i, (word, definition, pos) in enumerate(pairs):
        col = cols[i % 2]
        with col:
            key = f"flashcard_{i}"
            if key not in st.session_state:
                st.session_state[key] = False

            label = pos if pos else "Vocabulary"

            if not st.session_state[key]:
                st.markdown(
                    f'<div class="ml-card">'
                    f'<div class="ml-card-pos">{label}</div>'
                    f'<div class="ml-card-word">{word}</div>'
                    f'<div class="ml-card-hint">Select below to reveal the meaning</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if st.button("Show meaning", key=f"btn_{i}", use_container_width=True):
                    st.session_state[key] = True
                    st.rerun()
            else:
                st.markdown(
                    f'<div class="ml-card ml-card-back">'
                    f'<div class="ml-card-pos">{label}</div>'
                    f'<div class="ml-card-word">{word}</div>'
                    f'<div class="ml-card-def">{definition}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if st.button("Hide meaning", key=f"back_{i}", use_container_width=True):
                    st.session_state[key] = False
                    st.rerun()
