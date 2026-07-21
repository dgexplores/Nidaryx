# Nidaryx Project Status

Paused on 2026-07-21.

## Current State

- Repository: `dgexplores/Nidaryx`
- Main branch latest checkpoint: deployment log cleanup after approval-gated remediation showcase
- Backend target: Render free web service
- Backend URL used during setup: `https://nidaryx.onrender.com`
- Frontend target: Vercel static deployment from `apps/web-ui`

## Implemented

- Monorepo structure for frontend, API gateway, domain intelligence, service boundaries, contracts, common utilities, telemetry adapter, observability config, runbooks, and tests.
- React/Vite incident workspace with operational console UI.
- Incident drill controls:
  - healthy state
  - DB pool saturation scenario
  - degraded service and telemetry parameters
  - incident table
  - RCA evidence panel
  - recommendation panel
- FastAPI API gateway endpoints:
  - `GET /health`
  - `GET /ready`
  - `GET /ops/state`
  - `POST /ops/scenario`
  - `GET /incidents`
  - `GET /incidents/{incident_id}`
  - `POST /incidents/{incident_id}/remediation/approve`
- Domain intelligence:
  - statistical baseline anomaly scoring
  - dependency-aware correlation
  - evidence-weighted RCA ranking
  - similar incident memory
  - investigation-first recommendation engine
  - allow-listed remediation approval and dry-run execution
- Prometheus adapter path for live telemetry mode with deterministic fallback.
- Render deployment config.
- Vercel deployment config for both repo-root and `apps/web-ui` root-directory setups.
- Security hygiene:
  - `.env.example` used for configuration shape
  - no secrets committed intentionally
  - security check script passing
  - remediation does not accept raw shell commands

## Verified Locally

```bash
npm run web:build
npm run web:lint
.venv/bin/python -m unittest discover -s tests/unit -p 'test_*.py'
./scripts/security_check.sh
git diff --check
```

The last full verification before pause passed with 11 unit tests.

## Cloud Setup Notes

Render backend:

```text
Build Command: python -m pip install -r requirements-cloud.txt
Start Command: PYTHONPATH=packages/contracts:packages/common-python:packages/telemetry-client:services/intelligence-core uvicorn app.main:app --app-dir apps/api-gateway --host 0.0.0.0 --port $PORT
Health Check: https://nidaryx.onrender.com/health
```

Vercel frontend:

```text
Root Directory: apps/web-ui
Install Command: npm ci --loglevel=error
Build Command: npm run web:build
Output Directory: dist
Environment Variable: VITE_NIDARYX_API_URL=https://nidaryx.onrender.com
```

After Vercel gives a final frontend URL, add it to Render:

```text
CORS_ALLOWED_ORIGINS=https://<vercel-site>.vercel.app
```

Then redeploy Render and Vercel.

## Showcase Script

1. Open the Vercel site.
2. Confirm `Telemetry API connected`.
3. Show healthy service telemetry.
4. Click `Trigger DB Saturation`.
5. Show latency, error rate, and DB pool utilization crossing baseline.
6. Show the incident queue.
7. Show RCA ranking with `mongodb` as the top candidate.
8. Show investigation-first recommendations.
9. Click `Request approval` on the executable runbook.
10. Show dry-run audit output: approved/executed, but no production mutation.

## What Is Still Left

- Confirm final Vercel production URL and set Render CORS to that URL.
- Upgrade ESLint toolchain to v9 later; deployment log noise has already been reduced with `npm ci --loglevel=error`.
- Add FastAPI integration tests using a test client.
- Add persistent storage repositories, likely MongoDB, for incidents, memory, and audit records.
- Replace deterministic drill telemetry with real Prometheus-backed feature collection when a live telemetry source is available.
- Add full Docker health checks after local Docker is available and stable.
- Prepare final-year presentation deck and architecture/demo diagrams.
