import time
import re


def reverse_per_word(text: str) -> str:
    return " ".join(word[::-1] for word in text.split())


def safe_sleep(duration: float, check_interval: float = 0.01):
    if duration <= 0:
        return
    start = time.time()
    while time.time() - start < duration:
        time.sleep(check_interval)


def strip_minecraft_formatting(s: str) -> str:
    s = re.sub(r"§.", "", s)
    s = re.sub(r"[\x00-\x1f\x7f]", "", s)
    return s.strip()


def hard_normalize(s: str) -> str:
    s = re.sub(r"§.", "", s)
    s = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", s)
    s = re.sub(r"[^A-Za-z0-9 ]", "", s)
    return s.strip()


def normalize_quotes(s: str) -> str:
    return s.replace("’", "'").replace("`", "'").replace("‘", "'")


def normalize_word(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def normalize_letters(s: str):
    return sorted(re.sub(r"[^a-z]", "", s.lower()))


def same_letters(a: str, b: str) -> bool:
    clean = lambda s: re.sub(r"[^a-z]", "", s.lower())
    return sorted(clean(a)) == sorted(clean(b))
