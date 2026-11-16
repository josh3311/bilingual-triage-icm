"""Shared helpers for the triage scripts. Standard library only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RUNS = ROOT / "runs"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def config():
    return load_json(DATA / "categories.json")


def routing():
    return load_json(DATA / "routing_table.json")


def language_words():
    return load_json(DATA / "language_words.json")


def run_dir(run_id):
    return RUNS / run_id


def load_stage(run_id, name):
    path = run_dir(run_id) / name
    if not path.exists():
        print(f"MISSING {path.relative_to(ROOT)}")
        sys.exit(1)
    return load_json(path)


def mulberry32(seed):
    """Small seeded random generator. The website uses the same one, so both pick the same sample."""
    mask = 0xFFFFFFFF
    state = seed & mask

    def rnd():
        nonlocal state
        state = (state + 0x6D2B79F5) & mask
        t = ((state ^ (state >> 15)) * (1 | state)) & mask
        t = (((t + (((t ^ (t >> 7)) * (61 | t)) & mask)) & mask) ^ t) & mask
        return ((t ^ (t >> 14)) & mask) / 4294967296

    return rnd


def seeded_sample(ids, size, seed):
    ids = sorted(ids)
    rnd = mulberry32(seed)
    for i in range(len(ids) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        ids[i], ids[j] = ids[j], ids[i]
    return ids[:size]
