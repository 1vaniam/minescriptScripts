import time
import re

import config
from logger import debug_log
from words import WORDS, WORDS_LOWER, phrase_in_dict
from utils import (
    safe_sleep,
    strip_minecraft_formatting,
    reverse_per_word,
)


IGNORE_PATTERNS = [
    re.compile(r"range of \d+-\d+"),
    re.compile(r"You have 20 seconds to '✗'!"),
]

def handle_ignore(msg):
    for pat in IGNORE_PATTERNS:
        if pat.search(msg.strip()):
            return True
    return False


def handle_unreverse(msg):
    stripped_msg = msg.strip()

    if "unreverse the letters to win" in stripped_msg.lower():
        config.WAITING_UNREVERSE = True
        config.UNREVERSE_TIME = time.time()
        return ""

    if not config.WAITING_UNREVERSE:
        return None

    if time.time() - config.UNREVERSE_TIME > 3:
        config.WAITING_UNREVERSE = False
        return ""

    config.WAITING_UNREVERSE = False

    cand_per_word = reverse_per_word(msg)
    cand_whole = msg[::-1]

    debug_log(f"[Unreverse] cand_per_word='{cand_per_word}'")
    debug_log(f"[Unreverse] cand_whole='{cand_whole}'")

    if phrase_in_dict(cand_per_word):
        return cand_per_word

    return cand_whole


def handle_unscramble(msg):
    stripped_msg = msg.strip()

    if "unscramble the letters to win" in stripped_msg.lower():
        config.WAITING_UNSCRAMBLE = True
        config.UNSCRAMBLE_TIME = time.time()
        debug_log("[Unscramble] Triggered")
        return ""

    if not config.WAITING_UNSCRAMBLE:
        return None

    if time.time() - config.UNSCRAMBLE_TIME > 3:
        config.WAITING_UNSCRAMBLE = False
        debug_log("[Unscramble] Timeout")
        return ""

    config.WAITING_UNSCRAMBLE = False

    scrambled_words = stripped_msg.split()
    lengths = [len(w) for w in scrambled_words]
    joined_scrambled = "".join(scrambled_words).lower()

    debug_log(f"[Unscramble] joined='{joined_scrambled}', lengths={lengths}")

    candidates = [
        w for w in WORDS
        if sorted(re.sub(r"[^a-z]", "", w.lower()))
        == sorted(re.sub(r"[^a-z]", "", joined_scrambled))
    ]

    for cand in candidates:
        cand_clean = re.sub(r"[^a-zA-Z0-9]", "", cand)
        if len(cand_clean) != sum(lengths):
            continue

        idx = 0
        parts = []
        for l in lengths:
            parts.append(cand_clean[idx:idx + l])
            idx += l

        result = " ".join(parts)
        debug_log(f"[Unscramble] Match: {result}")
        return result

    debug_log("[Unscramble] No match")
    return None


def handle_fill_gaps(msg):
    clean = strip_minecraft_formatting(msg).strip()

    if clean.lower() == "fill the gaps to win!":
        config.WAITING_FILL_GAPS = True
        config.FILL_GAPS_TIME = time.time()
        return ""

    if not config.WAITING_FILL_GAPS:
        return None

    if time.time() - config.FILL_GAPS_TIME > 3:
        config.WAITING_FILL_GAPS = False
        return ""

    config.WAITING_FILL_GAPS = False

    regex_pattern = "^" + "".join(
        "." if c == "_" else re.escape(c)
        for c in clean
    ) + "$"

    regex = re.compile(regex_pattern, re.IGNORECASE)
    debug_log(f"[FillGaps] Regex: {regex_pattern}")

    for phrase in WORDS:
        phrase_clean = strip_minecraft_formatting(phrase).strip()
        if regex.fullmatch(phrase_clean):
            debug_log(f"[FillGaps] Match: {phrase_clean}")
            return phrase_clean

    debug_log("[FillGaps] No match")
    return None

def handle_math(msg):
    stripped_msg = msg.strip()

    if stripped_msg.lower() == "solve the math equation to win!":
        config.WAITING_MATH = True
        config.MATH_TIME = time.time()
        debug_log("[Math] Triggered")
        return ""

    if not config.WAITING_MATH:
        return None

    if time.time() - config.MATH_TIME > 3:
        config.WAITING_MATH = False
        debug_log("[Math] Timeout")
        return ""

    expr = msg.replace("x", "*").replace("X", "*").replace("×", "*").strip()

    if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
        config.WAITING_MATH = False
        return None

    try:
        result = eval(expr)
        config.WAITING_MATH = False
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        debug_log(f"[Math] Result: {result}")
        return str(result)
    except Exception as e:
        config.WAITING_MATH = False
        debug_log(f"[Math] Error: {e}")
        return None

TRIVIA_ANSWERS = {
    r"In which major update were netherite items added?": "1.16",
    r"How many dimensions are in minecraft?": "3",
    r"What is the ingame name of the creator of minecraft?": "Notch",
}

COMPILED_TRIVIA = [
    (re.compile(pat.lower()), ans)
    for pat, ans in TRIVIA_ANSWERS.items()
]

def handle_trivia(msg):
    lower = msg.strip().lower()
    for pat, ans in COMPILED_TRIVIA:
        if pat.search(lower):
            return ans
    return None

def handle_underscore_word(msg):
    m = re.search(r"You have\s+\d+\s+seconds\s+to\s+'([A-Za-z_]+)'", msg.strip())
    if not m:
        return None

    pattern = m.group(1).lower()

    for word in WORDS:
        if len(word) == len(pattern):
            if all(p == "_" or p == w.lower() for p, w in zip(pattern, word.lower())):
                return word
    return None


def handle_quoted_word(msg):
    m = re.search(r"You have\s+\d+\s+seconds\s+to\s+'([^']+)'", msg.strip())
    return m.group(1).strip() if m else None


def handle_keyword(msg):
    m = re.search(r"You have\s+\d+\s+seconds\s+to\s+(.+?)[!']?$", msg.strip())
    if not m:
        return None

    return WORDS_LOWER.get(m.group(1).lower())
