"""Stage 04: check each draft reply. No AI involved.

Usage: python scripts/check_reply.py <run_id>
Prints OK <id> or BAD <id>: <reason>. Exit code 1 if any line is BAD.
"""
import re
import sys

from common import config, load_stage, routing
from detect_language import detect

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
PRIORITY_LABEL = re.compile(r"\bP[123]\b")


def sentence_count(text):
    return len([part for part in SENTENCE_SPLIT.split(text.strip()) if part])


def banned_hits(text, cfg):
    lowered = text.lower()
    hits = []
    for language in cfg["banned_phrases"]:
        hits += [phrase for phrase in cfg["banned_phrases"][language] if phrase in lowered]
    return sorted(set(hits))


def internal_words(text):
    found = [team for team in routing().values() if team.lower() in text.lower()]
    if PRIORITY_LABEL.search(text):
        found.append("a priority label")
    return found


def problems(item, cfg):
    found = []
    draft = item.get("draft")
    if not isinstance(draft, str) or not draft.strip():
        return ["draft is empty"]
    count = sentence_count(draft)
    if not 3 <= count <= 5:
        found.append(f"draft has {count} sentences, needs 3 to 5")
    if item.get("draft_language") != item.get("language") or detect(draft)[0] != item.get("language"):
        found.append(f"draft language does not match ticket language {item.get('language')}")
    hits = banned_hits(draft, cfg)
    if hits:
        found.append("banned promise phrase: " + ", ".join(hits))
    leaked = internal_words(draft)
    if leaked:
        found.append("internal words in draft: " + ", ".join(leaked))
    if item.get("status") != "waiting_for_approval":
        found.append("status must be waiting_for_approval")
    return found


def main():
    if len(sys.argv) != 2:
        print("usage: check_reply.py <run_id>")
        return 2
    cfg = config()
    bad = 0
    for item in load_stage(sys.argv[1], "04_reply.json"):
        found = problems(item, cfg)
        if found:
            bad += 1
            print(f"BAD {item.get('id')}: {'; '.join(found)}")
        else:
            print(f"OK {item['id']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
