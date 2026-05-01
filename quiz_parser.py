import re

def extract_quiz_and_rest(text, num_questions=5):

    # Find all question starts
    matches = list(re.finditer(r"\d+\.\s", text))

    if not matches:
        return None, text

    question_spans = []

    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)

        block = text[start:end].strip()

        # keep ONLY real MCQ blocks
        if re.search(r"a\).*b\).*c\)", block, re.DOTALL):
            question_spans.append(block)

    # limit questions
    quiz_blocks = question_spans[:num_questions]

    # remove them from original text
    rest_text = text
    for qb in quiz_blocks:
        rest_text = rest_text.replace(qb, "")

    quiz_text = "\n\n".join(quiz_blocks)

    return quiz_text, rest_text


def parse_quiz(section_text):

    questions = []
    q_blocks = re.split(r"\n(?=\d+\.\s)", section_text)

    for block in q_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")

        question = lines[0].strip()
        options = []
        answer = None

        for line in lines[1:]:
            line = line.strip()

            if re.match(r"^[a-c]\)", line):
                options.append(line)

            if "answer:" in line.lower():
                answer = line.lower().split("answer:")[-1].strip()

        # FILTER BAD QUESTIONS
        if len(options) >= 2 and "quiz" not in question.lower():
            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })

    return questions