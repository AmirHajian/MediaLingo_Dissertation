from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def generate_pdf(lesson_text, level, score_text, quiz_data=None, file_path="lesson.pdf"):

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    # Header
    content.append(Paragraph("<b>AI English Lesson</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"<b>Level:</b> {level}", styles["Normal"]))
    content.append(Paragraph(f"<b>Quiz Score:</b> {score_text}", styles["Normal"]))
    content.append(Spacer(1, 20))

    # Quiz Section
    if quiz_data:
        content.append(Paragraph("<b>Pre-Lesson Quiz</b>", styles["Heading2"]))
        content.append(Spacer(1, 12))

        for i, q in enumerate(quiz_data):
            content.append(Paragraph(f"<b>Q{i+1}:</b> {q['question']}", styles["Normal"]))
            content.append(Spacer(1, 6))

            for opt in q["options"]:
                content.append(Paragraph(opt, styles["Normal"]))

            content.append(Spacer(1, 4))

            # show user + correct
            def extract_letter(ans):
                if not ans:
                    return "N/A"
                return ans.strip()[0].lower()

            user_ans = extract_letter(q.get("user"))
            correct_ans = extract_letter(q.get("correct"))

            content.append(Paragraph(f"Your answer: {user_ans}", styles["Normal"]))
            content.append(Paragraph(f"Correct answer: {correct_ans}", styles["Normal"]))

            content.append(Spacer(1, 10))

        content.append(PageBreak())

    # 📘 LESSON CONTENT
    content.append(Paragraph("<b>Lesson Content</b>", styles["Heading2"]))
    content.append(Spacer(1, 15))

    import re
    lines = lesson_text.split("\n")

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        # clean formatting
        clean = re.sub(r"^#+\s*", "", clean)
        clean = re.sub(r"^\d+\.\s*", "", clean)

        lower = clean.lower()

        # section headers
        if any(word in lower for word in [
            "definition", "example", "practice", "writing"
        ]):
            content.append(Spacer(1, 15))
            content.append(Paragraph(f"<b>{clean}</b>", styles["Heading2"]))
            content.append(Spacer(1, 10))

        elif clean.startswith("-"):
            content.append(Paragraph(f"• {clean[1:].strip()}", styles["Normal"]))
            content.append(Spacer(1, 6))

        else:
            content.append(Paragraph(clean, styles["Normal"]))
            content.append(Spacer(1, 8))

    doc.build(content)

    return file_path