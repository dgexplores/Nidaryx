# Security And Remediation

Nidaryx uses a strict approval and allow-list model.

## Rules

- No arbitrary shell execution.
- No remediation without actor, role, runbook id, parameter validation, and audit record.
- Viewer and investigator roles cannot approve remediation.
- Runbooks may define investigation-only entries with no executable action.
- Execution is dry-run by default until a controlled executor is explicitly wired for a demo environment.
- Failed remediation does not auto-retry unless a runbook defines idempotency, verification, and rollback.

## Audit Fields

Each state-changing action records incident id, actor, role, decision, action identifier, request payload, result payload, and timestamp.

