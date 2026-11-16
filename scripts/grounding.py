"""Check that a draft only states facts the records or the ticket back up. No AI involved.
Rules:
1. Every number in the draft (amounts, days, order numbers) must appear in the records for that ticket or in the ticket text.
2. Status claims (in transit, delivered, account locked) must match the records.
3. For billing and delivery tickets with an order on record, the draft must name the order number.
"""
import json
import re

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")

# (pattern, what the records must say)
CLAIMS = [
    (re.compile(r"\bin transit\b|\ben transit\b", re.I), "in transit", lambda f: bool(f["order"]) and f["order"]["tracking_status"] == "in_transit"),
    (re.compile(r"\b(?:was|were|been) delivered\b|\ba été livré", re.I), "delivered", lambda f: bool(f["order"]) and f["order"]["status"] == "delivered"),
    (re.compile(r"account (?:is|was|has been) locked|compte (?:est|a été) (?:bloqué|verrouillé)", re.I), "account locked", lambda f: bool(f["customer"]) and f["customer"]["account_status"] == "locked"),
    (re.compile(r"\b(?:has|have) not shipped\b|pas encore été expédié|pas encore expédié", re.I), "not shipped yet", lambda f: bool(f["order"]) and f["order"]["status"] == "processing"),
]


def normalize(token):
    """Compare numbers by value: 54, 54.0 and 54,00 are the same number."""
    value = float(token.replace(",", "."))
    return str(int(value)) if value == int(value) else repr(value)


def fact_text(facts):
    """The facts a draft may rely on, as one string. Row ids of customers, charges and policies are left out."""
    keep = {
        "customer": {k: v for k, v in (facts.get("customer") or {}).items() if k != "id"},
        "order": facts.get("order"),
        "charges": [{k: v for k, v in c.items() if k != "id"} for c in facts.get("charges", [])],
        "policy": {k: v for k, v in (facts.get("policy") or {}).items() if k != "id"},
    }
    return json.dumps(keep, ensure_ascii=False)


def numbers(text):
    return {normalize(t) for t in NUMBER.findall(text)}


def problems(item):
    facts = item.get("facts")
    draft = item.get("draft") or ""
    if not isinstance(facts, dict):
        return ["no lookup result to check the draft against"]
    found = []
    allowed = numbers(fact_text(facts)) | numbers(item.get("subject", "") + " " + item.get("body", ""))
    unknown = sorted({normalize(t) for t in NUMBER.findall(draft)} - allowed)
    if unknown:
        found.append("number not in the records or the ticket: " + ", ".join(unknown))
    for pattern, label, supported in CLAIMS:
        if pattern.search(draft) and not supported(facts):
            found.append(f"claims '{label}' but the records do not say so")
    order = facts.get("order")
    if order and item.get("category") in {"billing", "delivery"} and str(order["id"]) not in draft:
        found.append(f"draft does not name order {order['id']}")
    return found
