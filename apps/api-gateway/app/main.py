from __future__ import annotations

import os

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from nidaryx_common.settings import ServiceSettings
from nidaryx_intelligence.demo_data import sample_incident_payload

settings = ServiceSettings.from_env("api-gateway")
app = FastAPI(
    title="Nidaryx API Gateway",
    version="0.1.0",
    description="Incident-facing facade for Nidaryx workflows.",
)
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:8080",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def index() -> dict[str, object]:
    return {
        "name": "Nidaryx",
        "mode": "showcase",
        "links": ["/health", "/ready", "/incidents", "/models"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "dependencies": {"mongodb": "unchecked", "intelligence": "demo"}}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'nidaryx_service_ready{{service="{settings.service_name}"}} 1\n',
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
