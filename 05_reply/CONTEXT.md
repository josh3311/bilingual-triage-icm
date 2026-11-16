# 05_reply

Desk 5. Write a DRAFT reply in the customer's own language, using only the facts the lookup found. A person approves it later. This is where the human gate begins.

## 1. Task
For each ticket, write one draft reply. English tickets get English drafts. French tickets get French drafts. Set the status to `waiting_for_approval`. Do not send anything.

## 2. Inputs (what arrives)
`runs/<run_id>/04_lookup.json`. Each ticket has `id`, `subject`, `body`, `language`, `category`, `priority`, `team`, `needs_human`, and `facts` (customer, order, charges, policy) with a `lookup_status`.

## 3. Skills used
`skills/draft-reply/SKILL.md`. It writes the draft: 3 to 5 sentences, polite, one clear next step, no promises. It may state only what is in `facts` or in the ticket itself. Writing a good message in two languages is judgment, so a skill does it.

## 4. Scripts used
| Script | What it checks | Prints |
|---|---|---|
| `scripts/check_reply.py` | Draft is not empty and is 3 to 5 sentences. Draft language matches the ticket `language` (same French versus English word count method as stage 1). Draft contains none of the banned promise phrases in `data/categories.json`. Draft names no team from the routing table and shows no priority label. Every number, date and amount in the draft is in the facts or the ticket. A claim such as "in transit", "delivered" or "account locked" matches the records. A billing or delivery draft names the order. Status is `waiting_for_approval`. | `OK` or `BAD <id>: <reason>` per ticket |
| `scripts/count_check.py 05` | Tickets in equals drafts out | `COUNT OK 30 = 30` or `COUNT FAIL` |

## 5. Done when
1. `check_reply.py` prints no `BAD` line.
2. `count_check.py 05` prints `COUNT OK`.
3. `runs/<run_id>/05_reply.json` has one draft per ticket, each with status `waiting_for_approval`.

## 6. Do not
- MUST NOT send, email, post or export anything. This stage has no sending tool.
- MUST NOT state a fact that is not in `facts` or the ticket. If the records have no answer, say a team member will check.
- MUST NOT promise a refund, a delivery date, compensation, or a time limit such as "within 24 hours".
- MUST NOT mix languages inside one draft. A French ticket gets all French.
- MUST NOT mention internal things: team names, priority labels, category names.
- MUST NOT mark a draft `approved`. Only a person does that.

## 7. Next stage
`06_audit`. Hand over `runs/<run_id>/05_reply.json`.
