import os

def load_words(filename="words.txt"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)

    words = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip()
                if w:
                    words.add(w)
    except FileNotFoundError:
        
        return set()

    return words


WORDS = load_words()
WORDS_LOWER = {w.lower(): w for w in WORDS}


def phrase_in_dict(phrase: str) -> bool:
    return all(w.lower() in WORDS_LOWER for w in phrase.split())
