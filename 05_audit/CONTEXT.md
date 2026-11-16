# 05_audit

Desk 5. The teacher who checks the homework. A script samples tickets from the whole run and says PASS or FAIL. The AI does not grade itself.

## 1. Task
Pick 20 tickets from the run. Check each one end to end across all four stage files. Print PASS or FAIL. Then stop and wait for a person.

## 2. Inputs (what arrives)
All four files in `runs/<run_id>/`: `01_intake.json`, `02_classify.json`, `03_route.json`, `04_reply.json`.

## 3. Skills used
None. If the same AI that wrote the replies also judged them, it would mark its own homework. A script with fixed rules is fair.

## 4. Scripts used
| Script | What it does | Prints |
|---|---|---|
| `scripts/audit_sample.py` | Picks 20 of 30 tickets using the fixed seed `42`, so a re-run checks the same 20. For each, runs 7 checks (below). | One line per ticket, then `AUDIT PASS 20/20` or `AUDIT FAIL 17/20` with the failing ids and the stage to fix |
| `scripts/export_approved.py` | After a person marks drafts `approved`, writes only those to `runs/<run_id>/outbox.json`. It does not send. | `EXPORTED <n> drafts` |

The 7 checks per sampled ticket:
1. Language tag is `EN` or `FR`.
2. Category is in the allowed 6.
3. Priority is in the allowed 3.
4. Team matches the routing table for that category.
5. Draft language equals ticket language.
6. Draft has no banned promise phrase.
7. Draft status is `waiting_for_approval`.

## 5. Done when
`audit_sample.py` prints `AUDIT PASS 20/20`. PASS needs all 20. The checks are exact rules, so 19 of 20 means a real bug, not noise.
(Review note for Josh: 20 of 20 is my choice. Trove used 95 percent because flyers need human comparison. Change it if you disagree.)

## 6. Do not
- MUST NOT hide a failure or reword it as a pass.
- MUST NOT re-run until it passes without fixing the cause.
- MUST NOT change the seed to get an easier sample.
- MUST NOT export or send drafts that a person has not approved.

## 7. Next stage
There is no stage 6. After PASS, a person reads the drafts and marks each `approved` or `returned`.
- `approved` drafts: run `export_approved.py`, then a person sends them.
- `returned` drafts: go back to `04_reply` for those tickets only.
After FAIL: go to the stage named in the failure line, fix, and re-run from that stage to 5.
