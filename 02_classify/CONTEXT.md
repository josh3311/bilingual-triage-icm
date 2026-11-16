# 02_classify

Desk 2. The first thinking desk. Decide what kind of problem this is and how urgent it is. A script then checks the answer is allowed.

## 1. Task
For each ticket, make two decisions: a category and a priority. Also flag any ticket the skill is unsure about.

## 2. Inputs (what arrives)
`runs/<run_id>/01_intake.json`. Each ticket has `id`, `subject`, `body`, `received_at`, `language`.

## 3. Skills used
`skills/triage-ticket/SKILL.md`. It reads the ticket and decides:
- `category`: one of 6 (`billing`, `delivery`, `account_access`, `product_issue`, `complaint`, `other`)
- `priority`: `P1`, `P2` or `P3`
- `needs_human`: `true` or `false`
- `reason`: one sentence in English, so a reviewer can read why, even when the ticket is French

This is judgment, not counting. Two tickets can use different words for the same problem, so a person-like reading is needed.

## 4. Scripts used
| Script | What it checks | Prints |
|---|---|---|
| `scripts/check_classification.py` | `category` is in the 6 allowed, `priority` is in the 3 allowed, `needs_human` is true or false, `reason` is not empty, and every `id` matches an intake ticket | `OK` or `BAD <id>: <reason>` per ticket |
| `scripts/count_check.py 02` | Tickets in equals tickets out | `COUNT OK 30 = 30` or `COUNT FAIL` |

## 5. Done when
1. `check_classification.py` prints no `BAD` line.
2. `count_check.py 02` prints `COUNT OK`.
3. `runs/<run_id>/02_classify.json` exists and every ticket has status `classified`.

## 6. Do not
- MUST NOT invent a new category or priority.
- MUST NOT leave a ticket without a category. When unsure, use `other`, priority `P2`, and set `needs_human` to `true`.
- MUST NOT translate or rewrite the ticket. Only add the four new fields.
- MUST NOT run the checking script on its own output and then say "looks fine". The script's printed result is the answer.

## 7. Next stage
`03_route`. Hand over `runs/<run_id>/02_classify.json`.
