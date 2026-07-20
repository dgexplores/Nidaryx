from __future__ import annotations

from fastapi import FastAPI, Response

from tracesentry_common.settings import ServiceSettings
from tracesentry_intelligence.demo_data import sample_incident_payload

settings = ServiceSettings.from_env("incident-service")
app = FastAPI(title="TraceSentry Incident Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "correlator": "deterministic-demo"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'tracesentry_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.get("/incidents/demo")
def demo_incident() -> dict[str, object]:
    return sample_incident_payload()
