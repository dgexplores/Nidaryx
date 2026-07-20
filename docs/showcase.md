# Nidaryx Incident Drill Path

This is the laptop-light path for a final-year incident-response showcase.

## What Runs

- Frontend: Netlify static site
- Backend: Render free FastAPI service
- Data: deterministic telemetry window with realistic SRE parameters
- Docker: skipped for the first live showcase

## Deploy Backend On Render

1. Create a Render account.
2. New Web Service -> connect the GitHub repo.
3. Render should detect `render.yaml`.
4. Set `CORS_ALLOWED_ORIGINS` after the frontend URL exists.

Health check:

```text
https://<render-service>/health
```

Incident API:

```text
https://<render-service>/incidents
```

## Deploy Frontend On Netlify

1. Create a Netlify account.
2. New site from GitHub.
3. Build command: `npm ci && npm run web:build`
4. Publish directory: `apps/web-ui/dist`
5. Add env var:

```text
VITE_NIDARYX_API_URL=https://<render-service>
```

The UI can run in local telemetry mode if the API is sleeping.

## Incident Drill Script

1. Open the UI.
2. Point to `Telemetry API connected`.
3. Show healthy service parameters.
4. Trigger DB saturation.
5. Show latency, error rate, and DB pool utilization crossing baseline.
6. Open RCA panel: mongodb ranks first.
7. Show recommendation: investigation before approval-gated remediation.
8. Request approval for `traffic.load.reduce`.
9. Show the dry-run audit result: approved, executed, but no production mutation.
10. Show `/ops/state` API JSON from Render.

## Live Telemetry Mode

Set these on the API service when Prometheus is available:

```text
NIDARYX_LIVE_TELEMETRY=true
NIDARYX_PROMETHEUS_URL=https://<prometheus-host>
```

Optional query overrides:

```text
NIDARYX_QUERY_REQUEST_RATE
NIDARYX_QUERY_P95_LATENCY_MS
NIDARYX_QUERY_ERROR_RATE
NIDARYX_QUERY_DB_POOL_UTILIZATION
```

`/ops/state` uses Prometheus first in live mode. If Prometheus is unavailable, the incident drill remains available so the presentation does not fail.

Skipped: full Docker observability stack. Add after the live showcase is stable.
