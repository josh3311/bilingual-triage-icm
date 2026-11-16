# 04_lookup

Desk 4. The filing cabinet. Find what the company's records say about this customer, this order and this topic, before anyone writes a reply. No AI is involved, because finding a record is an exact job.

## 1. Task
For each routed ticket, look up the customer, the order it is about, that order's charges, and the one policy article that fits. Save what was found next to the ticket. If there is no customer record, say so and flag the ticket for a person.

## 2. Inputs (what arrives)
`runs/<run_id>/03_route.json` and the records in `data/records.json` (customers, orders, charges, policy articles). The ticket carries a `customer_id`. An order number written in the ticket text is used first. If the ticket names no order, the customer's most recent order is used for billing, delivery, product and other tickets.

## 3. Skills used
None. A script does the lookup with a SQLite database built from `data/records.json`. To use a real company database, replace the records file or point `scripts/records.py` at the real tables. The rest of the workspace does not change.

## 4. Scripts used
| Script | What it does | Prints |
|---|---|---|
| `scripts/lookup_records.py <run_id>` | Looks up each ticket and writes `facts` (customer, order, charges, policy) and `lookup_status` to `04_lookup.json` | One line per ticket: `found`, `partial` or `not_found`, with the order and charge counts |
| `scripts/count_check.py 04` | Tickets in equals tickets out, and every ticket has a lookup result | `COUNT OK 30 = 30` or `COUNT FAIL` |

`lookup_status` values: `found` (customer and any order needed), `partial` (billing or delivery ticket, customer found, no order), `not_found` (no customer record, so `needs_human` becomes `true`).

## 5. Done when
1. `lookup_records.py` ran without error.
2. `count_check.py 04` prints `COUNT OK`.
3. `runs/<run_id>/04_lookup.json` has a `facts` object for every ticket.

## 6. Do not
- MUST NOT guess a missing fact. If a record is missing, the status says so.
- MUST NOT change `category`, `priority` or `team`.
- MUST NOT write any text for the customer. Writing starts in stage 5.
- MUST NOT use real customer data. The records are synthetic.

## 7. Next stage
`05_reply`. Hand over `runs/<run_id>/04_lookup.json`.
