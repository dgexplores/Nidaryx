# Nidaryx

Nidaryx is an AI-assisted observability and incident-response platform for microservice environments. It turns telemetry windows, anomaly evidence, service topology, historical incidents, and approved runbooks into correlated incidents, ranked probable root causes, similar-case retrieval, and human-approved remediation workflows.

This repository is built from the v2.0 documentation pack in `docs/source/`. The current implementation establishes the production-grade monorepo foundation, typed contracts, reusable intelligence core, service/API boundaries, web UI shell, Docker Compose topology, repeatable unit tests, and a cloud-deployable incident drill.

## Architecture

```text
Application services -> metrics/logs/traces -> feature-service -> anomaly-service
       -> incident-service -> rca-service -> memory-service
       -> recommendation-service -> remediation-service -> audit

Grafana shows raw telemetry. The custom web UI handles incident workflow, RCA evidence,
similar incidents, recommendations, feedback, approvals, and audit.
```

## Access Links

Current known links from the pause checkpoint:

```text
Local frontend: http://127.0.0.1:5173
Local API docs: http://127.0.0.1:8000/docs
Render backend: https://nidaryx.onrender.com
Render health:  https://nidaryx.onrender.com/health
Vercel frontend: add the production URL from the Vercel project dashboard
```

The deployed frontend should use this environment variable:

```text
VITE_NIDARYX_API_URL=https://nidaryx.onrender.com
```

If the deployed frontend shows `Local telemetry mode`, redeploy Vercel after setting the environment variable and make sure Render has:

```text
CORS_ALLOWED_ORIGINS=https://<vercel-site>.vercel.app
```

## Repository Layout

```text
apps/
  api-gateway/       Incident-facing API facade
  demo-api/          Checkout-path traffic/fault service for incident drills
  order-service/     Example business service
  web-ui/            React/Vite incident workflow UI
services/
  intelligence-core/ Dependency-light domain logic used by services and tests
  feature-service/   Feature window validation and schema boundary
  anomaly-service/   Baseline/anomaly scoring API boundary
  incident-service/  Correlation and lifecycle API boundary
  rca-service/       Evidence-ranked probable cause API boundary
  memory-service/    Fingerprint and similarity API boundary
  recommendation-service/
  remediation-service/
packages/
  contracts/         Versioned dataclass contracts
  common-python/     Logging, settings, IDs, time helpers
  telemetry-client/  Prometheus adapter contract
ml/                  Training/evaluation/registry workspace
observability/       Prometheus/Grafana/OTel/Loki/Tempo config
runbooks/            Approved, allow-listed runbook definitions
tests/               Unit, integration, e2e, labelled scenarios
docs/                Product and engineering documentation
```

## Local Development

Incident drill mode:

```bash
npm run demo
```

Then open `http://127.0.0.1:5173`.

```bash
cp .env.example .env
python3 -m pip install -e ".[dev]"
npm install
make test
make lint
docker compose --profile demo up --build
```

## Showcase Deployment

Use the laptop-light path first:

- Backend: Render free web service using `render.yaml`
- Frontend: Vercel static deployment using `apps/web-ui/vercel.json`
- Guide: `docs/showcase.md`

The active Render backend used during setup was:

```text
https://nidaryx.onrender.com
```

The UI reads `VITE_NIDARYX_API_URL` when deployed and can run in local telemetry mode if the API is unavailable. Set it to the Render API URL without a trailing path:

```text
VITE_NIDARYX_API_URL=https://nidaryx.onrender.com
```

To read real Prometheus metrics in `/ops/state`, set:

```bash
NIDARYX_LIVE_TELEMETRY=true
NIDARYX_PROMETHEUS_URL=https://<prometheus-host>
```

The dependency-free domain tests can run before installing third-party packages:

```bash
PYTHONPATH=packages/contracts:packages/common-python:packages/telemetry-client:services/intelligence-core \
python3 -m unittest discover -s tests/unit -p "test_*.py"
```

## Safety Rules

- RCA returns ranked probable causes, never guaranteed causality.
- Recommendations cite current evidence, runbooks, and similar incidents.
- Remediation accepts only allow-listed action identifiers with validated parameters.
- State-changing actions require actor, role, approval, audit, and verification metadata.
- Fault injection is disabled unless the explicit development profile enables it.

## Current Milestone

Phase 0/1 foundation is implemented with representative Phase 3-7 core logic. The showcase path now demonstrates healthy telemetry, controlled DB saturation, anomaly/RCA ranking, recommendations, approval-gated remediation, and dry-run audit output. See `docs/project-status.md` for the pause handoff and next steps.
