from __future__ import annotations

from fastapi import FastAPI, Response

from tracesentry_common.settings import ServiceSettings
from tracesentry_intelligence.demo_data import sample_incident_payload

settings = ServiceSettings.from_env("rca-service")
app = FastAPI(title="TraceSentry RCA Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "ranking_model": "weighted-evidence.v1"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'tracesentry_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.get("/rca/demo")
def demo_rca() -> dict[str, object]:
    incident = sample_incident_payload()
    return {"incident_id": incident["id"], "candidates": incident["candidates"]}
