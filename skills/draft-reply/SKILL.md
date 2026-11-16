---
name: draft-reply
description: Use in stage 05_reply to write one short, polite DRAFT reply, grounded in the looked up records, to a support ticket in the ticket's own language (English or French). Never sends. Never promises.
---

# draft-reply

## What this skill does
It writes one draft reply for one ticket. A person approves it later. The draft is never sent by this skill.

## Input
One looked up ticket: `id`, `subject`, `body`, `language`, `category`, `priority`, `team`, `needs_human`, and `facts` with `customer`, `order`, `charges`, `policy` and `lookup_status`.

## Output (exactly this JSON, nothing else)
```json
{"id": "T014", "language": "EN", "draft": "Hello, thank you for contacting us. ...", "status": "waiting_for_approval"}
```

## Step by step
1. Look at `language`. Write the whole draft in that language. `EN` means English. `FR` means French.
2. Write 3 to 5 sentences in this order:
   1. Greeting.
   2. Show you understood the problem, or state what the records show, in one or two sentences.
   3. Say what happens next, in plain terms ("our team will review your request").
   4. Closing.
3. In French, use "vous" (formal). Greet with "Bonjour". Close with "Cordialement,".
4. In English, greet with "Hello". Close with "Kind regards,".
5. Sign English drafts "Customer Care Team". Sign French drafts "L'équipe du service à la clientèle".
6. Set `status` to `waiting_for_approval`.

## Use the facts
- Take every number, date, amount and status from `facts` or from the ticket. Copy them exactly.
- On a billing or delivery ticket with an order on record, name the order number.
- Use the `policy` text to explain how things work (for example how long a pending charge takes to clear). Do not add rules that are not in it.
- Say "in transit", "delivered", "locked" or "not shipped yet" only when the records say so.
- If `lookup_status` is `not_found`, say you could not match the message to a customer record and that a team member will confirm details.
- If the records do not answer the question, say a team member will check. Do not fill the gap.

## Rules
- MUST write the whole draft in the ticket's language. MUST NOT mix languages.
- MUST NOT promise a refund, a replacement, compensation, a date, or a time limit.
- MUST NOT use these phrases (the script checks them, master list in `data/categories.json`):
  - English: "refund", "guarantee", "within 24 hours", "within 48 hours", "by tomorrow", "we promise", "compensation"
  - French: "remboursement garanti", "nous garantissons", "dans les 24 heures", "dans les 48 heures", "demain", "nous promettons", "compensation"
- MUST NOT mention internal words: team names, priority labels, category names.
- MUST NOT say the message was sent.
- MUST NOT state any fact that is not in `facts` or the ticket (`scripts/grounding.py` checks this).
- If `needs_human` is `true`, say that a team member will review it personally.

## Examples

English ticket about a late package:
```json
{"id": "T014", "language": "EN", "draft": "Hello, thank you for contacting us. Our records show order 7011 shipped on October 20 and that its tracking has not been updated since October 24. A member of our team will follow up with you about the next step. Kind regards, Customer Care Team", "status": "waiting_for_approval"}
```

French ticket about a double charge:
```json
{"id": "T003", "language": "FR", "draft": "Bonjour, merci de nous avoir écrit. Notre dossier montre deux paiements de 112,30 dollars pour la commande 8812, tous deux datés du 3 novembre. Un membre de notre équipe comparera les relevés et vous répondra. Cordialement, L'équipe du service à la clientèle", "status": "waiting_for_approval"}
```

## You know it worked when
`scripts/check_reply.py` prints no `BAD` line for this ticket.
