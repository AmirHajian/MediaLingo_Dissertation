from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def extract_domain_keywords(text):
    prompt = f"""
    Analyse the following text and extract:

    1. Main topic (1 short phrase)
    2. 5–10 important domain-specific keywords

    Text:
    {text}

    Return in this exact format:
    Topic: ...
    Keywords: word1, word2, word3
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content

    # Parse output
    topic = ""
    keywords = []

    for line in content.split("\n"):
        if line.lower().startswith("topic:"):
            topic = line.split(":", 1)[1].strip()
        elif line.lower().startswith("keywords:"):
            keywords = [k.strip().lower() for k in line.split(":", 1)[1].split(",")]

    return topic, keywords

