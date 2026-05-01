CEFR_LEVELS = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6
}

LEVELS = ["A1","A2","B1","B2","C1","C2"]

def level_distance(word_level, user_level):
    return abs(LEVELS.index(word_level) - LEVELS.index(user_level))


def score_word(word, word_level, profile, keywords):
    score = 0

    # word complexity
    score += len(word)

    # longer = harder
    if len(word) > 7:
        score += 2

    # topic relevance
    if any(word.lower() in k.lower() for k in keywords):
        score += 5

    # level matching (soft)
    distance = level_distance(word_level, profile["level"])
    if distance == 0:
        score += 4
    elif distance == 1:
        score += 2

    return score

def filter_vocabulary(vocab, profile, keywords):

    scored_vocab = []

    for item in vocab:
        # handle tuple or string
        if isinstance(item, tuple):
            word, word_level = item
        else:
            word = item
            word_level = profile["level"] 

        score = score_word(word, word_level, profile, keywords)
        scored_vocab.append((word, score))

    # sort by score (descending)
    scored_vocab.sort(key=lambda x: x[1], reverse=True)

    # return top 5 words
    return [w[0] for w in scored_vocab[:5]]
