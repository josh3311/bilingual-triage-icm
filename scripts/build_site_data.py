"""Bundle one recorded run plus the rules into docs/data/run.json for the website. No AI involved.
Usage: python scripts/build_site_data.py <run_id>
"""
import sys
from common import ROOT, config, language_words, load_json, load_stage, routing, run_dir, write_json

STAGES = ["01_intake", "02_classify", "03_route", "04_lookup", "05_reply", "06_audit"]


def build(run_id):
    reply = load_stage(run_id, "05_reply.json")
    audit = load_stage(run_id, "06_audit.json")
    return {
        "run_id": run_id,
        "config": config(),
        "routing": routing(),
        "words": language_words(),
        "tickets": load_json(ROOT / "data" / "sample_tickets.json"),
        "records": load_json(ROOT / "data" / "records.json"),
        "classify": {t["id"]: {k: t[k] for k in ("category", "priority", "needs_human", "reason")}
                     for t in load_stage(run_id, "02_classify.json")},
        "replies": {t["id"]: t["draft"] for t in reply},
        "python_audit": audit,
        "contexts": {s: (ROOT / s / "CONTEXT.md").read_text(encoding="utf-8") for s in STAGES},
        "skills": {name: (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                   for name in ("triage-ticket", "draft-reply")},
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: build_site_data.py <run_id>")
        sys.exit(2)
    write_json(ROOT / "docs" / "data" / "run.json", build(sys.argv[1]))
    print("WROTE docs/data/run.json")
