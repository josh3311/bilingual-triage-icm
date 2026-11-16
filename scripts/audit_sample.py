"""Stage 06: audit a fixed sample of tickets end to end. No AI involved.

Usage: python scripts/audit_sample.py <run_id>
Picks 20 tickets with seed 42, runs 8 checks on each, prints AUDIT PASS or AUDIT FAIL and writes 06_audit.json.
PASS needs every sampled ticket to pass every check.
"""
import sys

from check_reply import banned_hits, internal_words
from common import config, load_stage, routing, run_dir, seeded_sample, write_json
from detect_language import detect
from grounding import problems as grounding_problems

# Which stage to fix when a check fails.
STAGE_FOR_CHECK = {1: "01_intake", 2: "02_classify", 3: "02_classify", 4: "03_route", 5: "05_reply", 6: "05_reply", 7: "05_reply", 8: "05_reply"}


def failed_checks(ticket, cfg, table):
    failed = []
    if ticket.get("language") not in cfg["languages"]:
        failed.append(1)
    if ticket.get("category") not in cfg["categories"]:
        failed.append(2)
    if ticket.get("priority") not in cfg["priorities"]:
        failed.append(3)
    if table.get(ticket.get("category")) != ticket.get("team"):
        failed.append(4)
    draft = ticket.get("draft") or ""
    if not draft.strip() or detect(draft)[0] != ticket.get("language") or ticket.get("draft_language") != ticket.get("language"):
        failed.append(5)
    if banned_hits(draft, cfg) or internal_words(draft):
        failed.append(6)
    if ticket.get("status") != "waiting_for_approval":
        failed.append(7)
    if grounding_problems(ticket):
        failed.append(8)
    return failed


def audit(tickets, cfg, table):
    ids = [t["id"] for t in tickets]
    sampled = seeded_sample(ids, min(cfg["sample_size"], len(ids)), cfg["sample_seed"])
    by_id = {t["id"]: t for t in tickets}
    results = []
    for ticket_id in sampled:
        failed = failed_checks(by_id[ticket_id], cfg, table)
        results.append({"id": ticket_id, "passed": not failed, "failed_checks": failed})
    passed = sum(1 for r in results if r["passed"])
    return {"sample_size": len(sampled), "seed": cfg["sample_seed"], "sampled_ids": sampled,
            "results": results, "passed_count": passed,
            "verdict": "PASS" if passed == len(sampled) else "FAIL"}


def main():
    if len(sys.argv) != 2:
        print("usage: audit_sample.py <run_id>")
        return 2
    run_id = sys.argv[1]
    cfg, table = config(), routing()
    result = audit(load_stage(run_id, "05_reply.json"), cfg, table)
    for r in result["results"]:
        if r["passed"]:
            print(f"{r['id']} PASS")
        else:
            stages = sorted({STAGE_FOR_CHECK[c] for c in r["failed_checks"]})
            print(f"{r['id']} FAIL checks {r['failed_checks']} -> fix {', '.join(stages)}")
    write_json(run_dir(run_id) / "06_audit.json", {"run_id": run_id, **result})
    print(f"AUDIT {result['verdict']} {result['passed_count']}/{result['sample_size']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
