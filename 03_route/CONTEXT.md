# 03_route

Desk 3. Send each ticket to the right team. This is a lookup, not thinking, so a table does it and no AI is needed.

## 1. Task
For each ticket, look up its `category` in `data/routing_table.json` and write the matching team. Carry the priority forward so the team can see urgent work first.

## 2. Inputs (what arrives)
`runs/<run_id>/02_classify.json`.

## 3. Skills used
None. The same category must always go to the same team. A table gives the same answer every time. A skill could drift.

## 4. Scripts used
| Script | What it does | Prints |
|---|---|---|
| `scripts/route_ticket.py` | Looks up each category in `data/routing_table.json` and writes `team` | `ROUTED <id> -> <team>` per ticket |
| `scripts/count_check.py 03` | Tickets in equals tickets out, and every ticket has exactly one team | `COUNT OK 30 = 30` or `COUNT FAIL` |

The table (master copy is `data/routing_table.json`):

| Category | Team |
|---|---|
| `billing` | Billing Team |
| `delivery` | Delivery Support |
| `account_access` | Account Security |
| `product_issue` | Technical Support |
| `complaint` | Customer Care Lead |
| `other` | General Support Queue |

## 5. Done when
1. Every ticket has exactly one `team` from the table.
2. `count_check.py 03` prints `COUNT OK`.
3. `runs/<run_id>/03_route.json` exists and every ticket has status `routed`.
4. Tickets with priority `P1` are marked `urgent: true`. All others are `urgent: false`.

## 6. Do not
- MUST NOT guess a team. If a category is not in the table, stop and report the ticket id.
- MUST NOT send a ticket to two teams.
- MUST NOT change `category` or `priority`. If they look wrong, report it. Fixing them belongs to stage 2.

## 7. Next stage
`04_reply`. Hand over `runs/<run_id>/03_route.json`.
