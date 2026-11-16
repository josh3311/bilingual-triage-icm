"""Stage 03: send each ticket to exactly one team using data/routing_table.json. No AI involved.

Usage: python scripts/route_ticket.py <run_id>
Writes runs/<run_id>/03_route.json. If any category is missing from the table it stops and writes nothing.
"""
import sys

from common import load_stage, routing, run_dir, write_json


def route_all(items, table):
    """Return (routed, unknown_ids). Never guesses a team."""
    routed, unknown = [], []
    for item in items:
        team = table.get(item.get("category"))
        if team is None:
            unknown.append(item.get("id"))
            continue
        routed.append({**item, "team": team, "urgent": item.get("priority") == "P1", "status": "routed"})
    return routed, unknown


def main():
    if len(sys.argv) != 2:
        print("usage: route_ticket.py <run_id>")
        return 2
    run_id = sys.argv[1]
    routed, unknown = route_all(load_stage(run_id, "02_classify.json"), routing())
    if unknown:
        for ticket_id in unknown:
            print(f"STOP {ticket_id}: category is not in the routing table")
        return 1
    for item in routed:
        print(f"ROUTED {item['id']} -> {item['team']}")
    write_json(run_dir(run_id) / "03_route.json", routed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
