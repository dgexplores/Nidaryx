from __future__ import annotations

from fastapi import FastAPI, Response

from tracesentry_common.settings import ServiceSettings
from tracesentry_intelligence.demo_data import sample_incident_payload

settings = ServiceSettings.from_env("api-gateway")
app = FastAPI(
    title="TraceSentry API Gateway",
    version="0.1.0",
    description="Incident-facing facade for TraceSentry workflows.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "dependencies": {"mongodb": "unchecked", "intelligence": "demo"}}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'tracesentry_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.get("/incidents")
def incidents() -> dict[str, object]:
    incident = sample_incident_payload()
    return {"items": [incident], "page": 1, "page_size": 25, "total": 1}


@app.get("/incidents/{incident_id}")
def incident_detail(incident_id: str) -> dict[str, object]:
    incident = sample_incident_payload()
    incident["id"] = incident_id
    return incident


@app.get("/models")
def models() -> dict[str, object]:
    return {
        "items": [
            {
                "model_version": settings.model_version,
                "feature_schema_version": settings.feature_schema_version,
                "status": "demo-ready",
            }
        ]
    }
