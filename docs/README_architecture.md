## Architecture

Six stages, one folder each. A reply is written only from facts a script found in the company's records. Scripts count and check, skills think and write, and a person approves before anything leaves. The workspace has no sending tool.

```mermaid
flowchart LR
  A["Support tickets<br/>English and French"] --> B["01 Intake<br/>scripts"]
  B --> C["02 Classify<br/>skill + check"]
  C --> D["03 Route<br/>lookup table"]
  D --> L["04 Lookup<br/>records database"]
  L --> E["05 Reply<br/>skill + fact check"]
  E --> F["06 Audit<br/>20 ticket sample"]
  F -->|PASS| G{"Person approves?"}
  F -->|FAIL| H["Fix the stage named<br/>in the failure, re-run"]
  G -->|approved| I["outbox.json<br/>a person sends"]
  G -->|returned| E
```

### Who does what

```mermaid
flowchart TB
  subgraph S["Scripts: count and check"]
    S1["validate and tag language"]
    S2["check allowed values"]
    S3["route by table"]
    S3b["look up customer, order, charges, policy"]
    S4["check reply language, promises and facts"]
    S5["audit 20 tickets"]
  end
  subgraph K["Skills: think and write"]
    K1["triage-ticket"]
    K2["draft-reply"]
  end
  subgraph P["Person: says OK"]
    P1["approve or return each draft"]
  end
  S --> K --> P
```

| Stage | Folder | Handled by | Output file |
|---|---|---|---|
| 1 | `01_intake` | Scripts | `01_intake.json` |
| 2 | `02_classify` | Skill `triage-ticket`, then a check script | `02_classify.json` |
| 3 | `03_route` | Script and `routing_table.json` | `03_route.json` |
| 4 | `04_lookup` | Script and `records.json` (SQLite) | `04_lookup.json` |
| 5 | `05_reply` | Skill `draft-reply`, then a check script | `05_reply.json` |
| 6 | `06_audit` | Script | `06_audit.json` |
| Gate | outside the stages | A person | `outbox.json` |
