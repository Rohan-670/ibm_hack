# Shared output schema — PR-mode agents

`diff-analyst`, `test-gap-agent`, `doc-sync-agent`, and `compliance-agent`
must all emit a JSON array of objects with this shape:

```json
{
  "file": "sample-project/app/routes.py",
  "line": 24,
  "severity": "blocker | warning | info",
  "category": "breaking_change | test_gap | doc_drift | compliance",
  "description": "Short human-readable explanation",
  "suggested_fix": "Concrete next step, or null"
}
```

Rules:
- `severity: blocker` = must be fixed before merge/release.
- `severity: warning` = should be fixed, not release-blocking on its own.
- `severity: info` = FYI, no action required.
- Never invent evidence. If unsure, use `"severity": "info"` and say so in
  the description rather than guessing.
- Output ONLY the JSON array. No prose before or after it.
