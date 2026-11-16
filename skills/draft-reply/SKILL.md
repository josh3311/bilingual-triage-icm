---
name: draft-reply
description: Use in stage 04_reply to write one short, polite DRAFT reply to a support ticket in the ticket's own language (English or French). Never sends. Never promises.
---

# draft-reply

## What this skill does
It writes one draft reply for one ticket. A person approves it later. The draft is never sent by this skill.

## Input
One routed ticket: `id`, `subject`, `body`, `language`, `category`, `priority`, `team`, `needs_human`.

## Output (exactly this JSON, nothing else)
```json
{"id": "T014", "language": "EN", "draft": "Hello, thank you for contacting us. ...", "status": "waiting_for_approval"}
```

## Step by step
1. Look at `language`. Write the whole draft in that language. `EN` means English. `FR` means French.
2. Write 3 to 5 sentences in this order:
   1. Greeting.
   2. Show you understood the problem, in your own words, in one sentence.
   3. Say what happens next, in plain terms ("our team will review your request").
   4. Closing.
3. In French, use "vous" (formal). Greet with "Bonjour". Close with "Cordialement,".
4. In English, greet with "Hello". Close with "Kind regards,".
5. Sign English drafts "Customer Care Team". Sign French drafts "L'équipe du service à la clientèle".
6. Set `status` to `waiting_for_approval`.

## Rules
- MUST write the whole draft in the ticket's language. MUST NOT mix languages.
- MUST NOT promise a refund, a replacement, compensation, a date, or a time limit.
- MUST NOT use these phrases (the script checks them, master list in `data/categories.json`):
  - English: "refund", "guarantee", "within 24 hours", "within 48 hours", "by tomorrow", "we promise", "compensation"
  - French: "remboursement garanti", "nous garantissons", "dans les 24 heures", "dans les 48 heures", "demain", "nous promettons", "compensation"
- MUST NOT mention internal words: team names, priority labels, category names.
- MUST NOT say the message was sent.
- If `needs_human` is `true`, say that a team member will review it personally.

## Examples

English ticket about a late package:
```json
{"id": "T014", "language": "EN", "draft": "Hello, thank you for contacting us. We understand your package has not arrived yet and we are sorry for the worry this causes. A member of our team will review your tracking details and follow up with you. Kind regards, Customer Care Team", "status": "waiting_for_approval"}
```

French ticket about a double charge:
```json
{"id": "T003", "language": "FR", "draft": "Bonjour, merci de nous avoir écrit. Nous comprenons que vous avez été débité deux fois pour la même commande. Un membre de notre équipe va examiner votre dossier et vous répondra. Cordialement, L'équipe du service à la clientèle", "status": "waiting_for_approval"}
```

## You know it worked when
`scripts/check_reply.py` prints no `BAD` line for this ticket.
