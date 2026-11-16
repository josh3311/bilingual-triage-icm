"""Stage 04: look up what the records say about each ticket. No AI involved.
Usage: python scripts/lookup_records.py <run_id>
Writes runs/<run_id>/04_lookup.json. A ticket with no customer record gets needs_human set to true.
"""
import sys

from common import load_stage, run_dir, write_json
from records import build_db, find_facts


def lookup_all(items, db):
    out = []
    for item in items:
        facts = find_facts(item, db)
        flagged = facts["status"] == "not_found"
        out.append({**item, "facts": facts, "lookup_status": facts["status"],
                    "needs_human": True if flagged else item["needs_human"],
                    "status": "looked_up"})
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: lookup_records.py <run_id>")
        return 2
    run_id = sys.argv[1]
    result = lookup_all(load_stage(run_id, "03_route.json"), build_db())
    for item in result:
        f = item["facts"]
        order = f["order"]["id"] if f["order"] else "no order"
        print(f"{item['id']} {item['lookup_status']} customer={'yes' if f['customer'] else 'NO'} order={order} charges={len(f['charges'])} policy={f['policy']['topic'] if f['policy'] else 'none'}")
    write_json(run_dir(run_id) / "04_lookup.json", result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
