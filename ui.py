"""Visual system for MediaLingo.

Everything presentational lives here: the palette, the glass surfaces and the
typography scale used by every screen. app.py only composes these pieces, so a
restyle never has to touch the lesson logic.
"""

import re
from html import escape

import streamlit as st

_CSS = """
<style>
:root {
    --brand: #4C8DFF;
    --brand-deep: #2A6BFF;
    --accent: #6FE3FF;
    --violet: #8B7BFF;
    --ink: #EDF1FB;
    --muted: #96A3BE;
    --stroke: rgba(255, 255, 255, 0.13);
    --stroke-soft: rgba(255, 255, 255, 0.07);
    --radius: 22px;
    --shadow: 0 20px 50px rgba(3, 6, 15, 0.5);
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
        "Inter", "Segoe UI", Roboto, sans-serif;
}

.stApp,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
.stApp button, .stApp [data-testid="stMarkdownContainer"] {
    font-family: var(--font);
}

.stApp {
    background:
        radial-gradient(1100px 720px at 6% -12%, rgba(42, 107, 255, 0.42), transparent 62%),
        radial-gradient(880px 620px at 96% -4%, rgba(111, 227, 255, 0.16), transparent 58%),
        radial-gradient(900px 900px at 52% 118%, rgba(139, 123, 255, 0.20), transparent 62%),
        #070A12;
    color: var(--ink);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
footer { visibility: hidden; }

.block-container {
    max-width: 1080px;
    padding: 2.6rem 2rem 5rem 2rem;
}

/* ---------- typography ---------- */
.ml-h2 {
    font-size: 30px;
    font-weight: 680;
    letter-spacing: -0.03em;
    margin: 0 0 8px 0;
    color: var(--ink);
}
.ml-h3 {
    font-size: 19px;
    font-weight: 650;
    letter-spacing: -0.02em;
    margin: 0 0 8px 0;
}
.ml-copy {
    font-size: 14.5px;
    line-height: 1.65;
    color: var(--muted);
    max-width: 66ch;
    margin: 0 0 8px 0;
}
.ml-eyebrow {
    font-size: 11.5px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--brand);
    margin: 0 0 6px 0;
}

/* ---------- brand ---------- */
.ml-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
}
.ml-brand-mark {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6FE3FF 0%, #4C8DFF 48%, #8B7BFF 100%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55),
        0 10px 24px rgba(76, 141, 255, 0.42);
}
.ml-brand-name {
    font-size: 19px;
    font-weight: 660;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.ml-brand-sub {
    font-size: 12.5px;
    color: var(--muted);
    letter-spacing: 0.01em;
}

/* ---------- sections ---------- */
.ml-section { margin: 30px 0 14px 0; }
.ml-section h3 {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #B9CCF0;
    margin: 0;
}
.ml-section p {
    font-size: 13.5px;
    color: var(--muted);
    margin: 6px 0 0 0;
}

/* ---------- glass ---------- */
.ml-glass,
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.11) 0%, rgba(255, 255, 255, 0.045) 58%, rgba(255, 255, 255, 0.02) 100%);
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(28px) saturate(170%);
    -webkit-backdrop-filter: blur(28px) saturate(170%);
}

/* ---------- stats ---------- */
.ml-stat-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 14px;
    margin: 18px 0 4px 0;
}
.ml-stat {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.115), rgba(255, 255, 255, 0.04));
    border: 1px solid var(--stroke);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(18px);
}
.ml-stat-value {
    font-size: 25px;
    font-weight: 660;
    letter-spacing: -0.03em;
    line-height: 1.15;
    background: linear-gradient(135deg, #FFFFFF 0%, #A8CAFF 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.ml-stat-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-top: 6px;
}

/* ---------- chips ---------- */
.ml-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 4px 0 6px 0;
}
.ml-chip {
    font-size: 13px;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(76, 141, 255, 0.12);
    border: 1px solid rgba(76, 141, 255, 0.28);
    color: #D9E5FF;
    letter-spacing: -0.005em;
}
.ml-chip-learned {
    background: transparent;
    border: 1px dashed rgba(255, 255, 255, 0.16);
    color: var(--muted);
    text-decoration: line-through;
}

/* ---------- quiz ---------- */
.ml-q { margin: 18px 0 8px 0; }
.ml-q-count {
    font-size: 10.5px;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--brand);
}
.ml-q p {
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 1.45;
    margin: 6px 0 0 0;
    color: var(--ink);
}
.ml-score {
    display: flex;
    align-items: baseline;
    gap: 14px;
    padding: 16px 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(76, 141, 255, 0.22), rgba(111, 227, 255, 0.07));
    border: 1px solid rgba(76, 141, 255, 0.34);
}
.ml-score-main {
    font-size: 28px;
    font-weight: 680;
    letter-spacing: -0.03em;
}
.ml-score-main span {
    font-size: 15px;
    color: var(--muted);
    font-weight: 600;
}
.ml-score-label {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #B9CCF0;
}

/* ---------- empty state ---------- */
.ml-empty {
    padding: 40px 26px;
    text-align: center;
    border-radius: 20px;
    border: 1px dashed rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.02);
    margin-top: 12px;
}
.ml-empty-title {
    font-weight: 650;
    font-size: 15px;
    margin-bottom: 6px;
    color: var(--ink);
}
.ml-empty p { color: var(--muted); font-size: 13.5px; margin: 0; }

/* ---------- lesson body ---------- */
.ml-body { padding: 28px 30px; }
.ml-body-h {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: var(--brand);
    font-weight: 700;
    margin: 24px 0 10px 0;
}
.ml-body-h:first-child { margin-top: 0; }
.ml-body-p {
    font-size: 15px;
    line-height: 1.75;
    margin: 0 0 10px 0;
    color: #E3E9F6;
}
.ml-body-li {
    font-size: 15px;
    line-height: 1.7;
    margin: 0 0 8px 0;
    padding-left: 18px;
    position: relative;
    color: #E3E9F6;
}
.ml-body-li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 9px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6FE3FF, #4C8DFF);
}

/* ---------- widgets ---------- */
.stButton > button,
[data-testid="stDownloadButton"] button {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.14), rgba(255, 255, 255, 0.05));
    color: var(--ink);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: -0.01em;
    padding: 0.62rem 1.1rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22), 0 10px 26px rgba(3, 6, 15, 0.3);
    transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: rgba(76, 141, 255, 0.55);
    box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.26);
    transform: translateY(-1px);
    color: #FFFFFF;
}
.stButton > button:active { transform: translateY(0); }

.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #5C99FF 0%, #2A6BFF 55%, #6FE3FF 100%);
    border: 1px solid rgba(255, 255, 255, 0.24);
    color: #FFFFFF;
    font-weight: 680;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4), 0 14px 34px rgba(42, 107, 255, 0.35);
}
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45), 0 16px 40px rgba(42, 107, 255, 0.45);
}

[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.045) !important;
    border: 1px solid var(--stroke-soft) !important;
    border-radius: 14px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    color: var(--ink) !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: rgba(76, 141, 255, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.14) !important;
}
.stTextInput input, .stTextArea textarea {
    background: transparent !important;
    color: var(--ink) !important;
    font-size: 14.5px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: rgba(150, 163, 190, 0.75) !important;
}
.stSelectbox label p, .stTextInput label p, .stTextArea label p {
    font-size: 12px !important;
    letter-spacing: 0.02em !important;
    color: #B9CCF0 !important;
    font-weight: 600 !important;
}

[data-testid="stRadioGroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 7px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid var(--stroke-soft);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px) saturate(150%);
    width: 100%;
    justify-content: center;
}
[data-testid="stRadioOption"] {
    margin: 0;
    padding: 9px 20px;
    border-radius: 11px;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    transition: background 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
}
[data-testid="stRadioOption"] > div > div:first-child { display: none !important; }
[data-testid="stRadioOption"]:hover { background: rgba(255, 255, 255, 0.07); }
[data-testid="stRadioOption"]:has(input:checked) {
    background: linear-gradient(180deg, rgba(76, 141, 255, 0.38), rgba(42, 107, 255, 0.18));
    border-color: rgba(76, 141, 255, 0.55);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22), 0 6px 18px rgba(42, 107, 255, 0.26);
}
[data-testid="stRadioOption"] p {
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: -0.005em;
    color: #C9D6EE;
}
[data-testid="stRadioOption"]:has(input:checked) p { color: #FFFFFF; }

[data-testid="stExpander"] details {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid var(--stroke-soft);
    border-radius: 16px;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-size: 13.5px;
    font-weight: 600;
    color: #D5DFF3;
}
[data-testid="stExpander"] summary:hover { color: #FFFFFF; }

[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid var(--stroke-soft) !important;
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(14px);
}
[data-testid="stAlert"] p { font-size: 13.5px; }

[data-testid="stToast"] {
    background: rgba(12, 17, 28, 0.92);
    border: 1px solid var(--stroke);
    border-radius: 14px;
    backdrop-filter: blur(20px);
}
[data-testid="stToast"] p { font-size: 13.5px; color: var(--ink); }

hr {
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin: 26px 0 !important;
}

[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--muted) !important;
    font-size: 12.5px !important;
}

[data-testid="stSpinner"] p { color: var(--muted); font-size: 13.5px; }
</style>
"""


def inject_styles():
    st.markdown(_CSS, unsafe_allow_html=True)


def brand_header(subtitle="Personalised English lessons from any media"):
    st.markdown(
        '<div class="ml-brand">'
        '<div class="ml-brand-mark"></div>'
        f'<div><div class="ml-brand-name">MediaLingo</div>'
        f'<div class="ml-brand-sub">{escape(subtitle)}</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def section(title, caption=None):
    html = f'<div class="ml-section"><h3>{escape(title)}</h3>'
    if caption:
        html += f"<p>{escape(caption)}</p>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def stats(items):
    cells = []
    for value, label in items:
        shown = "—" if value in (None, "") else str(value)
        cells.append(
            '<div class="ml-stat">'
            f'<div class="ml-stat-value">{escape(shown)}</div>'
            f'<div class="ml-stat-label">{escape(label)}</div>'
            "</div>"
        )
    st.markdown(f'<div class="ml-stat-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def chips(items, learned=()):
    learned = set(learned)
    cells = []
    for item in items:
        extra = " ml-chip-learned" if item in learned else ""
        cells.append(f'<span class="ml-chip{extra}">{escape(str(item))}</span>')
    if cells:
        st.markdown(f'<div class="ml-chip-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def question_label(index, total, text):
    st.markdown(
        f'<div class="ml-q"><span class="ml-q-count">Question {index} of {total}</span>'
        f"<p>{escape(text)}</p></div>",
        unsafe_allow_html=True,
    )


def score(correct, total):
    st.markdown(
        f'<div class="ml-score">'
        f'<div class="ml-score-main">{correct}<span> / {total}</span></div>'
        f'<div class="ml-score-label">Correct answers</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def empty(title, body):
    st.markdown(
        f'<div class="ml-empty"><div class="ml-empty-title">{escape(title)}</div>'
        f"<p>{escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def lesson_body(text):
    """Render generated lesson markdown as structured glass typography."""
    parts = []

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue

        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        line = re.sub(r"_{3,}", "______", line)

        if line in {"—", "-", "•", "• —"}:
            continue

        safe = escape(line)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)

        lower = line.lower()
        is_heading = len(line) < 64 and any(
            word in lower
            for word in ("definition", "example", "practice", "writing task")
        )

        if is_heading:
            parts.append(f'<h4 class="ml-body-h">{safe}</h4>')
        elif line.startswith(("-", "•")):
            parts.append(f'<p class="ml-body-li">{safe.lstrip("-•").strip()}</p>')
        else:
            parts.append(f'<p class="ml-body-p">{safe}</p>')

    if parts:
        st.markdown(
            '<div class="ml-glass ml-body">' + "".join(parts) + "</div>",
            unsafe_allow_html=True,
        )
