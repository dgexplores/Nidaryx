# Nidaryx Showcase Path

This is the laptop-light path for a final-year demo.

## What Runs

- Frontend: Netlify static site
- Backend: Render free FastAPI service
- Data: deterministic incident intelligence demo
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

Demo API:

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

The UI falls back to built-in demo data if the API is sleeping.

## Demo Script

1. Open the UI.
2. Point to `API connected` or `Demo fallback`.
3. Show active incident queue.
4. Open RCA panel: mongodb ranks first.
5. Explain evidence: temporal, dependency, trace, severity, history.
6. Show recommendation: investigation before approval-gated remediation.
7. Show `/incidents` API JSON from Render.

Skipped: full Docker observability stack. Add after the live showcase is stable.

