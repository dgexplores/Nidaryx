# Nidaryx Architecture

The repository follows the v2.0 architecture pack in `docs/source/`. Raw observability remains separate from incident intelligence so metrics, logs, and traces continue operating even if scoring or RCA services are degraded.

## Runtime Boundaries

- `apps/demo-api` and `apps/order-service` generate realistic service traffic and faults.
- `feature-service` owns event-time windows, schema validation, freshness, and completeness flags.
- `anomaly-service` owns model loading, scoring, thresholds, and feature contribution explanations.
- `incident-service` owns idempotent correlation and lifecycle state.
- `rca-service` owns candidate generation and transparent weighted evidence ranking.
- `memory-service` owns resolved incident fingerprints and similarity retrieval.
- `recommendation-service` owns investigation-first suggestions and runbook provenance.
- `remediation-service` owns approval, allow-list validation, dry-run execution, verification, and audit.

## Design Decisions

- HTTP/JSON service contracts are used for the MVP; the core logic is dependency-light and reusable if the transport later moves to an event bus.
- RCA is a ranked evidence model, not a causal oracle.
- Remediation never accepts raw shell commands. Only allow-listed action identifiers can be approved.
- LLM functionality, when added, should summarize structured evidence only and must not invent telemetry.

