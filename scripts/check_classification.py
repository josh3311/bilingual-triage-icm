"""Stage 02: check the skill's answers are allowed values. No AI involved.

Usage: python scripts/check_classification.py <run_id>
Prints OK <id> or BAD <id>: <reason>. Exit code 1 if any line is BAD.
"""
import sys

from common import config, load_stage


def problems(item, intake_ids, cfg):
    found = []
    if item.get("id") not in intake_ids:
        found.append("id does not match an intake ticket")
    if item.get("category") not in cfg["categories"]:
        found.append(f"category {item.get('category')!r} is not allowed")
    if item.get("priority") not in cfg["priorities"]:
        found.append(f"priority {item.get('priority')!r} is not allowed")
    if not isinstance(item.get("needs_human"), bool):
        found.append("needs_human must be true or false")
    reason = item.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        found.append("reason is empty")
    return found


def main():
    if len(sys.argv) != 2:
        print("usage: check_classification.py <run_id>")
        return 2
    run_id = sys.argv[1]
    cfg = config()
    intake_ids = {t["id"] for t in load_stage(run_id, "01_intake.json")}
    items = load_stage(run_id, "02_classify.json")
    bad = 0
    seen = set()
    for item in items:
        found = problems(item, intake_ids, cfg)
        if item.get("id") in seen:
            found.append("duplicate id")
        seen.add(item.get("id"))
        if found:
            bad += 1
            print(f"BAD {item.get('id')}: {'; '.join(found)}")
        else:
            print(f"OK {item['id']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
