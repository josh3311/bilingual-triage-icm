"""Stage 01: validate every ticket, tag the language, write the handover files.

Usage: python scripts/run_intake.py <run_id> [tickets.json]
Writes runs/<run_id>/00_input.json, 01_intake.json and 01_rejected.json, then prints the count check.
"""
import sys

from common import DATA, load_json, run_dir, write_json
from detect_language import detect
from validate_ticket import validate_all


def main():
    if len(sys.argv) < 2:
        print("usage: run_intake.py <run_id> [tickets.json]")
        return 2
    run_id = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else DATA / "sample_tickets.json"
    tickets = load_json(source)
    valid, rejected = validate_all(tickets)

    kept = []
    for ticket in valid:
        language, confidence = detect(ticket["subject"] + " " + ticket["body"])
        kept.append({**ticket, "language": language, "language_confidence": confidence, "status": "intake_ok"})
        print(f"{ticket['id']} {language} ({confidence})")
    for item in rejected:
        print(f"REJECTED {item['id']}: {item['reason']}")

    folder = run_dir(run_id)
    write_json(folder / "00_input.json", tickets)
    write_json(folder / "01_intake.json", kept)
    write_json(folder / "01_rejected.json", rejected)

    total, ok = len(tickets), len(kept) + len(rejected)
    if total == ok:
        print(f"COUNT OK {total} = {len(kept)} + {len(rejected)}")
        return 0
    print(f"COUNT FAIL {total} != {len(kept)} + {len(rejected)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
