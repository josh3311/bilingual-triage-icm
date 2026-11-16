"""Stage 01: check every ticket is complete. No AI involved.

Usage: python scripts/validate_ticket.py data/sample_tickets.json
Prints VALID <id> or REJECTED <id>: <reason> for each ticket. Exit code 1 if any ticket is rejected.
"""
import re
import sys
from datetime import datetime

from common import load_json

FIELDS = ["id", "subject", "body", "received_at"]


def validate(ticket, seen_ids):
    """Return None if the ticket is valid, otherwise a short reason."""
    if not isinstance(ticket, dict):
        return "ticket is not an object"
    for field in FIELDS:
        value = ticket.get(field)
        if not isinstance(value, str) or value.strip() == "":
            return f"missing or empty field {field}"
    if not re.fullmatch(r"T\d{3}", ticket["id"]):
        return "id must be T plus 3 digits"
    if ticket["id"] in seen_ids:
        return "duplicate id"
    if not 1 <= len(ticket["subject"]) <= 120:
        return "subject must be 1 to 120 characters"
    if not 10 <= len(ticket["body"]) <= 2000:
        return "body must be 10 to 2000 characters"
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ticket["received_at"]):
        return "received_at must look like YYYY-MM-DD"
    try:
        datetime.strptime(ticket["received_at"], "%Y-%m-%d")
    except ValueError:
        return "received_at is not a real date"
    return None


def validate_all(tickets):
    """Return (valid_tickets, rejected) where rejected is a list of {id, reason}."""
    valid, rejected, seen = [], [], set()
    for ticket in tickets:
        reason = validate(ticket, seen)
        if reason is None:
            seen.add(ticket["id"])
            valid.append(ticket)
        else:
            ticket_id = ticket.get("id") if isinstance(ticket, dict) else None
            rejected.append({"id": ticket_id, "reason": reason})
    return valid, rejected


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_tickets.json"
    valid, rejected = validate_all(load_json(path))
    for ticket in valid:
        print(f"VALID {ticket['id']}")
    for item in rejected:
        print(f"REJECTED {item['id']}: {item['reason']}")
    sys.exit(1 if rejected else 0)
