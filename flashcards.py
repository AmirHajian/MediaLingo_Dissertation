import re
import streamlit as st


def render_flashcards(definitions_text, nlp):

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
                    "ADV": "Adverb"
                }
                pos_label = pos_map.get(token.pos_, "")

            pairs.append((word, definition, pos_label))

    # ---------------------------
    # Step 3: Empty handling
    # ---------------------------
    if not pairs:
        st.warning("⚠️ No definitions detected. Please check lesson format.")
        return

    # ---------------------------
    # Step 4: Layout (Enhanced Visibility)
    # ---------------------------
    
    st.markdown("""
        <style>
        .flashcard-container {
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 12px;
            min-height: 190px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
        }

        /* FRONT STATE: High visibility border and subtle inner shadow */
        .card-front {
            background-color: rgba(255, 255, 255, 0.03); /* Very slight tint */
            border: 2px solid rgba(120, 120, 120, 0.4); /* Stronger gray border */
        }

        /* BACK STATE: Blue accent border as requested */
        .card-back {
            background-color: rgba(96, 165, 250, 0.05);
            border: 2px solid #60a5fa;
        }

        .flashcard-container:hover {
            transform: translateY(-5px); /* Lift effect */
            border-color: #60a5fa;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .card-pos {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #60a5fa; 
            text-align: right;
            margin-bottom: auto; /* Pushes POS to the very top */
        }

        .card-title {
            font-size: 24px;
            font-weight: 800;
            color: var(--text-color);
            margin-top: 10px;
        }

        .card-definition {
            font-size: 16px;
            line-height: 1.5;
            color: var(--text-color);
            margin-top: 12px;
        }

        .card-instruction {
            color: #888888;
            font-size: 12px;
            margin-top: auto; /* Pushes instruction to the bottom */
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(2)

    for i, (word, definition, pos) in enumerate(pairs):
        col = cols[i % 2]
        with col:
            key = f"flashcard_{i}"
            if key not in st.session_state:
                st.session_state[key] = False

            if not st.session_state[key]:
                # FRONT (Un-flipped)
                st.markdown(f"""
                <div class="flashcard-container card-front">
                    <div class="card-pos">{pos if pos else "VOCAB"}</div>
                    <div class="card-title">{word}</div>
                    <div class="card-instruction">Click 'Show Definition' to reveal</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("👁️ Show Definition", key=f"btn_{i}", use_container_width=True):
                    st.session_state[key] = True
                    st.rerun()
            else:
                # BACK (Flipped)
                st.markdown(f"""
                <div class="flashcard-container card-back">
                    <div class="card-pos">{pos if pos else "VOCAB"}</div>
                    <div class="card-title" style="color:#60a5fa;">{word}</div>
                    <div class="card-definition">{definition}</div>
                    <div class="card-instruction">Click 'Hide' to test again</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("↩️ Hide Definition", key=f"back_{i}", use_container_width=True):
                    st.session_state[key] = False
                    st.rerun()