from __future__ import annotations

from fastapi import FastAPI, Response

from nidaryx_common.settings import ServiceSettings
from nidaryx_intelligence.demo_data import sample_incident_payload

settings = ServiceSettings.from_env("memory-service")
app = FastAPI(title="Nidaryx Memory Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "index": "structured-demo"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'nidaryx_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.get("/incidents/demo/similar")
def demo_similar() -> dict[str, object]:
    incident = sample_incident_payload()
    refs = incident.get("recommendation", {}).get("similar_incident_refs", [])
    return {"incident_id": incident["id"], "similar_incident_refs": refs}
