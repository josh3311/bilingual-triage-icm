"""After a person approves drafts, write only the approved ones to outbox.json. This does not send anything.

Usage: python scripts/export_approved.py <run_id>
Needs runs/<run_id>/approval.json, for example {"T001": "approved", "T002": "returned"}.
Refuses to run unless the audit verdict is PASS.
"""
import sys

from common import load_stage, run_dir, write_json


def main():
    if len(sys.argv) != 2:
        print("usage: export_approved.py <run_id>")
        return 2
    run_id = sys.argv[1]
    audit = load_stage(run_id, "05_audit.json")
    if audit.get("verdict") != "PASS":
        print("REFUSED the audit did not pass")
        return 1
    approval = load_stage(run_id, "approval.json")
    drafts = load_stage(run_id, "04_reply.json")
    outbox = [{"id": d["id"], "language": d["language"], "draft": d["draft"]}
              for d in drafts if approval.get(d["id"]) == "approved"]
    write_json(run_dir(run_id) / "outbox.json", outbox)
    returned = [i for i, v in approval.items() if v == "returned"]
    print(f"EXPORTED {len(outbox)} drafts")
    if returned:
        print(f"RETURNED to 04_reply: {', '.join(sorted(returned))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
