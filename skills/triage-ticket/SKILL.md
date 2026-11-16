---
name: triage-ticket
description: Use in stage 02_classify to give one English or French support ticket a category, a priority and a needs_human flag. Output is strict JSON that scripts check afterward.
---

# triage-ticket

## What this skill does
It reads one ticket and decides three things: the category, the priority, and whether a person must look at it. It writes one sentence explaining why, in English.

## Input
One ticket object: `id`, `subject`, `body`, `received_at`, `language` (`EN` or `FR`). The ticket may be English or French. Read it in its own language.

## Output (exactly this JSON, nothing else)
```json
{"id": "T014", "category": "delivery", "priority": "P2", "needs_human": false, "reason": "Customer says the package never arrived and gives a tracking number."}
```

## Step by step
1. Read the `subject` and `body`.
2. Pick ONE category from this list. Use the meaning, not the exact words.

| Category | Choose it when the customer talks about | French clues |
|---|---|---|
| `billing` | a charge, an invoice, a payment, a refund request | facture, paiement, remboursement, débité |
| `delivery` | a package that is late, lost, damaged or at the wrong address | colis, livraison, retard, introuvable |
| `account_access` | a login, a password, a locked account | mot de passe, connexion, compte bloqué |
| `product_issue` | something that does not work or arrived broken | ne fonctionne pas, défectueux, panne |
| `complaint` | unhappiness about the service itself, with no other clear problem | insatisfait, mauvais service, plainte |
| `other` | anything else, or you cannot tell | |

3. Pick the priority with these exact rules:
   - `P1` if ANY is true: money was taken wrongly; the customer is locked out of their account; a package is missing for 14 days or more; the customer mentions a lawyer or legal action.
   - `P3` if the message is a question or feedback with no problem to fix.
   - `P2` for everything else.
4. Set `needs_human` to `true` if the ticket is unclear, mixes two problems, or has a safety or legal angle. Otherwise `false`.
5. Write `reason` as one sentence in English, under 25 words.

## Rules
- MUST use only the 6 categories and 3 priorities above.
- MUST NOT invent a new category. When unsure: `other`, `P2`, `needs_human` true.
- MUST NOT change or translate the ticket text.
- MUST output only the JSON object. No extra words.

## Examples

English ticket: "I was charged twice for order 5521. Please fix this."
```json
{"id": "T003", "category": "billing", "priority": "P1", "needs_human": false, "reason": "Customer was charged twice, so money was taken wrongly."}
```

French ticket: "Bonjour, je voudrais savoir si vous livrez aussi le dimanche."
```json
{"id": "T021", "category": "other", "priority": "P3", "needs_human": false, "reason": "General question about Sunday delivery with no problem to fix."}
```

## You know it worked when
`scripts/check_classification.py` prints no `BAD` line for this ticket.
