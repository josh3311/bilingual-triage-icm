# CLAUDE.md

The map of the whole workspace. Read this first, then open only the folder for the stage you are in.

## 1. What this workspace does

It takes customer support tickets written in English or French and moves them through six stages: intake, classify, route, lookup, reply, audit. The reply is written only from facts found in the company's records. The output is a set of draft replies in the customer's own language, each waiting for a person to approve it. Nothing in this repo can send a message to a customer.

## 2. The six stages, in order

| Stage | Folder | In | Out |
|---|---|---|---|
| 1 | `01_intake/` | `data/sample_tickets.json` | `runs/<run_id>/01_intake.json` (valid tickets with a language tag) and a list of rejected ids |
| 2 | `02_classify/` | `01_intake.json` | `02_classify.json` (category, priority, needs_human) |
| 3 | `03_route/` | `02_classify.json` | `03_route.json` (one team per ticket) |
| 4 | `04_lookup/` | `03_route.json` and `data/records.json` | `04_lookup.json` (customer, order, charges and policy found for each ticket) |
| 5 | `05_reply/` | `04_lookup.json` | `05_reply.json` (draft per ticket, status `waiting_for_approval`) |
| 6 | `06_audit/` | all five files above | `06_audit.json` (PASS or FAIL, with ticket ids) |

After stage 6 the workspace stops. A person approves or returns each draft. Only approved drafts are exported to `runs/<run_id>/outbox.json` by `scripts/export_approved.py`. A person sends them from there.

## Scripts and tests
Scripts live in `scripts/` (standard library Python only): `run_intake.py`, `validate_ticket.py`, `detect_language.py`, `check_classification.py`, `route_ticket.py`, `records.py`, `lookup_records.py`, `grounding.py`, `check_reply.py`, `audit_sample.py`, `count_check.py`, `export_approved.py`, `build_site_data.py`. Tests: `python3 -m unittest discover -s tests`. The website in `docs/` runs a JavaScript copy of the checks (`docs/triage.js`) and a test proves it matches the Python.

## 3. The core rule

Scripts count and check. Skills think and write. A person says OK. The AI never counts by eye, never grades its own work, and never sends.

## 4. Shared facts (one source of truth: `data/categories.json`; this list must match it)

- Languages: `EN`, `FR`
- Categories (6): `billing`, `delivery`, `account_access`, `product_issue`, `complaint`, `other`
- Priorities (3): `P1` urgent, `P2` normal, `P3` low
- Teams (6): Billing Team, Delivery Support, Account Security, Technical Support, Customer Care Lead, General Support Queue
- Statuses: `received`, `rejected`, `intake_ok`, `classified`, `routed`, `waiting_for_approval`, `approved`, `returned`
- Run folder: `runs/<run_id>/` where `run_id` is the date and a number, for example `2026-11-16_01`

## 5. Hard rules

- MUST read only the `CONTEXT.md` of the stage you are in, plus this file.
- MUST run the stage's scripts and report their PASS or FAIL output as printed. MUST NOT summarize a count from memory.
- MUST NOT invent a category, priority, team or status that is not in section 4.
- MUST NOT send, email or post anything. This workspace has no sending tool by design.
- MUST NOT state a fact in a reply that is not in the lookup facts or the ticket.
- MUST NOT promise a refund, a date, compensation or a deadline in any reply.
- MUST NOT use real customer data. `data/sample_tickets.json` is synthetic: 30 tickets, 15 EN and 15 FR.
- MUST stop after stage 6 and wait for a person.
- If something is unknown, write `TODO: ask owner` instead of guessing.

## 6. Failure handling

| Failure | Go back to |
|---|---|
| Stage 1 rejects a ticket | Stop for that ticket. List its id. Do not repair the customer's text. |
| Stage 2 or 3 check fails | Re-run the failed stage once. If it fails again, stop and report the ticket ids. |
| Stage 4 finds no customer | Keep going. The ticket is flagged `needs_human` and the draft says a person will confirm details. |
| Stage 5 language, promise or fact check fails | Re-run stage 5 for those tickets only. |
| Stage 6 says FAIL | Fix the stage named in the failure message, then re-run stages from there to 6. |
| Two failed fix loops on the same ticket | Stop. Write the blocker in `runs/<run_id>/blockers.md`. Ask the person. |
