"""Stage 01: tag a text as EN or FR by counting common words. No AI involved.

Usage: python scripts/detect_language.py "some text"
"""
import re
import sys

from common import language_words

TOKEN = re.compile(r"[a-zà-ÿœ]+(?:['’][a-zà-ÿœ]+)?")
ACCENT = re.compile(r"[à-ÿœ]")
APOSTROPHE = re.compile(r"['’]")


def score(text):
    words = language_words()
    fr_words = set(words["fr_words"])
    en_words = set(words["en_words"])
    elision = set(words["fr_elision"])
    fr = en = 0
    for token in TOKEN.findall(text.lower()):
        parts = APOSTROPHE.split(token)
        if len(parts) == 2 and parts[0] in elision:
            fr += 1
            parts = parts[1:]
        for part in parts:
            if part in fr_words:
                fr += 1
            elif part in en_words:
                en += 1
        if ACCENT.search(token):
            fr += 1
    return fr, en


def detect(text):
    """Return (language, confidence). A tie gives EN with low confidence."""
    fr, en = score(text)
    if fr > en:
        language = "FR"
    elif en > fr:
        language = "EN"
    else:
        return "EN", "low"
    return language, ("high" if abs(fr - en) >= 2 else "low")


if __name__ == "__main__":
    text = " ".join(sys.argv[1:])
    print(*detect(text))
