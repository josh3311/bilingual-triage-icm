# 01_intake

Desk 1. A ticket arrives. This desk checks it is complete and notices the language. It does no thinking about the problem.

## 1. Task
Read every ticket in `data/sample_tickets.json`. Keep the ones that are complete. Tag each kept ticket as `EN` or `FR`. List the rejected ones by id.

## 2. Inputs (what arrives)
One file: `data/sample_tickets.json`. Each ticket MUST have these 4 fields:

| Field | Meaning | Example |
|---|---|---|
| `id` | Unique ticket id, format `T` plus 3 digits | `T014` |
| `subject` | Short title, 1 to 120 characters | `Colis introuvable` |
| `body` | The message, 10 to 2000 characters | `Mon colis n'est jamais arrivé...` |
| `received_at` | Date in the form `YYYY-MM-DD` | `2026-11-02` |

## 3. Skills used
None. Checking fields and detecting a language are exact jobs, so scripts do them. A skill would only add guessing.

## 4. Scripts used
| Script | What it checks | Prints |
|---|---|---|
| `scripts/validate_ticket.py` | All 4 fields exist, `id` format is right, ids are unique, lengths are in range, date format is right | `VALID` or `REJECTED <id>: <reason>` per ticket |
| `scripts/detect_language.py` | Counts common French words (`le`, `la`, `je`, `mon`, `pas`, `est`, `vous`, accents) against common English words in the `subject` and `body`. More French hits gives `FR`, otherwise `EN`. A tie gives `EN` and sets `language_confidence` to `low` | The tag and confidence per ticket |
| `scripts/run_intake.py <run_id>` | Runs the two scripts above on `00_input.json` and writes `01_intake.json` (kept tickets with `language` and `language_confidence`) and `01_rejected.json` (rejected tickets with reasons) | The count line, for example `COUNT OK 30 = 30 + 0` |
| `scripts/count_check.py 01` | Tickets in equals tickets kept plus tickets rejected | `COUNT OK 30 = 30 + 0` or `COUNT FAIL` |

## 5. Done when
1. `count_check.py 01` prints `COUNT OK`.
2. Every ticket in `runs/<run_id>/01_intake.json` has a `language` of `EN` or `FR` and status `intake_ok`.
3. Every rejected ticket is listed in `runs/<run_id>/01_rejected.json` with its reason.

## 6. Do not
- MUST NOT change the text of a ticket. Not a typo, not a space.
- MUST NOT guess a missing field. A ticket with a missing field is rejected.
- MUST NOT call a skill or ask the AI to decide the language. The script decides.

## 7. Next stage
`02_classify`. Hand over `runs/<run_id>/01_intake.json`.
