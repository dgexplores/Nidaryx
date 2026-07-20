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
8. Show `/ops/state` API JSON from Render.

Skipped: full Docker observability stack. Add after the live showcase is stable.
