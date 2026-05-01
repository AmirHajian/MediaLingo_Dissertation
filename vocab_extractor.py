# vocab_extractor.py

from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import dot
from numpy.linalg import norm
from wordfreq import zipf_frequency

# ---------------------------
# Utility: Cosine Similarity
# ---------------------------
def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))


# ---------------------------
# Difficulty Estimation (CEFR proxy via Zipf)
# ---------------------------
def estimate_difficulty(word, lang='en'):
    word = word.strip()
    freq = zipf_frequency(word, lang)

    # slight normalisation for short words
    if len(word) < 9:
        freq += 0.2
    # heuristic fallbacks 
    if freq == 0:
        if len(word) <= 3:
            return "A1"
        elif len(word) <= 5:
            return "A2"
        elif len(word) <= 8:
            return "B1"
        elif len(word) <= 10:
            return "B2"
        elif len(word) <= 12:
            return "C1"
        else:
            return "C2"
    
    if freq > 6:
        return "A1"
    elif freq > 5.3:
        return "A2"
    elif freq > 4.7:
        return "B1"
    elif freq > 4:
        return "B2"
    elif freq > 3.2:
        return "C1"
    else:
        return "C2"


# ---------------------------
# Filters
# ---------------------------
BLACKLIST = {"sir", "thing", "something", "anything", "everything", "new"}

COMMON_WORDS = {
    "the", "is", "and", "to", "of", "in", "it", "that",
    "for", "on", "with", "as", "by", "at", "from"
}

LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


# ---------------------------
# Phrase Difficulty (hardest word defines phrase)
# ---------------------------
def phrase_difficulty(phrase):
    levels = [estimate_difficulty(w) for w in phrase.split()]
    return max(levels, key=lambda x: LEVEL_MAP[x])


# ---------------------------
# Main Function
# ---------------------------
def extract_vocabulary(text, domain_keywords, level, nlp, top_n=10):

    # --- Step 1: TF-IDF ---
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    word_scores = dict(zip(feature_names, scores))
    DOMAIN_BOOST = set(domain_keywords or [])

    # --- Step 2: spaCy ---
    doc = nlp(text)
    doc_vector = doc.vector

    candidates = []

    # ---------------------------
    # Step 2A: Noun Chunks
    # ---------------------------
    chunks = []

    for chunk in doc.noun_chunks:
        tokens = [t for t in chunk if not t.is_stop and not t.is_punct]

        if len(tokens) != 2:
            continue

        if not any(t.pos_ == "NOUN" for t in tokens):
            continue

        phrase = " ".join([t.lemma_.lower() for t in tokens])

        if len(phrase) < 5:
            continue

        chunks.append(phrase)

    chunks = sorted(set(chunks), key=len, reverse=True)

    for phrase in chunks:
        difficulty = phrase_difficulty(phrase)
        dist = abs(LEVEL_MAP[difficulty] - LEVEL_MAP[level])

        if dist > 1:
            continue

        # base score
        score = 0.6

        # domain relevance
        if any(word in phrase for word in DOMAIN_BOOST):
            score *= 1.6

        # CEFR alignment
        if dist == 0:
            score *= 1.8
        elif dist == 1:
            score *= 1.3

        candidates.append((phrase, score))

    # ---------------------------
    # Step 2B: Tokens
    # ---------------------------
    for token in doc:
        word = token.lemma_.lower()

        if (
            word in word_scores and
            not token.is_stop and
            not token.is_punct and
            token.pos_ in ["NOUN", "VERB", "ADJ"] and
            word not in BLACKLIST and
            len(word) > 3
        ):
            # remove named entities
            if token.ent_type_:
                continue

            score = word_scores[word]

            # penalise overly simple words
            if word in ["good", "bad", "big", "small", "very", "happy", "sad"]:
                score *= 0.5

            if len(word) <= 4:
                score *= 0.85

            # POS weighting
            if token.pos_ == "VERB":
                score *= 1.2
            elif token.pos_ == "NOUN":
                score *= 1.1

            # domain boost
            if any(word in k.lower() for k in DOMAIN_BOOST):
                score *= 1.6

            # semantic centrality
            if token.has_vector and doc_vector is not None:
                sim = cosine_similarity(token.vector, doc_vector)
                if sim < 0.2:
                    continue
                score *= (1 + sim * 0.4)

            # CEFR alignment
            difficulty = estimate_difficulty(word)
            dist = abs(LEVEL_MAP[difficulty] - LEVEL_MAP[level])

            if dist > 1:
                continue
            if dist == 0:
                score *= 1.7
            elif dist == 1:
                score *= 1.25

            # encourage harder vocab at higher levels
            if level in ["C1", "C2"]:
                if LEVEL_MAP[difficulty] >= 5:
                    score *= 1.4
                elif LEVEL_MAP[difficulty] <= 3:
                    score *= 0.7

            candidates.append((word, score))

    # ---------------------------
    # Step 3: Deduplication
    # ---------------------------
    seen = set()
    unique_candidates = []

    for word, score in candidates:
        if word not in seen:
            unique_candidates.append((word, score))
            seen.add(word)

    sorted_words = sorted(unique_candidates, key=lambda x: x[1], reverse=True)

    # ---------------------------
    # Step 4: Overlap Removal
    # ---------------------------
    final_candidates = []

    for word, score in sorted_words:
        words = set(word.split())
        skip = False

        for existing, _ in final_candidates:
            if words & set(existing.split()):
                skip = True
                break

        if not skip:
            final_candidates.append((word, score))

    # ---------------------------
    # Step 5: Balanced Selection
    # ---------------------------
    chunk_limit = max(1, top_n // 3)
    word_limit = top_n - chunk_limit

    filtered_words = []
    chunk_count = 0
    word_count = 0

    for word, score in final_candidates:
        if word.lower() in COMMON_WORDS or word.strip() in ["", "-", "—", "_"]:
            continue

        is_chunk = " " in word

        if is_chunk and chunk_count < chunk_limit:
            filtered_words.append(word)
            chunk_count += 1
        elif not is_chunk and word_count < word_limit:
            filtered_words.append(word)
            word_count += 1

        if len(filtered_words) >= top_n:
            break

    # ---------------------------
    # Step 6: Cleanup + Output
    # ---------------------------
    clean_output = []
    for word in filtered_words:
        word = " ".join(word.strip().split())
        clean_output.append(word)

    return [(word, phrase_difficulty(word)) for word in clean_output]