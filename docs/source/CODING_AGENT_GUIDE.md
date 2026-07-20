# AegisOps Coding-Agent Operating Guide

## Mission
Build AegisOps incrementally as a reliable, explainable, and safe AI-assisted SRE platform. Treat structured telemetry and versioned evidence as the source of truth. Never make broad speculative rewrites.

## Mandatory workflow for every task
1. Read the relevant architecture, contract, implementation, and test files.
2. State the single behavior being changed.
3. Reproduce the current failure or establish a baseline.
4. Implement the smallest cohesive change.
5. Add or update tests.
6. Run focused checks, then the full applicable gate.
7. Report changed files, commands, results, and risks.

## Never do these
- Do not delete or weaken tests to get green status.
- Do not suppress exceptions without an explicit fallback and observability.
- Do not introduce arbitrary shell-command execution.
- Do not place secrets in source, logs, fixtures, or prompts.
- Do not claim causal certainty; return ranked probable causes.
- Do not let an LLM invent telemetry evidence or choose executable actions.
- Do not automatically retry failed remediation actions without a defined idempotency and safety policy.

## Error-fixing protocol
```text
reproduce -> capture -> classify -> one hypothesis -> minimal patch -> focused test
          -> adjacent tests -> full gate -> root-cause note -> prevention test
```
If two different minimal hypotheses fail, revert speculative patches and produce a diagnostic report instead of continuing uncontrolled changes.

## Architecture contracts
- Raw telemetry survives ML/intelligence failure.
- Feature vectors include schema version and quality metadata.
- Anomaly events include model, preprocessing, threshold, and explanation versions.
- Correlation is idempotent.
- RCA exposes decomposed evidence scores.
- Recommendations cite runbooks and similar incidents.
- Remediation accepts only allow-listed action identifiers with validated parameters.
- Every state-changing operation is authenticated, authorized, audited, and verified.

## Required checks
### Python services
```bash
ruff check .
ruff format --check .
mypy services packages
pytest -q
```

### Web UI
```bash
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e
```

### Containers
```bash
docker compose config
docker compose build
docker compose up -d
# poll health endpoints; then run scenario tests
docker compose down -v
```

## Task response format
```text
Goal:
Files inspected:
Changes:
Tests executed:
Results:
Known limitations:
Next bounded task:
```
