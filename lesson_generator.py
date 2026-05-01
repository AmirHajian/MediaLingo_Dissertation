# lesson_generator.py

from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def generate_lesson(vocab, level):
    num_questions = 3 if len(vocab) < 3 else 5  
    prompt = f"""
    You are an English teacher creating a structured lesson.
    Learner level: {level}
    Vocabulary: {vocab}
    Format the lesson clearly using Markdown:
    ## Pre-Lesson Quiz
    - Exactly {num_questions} multiple choice questions
    Always include the correct answer for each question in the format:
    Answer: a
    ## 1. Definitions
    - Word: Definition
    ## 2. Examples
    - Example sentence for each word
    ## 3. Practice
    - Create {num_questions} fill-in-the-blank sentences
    - Use "______" for blanks (not dashes or symbols)
    - Do NOT create empty bullet points
    ## 4. Writing Task (Do not include examples here)
    Keep it simple and engaging.
    Do not use bold formatting (** **) in the output.
    """



    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content 