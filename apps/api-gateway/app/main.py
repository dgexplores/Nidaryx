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
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080",
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

_active_scenario = os.getenv("NIDARYX_DEMO_SCENARIO", "healthy")

_healthy_services = [
    {"service": "api-gateway", "state": "live", "latency": "42 ms", "errorRate": "0.1%", "owner": "edge-platform"},
    {"service": "demo-api", "state": "live", "latency": "55 ms", "errorRate": "0.0%", "owner": "platform-demo"},
    {"service": "order-service", "state": "live", "latency": "73 ms", "errorRate": "0.2%", "owner": "checkout"},
    {"service": "mongodb", "state": "live", "latency": "31 ms", "errorRate": "0.0%", "owner": "data-platform"},
]

_degraded_services = [
    {"service": "api-gateway", "state": "partial", "latency": "360 ms", "errorRate": "5.0%", "owner": "edge-platform"},
    {"service": "demo-api", "state": "live", "latency": "180 ms", "errorRate": "1.7%", "owner": "platform-demo"},
    {"service": "order-service", "state": "degraded", "latency": "390 ms", "errorRate": "8.0%", "owner": "checkout"},
    {"service": "mongodb", "state": "degraded", "latency": "420 ms", "errorRate": "3.0%", "owner": "data-platform"},
]


def _is_incident_active() -> bool:
    return _active_scenario != "healthy"


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
    return {
        "ready": True,
        "scenario": _active_scenario,
        "dependencies": {"mongodb": "unchecked", "intelligence": "demo"},
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'nidaryx_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.get("/incidents")
def incidents() -> dict[str, object]:
    if not _is_incident_active():
        return {"items": [], "page": 1, "page_size": 25, "total": 0}
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


@app.get("/demo/state")
def demo_state() -> dict[str, object]:
    incident = sample_incident_payload() if _is_incident_active() else None
    return {
        "scenario": _active_scenario,
        "active": _is_incident_active(),
        "services": _degraded_services if _is_incident_active() else _healthy_services,
        "incident": incident,
    }


@app.post("/demo/scenario")
def set_demo_scenario(payload: dict[str, object]) -> dict[str, object]:
    global _active_scenario
    scenario = str(payload.get("scenario", "healthy"))
    if scenario not in {"healthy", "db_pool_saturation"}:
        scenario = "healthy"
    _active_scenario = scenario
    return demo_state()
