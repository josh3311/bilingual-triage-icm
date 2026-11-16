"""Stage 04 helpers: a small SQLite database built from data/records.json, and the lookup rules. Standard library only.
The website runs a JavaScript copy of the same rules (docs/triage.js). tests check both give the same facts.
"""
import re
import sqlite3

from common import DATA, load_json

SCHEMA = """
CREATE TABLE customers (id TEXT PRIMARY KEY, language TEXT, account_status TEXT, locked_since TEXT, failed_logins INTEGER);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id TEXT, placed_at TEXT, total REAL, status TEXT, shipped_at TEXT,
                     carrier TEXT, tracking_status TEXT, tracking_last_update TEXT, expected_at TEXT);
CREATE TABLE charges (id TEXT PRIMARY KEY, order_id INTEGER, customer_id TEXT, amount REAL, charged_at TEXT, kind TEXT, description TEXT);
CREATE TABLE policies (id TEXT PRIMARY KEY, topic TEXT, language TEXT, title TEXT, body TEXT);
"""
COLUMNS = {
    "customers": ["id", "language", "account_status", "locked_since", "failed_logins"],
    "orders": ["id", "customer_id", "placed_at", "total", "status", "shipped_at", "carrier", "tracking_status", "tracking_last_update", "expected_at"],
    "charges": ["id", "order_id", "customer_id", "amount", "charged_at", "kind", "description"],
    "policies": ["id", "topic", "language", "title", "body"],
}
ORDER_CATEGORIES = {"billing", "delivery", "product_issue", "other"}


def build_db(records=None):
    """Build an in-memory database from the records file."""
    records = records or load_json(DATA / "records.json")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    for table, columns in COLUMNS.items():
        marks = ",".join("?" * len(columns))
        db.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({marks})",
                       [[row[c] for c in columns] for row in records[table]])
    return db


def one(db, sql, args=()):
    row = db.execute(sql, args).fetchone()
    return dict(row) if row else None


def many(db, sql, args=()):
    return [dict(r) for r in db.execute(sql, args).fetchall()]


def pick_topic(item, customer, order, charges):
    text = (item["subject"] + " " + item["body"]).lower()
    if re.search(r"sunday|dimanche", text):
        return "sunday_delivery"
    if re.search(r"opening hours|heures d.ouverture", text):
        return "holiday_hours"
    if re.search(r"\breturn|retour", text):
        return "return_policy"
    if re.search(r"receipt|(?:\bun|\ble|\bmon|\bdu) reçu\b", text):
        return "receipt"
    if re.search(r"adresse courriel|email address", text):
        return "email_change"
    if re.search(r"damaged|abîm|cracked|broken", text):
        return "product_defect"
    category = item.get("category")
    if category == "billing":
        payments = [c for c in charges if c["kind"] == "payment"]
        amounts = [c["amount"] for c in payments]
        return "double_charge" if len(amounts) != len(set(amounts)) else "billing_line"
    if category == "delivery":
        return "address_change" if order and order["status"] == "processing" else "late_delivery"
    if category == "account_access":
        return "locked_account" if customer and customer["account_status"] == "locked" else "password_reset"
    if category == "product_issue":
        return "app_issue" if re.search(r"\bapp\b|application", text) else "product_defect"
    if category == "complaint":
        return "complaint"
    return "general"


def find_facts(item, db):
    """Look up what the records say about one routed ticket. Returns the facts and a status:
    found (customer and any needed order), partial (customer but no order), not_found (no customer)."""
    customer = one(db, "SELECT * FROM customers WHERE id = ?", (item.get("customer_id"),))
    order, charges = None, []
    if customer and item.get("category") in ORDER_CATEGORIES:
        text = item["subject"] + " " + item["body"]
        for number in re.findall(r"\b\d{4}\b", text):
            order = one(db, "SELECT * FROM orders WHERE id = ? AND customer_id = ?", (int(number), customer["id"]))
            if order:
                break
        if not order:
            order = one(db, "SELECT * FROM orders WHERE customer_id = ? ORDER BY placed_at DESC, id DESC LIMIT 1", (customer["id"],))
    if order:
        charges = many(db, "SELECT id, amount, charged_at, kind, description FROM charges WHERE order_id = ? ORDER BY charged_at, id", (order["id"],))
    topic = pick_topic(item, customer, order, charges)
    policy = one(db, "SELECT id, topic, title, body FROM policies WHERE topic = ? AND language = ?", (topic, item.get("language")))
    if not customer:
        status = "not_found"
    elif item.get("category") in {"billing", "delivery"} and not order:
        status = "partial"
    else:
        status = "found"
    return {"status": status, "customer": customer, "order": order, "charges": charges, "policy": policy}
