from __future__ import annotations

import os

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from nidaryx_common.settings import ServiceSettings
from nidaryx_intelligence.demo_data import sample_incident_payload
from nidaryx_telemetry.prometheus import PrometheusClient, PrometheusQuery, TelemetryQueryError

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

_active_scenario = os.getenv("NIDARYX_SCENARIO", "healthy")

_healthy_services = [
    {"service": "api-gateway", "state": "live", "latency": "42 ms", "errorRate": "0.1%", "owner": "edge-platform"},
    {"service": "checkout-api", "state": "live", "latency": "55 ms", "errorRate": "0.0%", "owner": "checkout-platform"},
    {"service": "order-service", "state": "live", "latency": "73 ms", "errorRate": "0.2%", "owner": "checkout"},
    {"service": "mongodb", "state": "live", "latency": "31 ms", "errorRate": "0.0%", "owner": "data-platform"},
]

_degraded_services = [
    {"service": "api-gateway", "state": "partial", "latency": "360 ms", "errorRate": "5.0%", "owner": "edge-platform"},
    {"service": "checkout-api", "state": "partial", "latency": "180 ms", "errorRate": "1.7%", "owner": "checkout-platform"},
    {"service": "order-service", "state": "degraded", "latency": "390 ms", "errorRate": "8.0%", "owner": "checkout"},
    {"service": "mongodb", "state": "degraded", "latency": "420 ms", "errorRate": "3.0%", "owner": "data-platform"},
]

_healthy_signals = [
    {"name": "request_rate", "value": "110 req/min", "baseline": "100-140 req/min", "state": "live"},
    {"name": "p95_latency_ms", "value": "73 ms", "baseline": "< 180 ms", "state": "live"},
    {"name": "error_rate", "value": "0.2%", "baseline": "< 1.0%", "state": "live"},
    {"name": "db_pool_utilization", "value": "35%", "baseline": "< 70%", "state": "live"},
]

_degraded_signals = [
    {"name": "request_rate", "value": "118 req/min", "baseline": "100-140 req/min", "state": "live"},
    {"name": "p95_latency_ms", "value": "420 ms", "baseline": "< 180 ms", "state": "degraded"},
    {"name": "error_rate", "value": "8.0%", "baseline": "< 1.0%", "state": "degraded"},
    {"name": "db_pool_utilization", "value": "96%", "baseline": "< 70%", "state": "degraded"},
]

_signal_baselines = {
    "request_rate": "100-140 req/min",
    "p95_latency_ms": "< 180 ms",
    "error_rate": "< 1.0%",
    "db_pool_utilization": "< 70%",
}
_signal_queries = {
    "request_rate": os.getenv(
        "NIDARYX_QUERY_REQUEST_RATE",
        'sum(rate(http_requests_total{service=~"api-gateway|checkout-api|order-service"}[5m])) * 60',
    ),
    "p95_latency_ms": os.getenv(
        "NIDARYX_QUERY_P95_LATENCY_MS",
        'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=~"api-gateway|checkout-api|order-service"}[5m])) by (le)) * 1000',
    ),
    "error_rate": os.getenv(
        "NIDARYX_QUERY_ERROR_RATE",
        'sum(rate(http_requests_total{service=~"api-gateway|checkout-api|order-service",status=~"5.."}[5m])) / clamp_min(sum(rate(http_requests_total{service=~"api-gateway|checkout-api|order-service"}[5m])), 1)',
    ),
    "db_pool_utilization": os.getenv(
        "NIDARYX_QUERY_DB_POOL_UTILIZATION",
        'max(mongodb_pool_in_use_connections / clamp_min(mongodb_pool_max_connections, 1))',
    ),
}
_signal_thresholds = {
    "p95_latency_ms": 180.0,
    "error_rate": 0.01,
    "db_pool_utilization": 0.70,
}


def _is_incident_active() -> bool:
    return _active_scenario != "healthy"


def _live_telemetry_enabled() -> bool:
    return os.getenv("NIDARYX_LIVE_TELEMETRY", "false").lower() == "true"


def _first_value(client: PrometheusClient, name: str) -> float | None:
    samples = client.instant_query(PrometheusQuery(_signal_queries[name]))
    return samples[0].value if samples else None


def _format_signal(name: str, value: float | None) -> dict[str, object]:
    if value is None:
        return {"name": name, "value": "missing", "baseline": _signal_baselines[name], "state": "stale"}
    if name == "request_rate":
        formatted = f"{value:.0f} req/min"
    elif name == "p95_latency_ms":
        formatted = f"{value:.0f} ms"
    else:
        formatted = f"{value * 100:.1f}%"
    threshold = _signal_thresholds.get(name)
    state = "degraded" if threshold is not None and value > threshold else "live"
    return {"name": name, "value": formatted, "baseline": _signal_baselines[name], "state": state}


def _prometheus_ops_state() -> dict[str, object]:
    client = PrometheusClient(settings.prometheus_url)
    values = {name: _first_value(client, name) for name in _signal_queries}
    signals = [_format_signal(name, values[name]) for name in _signal_queries]
    active = any(signal["state"] == "degraded" for signal in signals)
    return {
        "scenario": "live_prometheus" if active else "healthy",
        "active": active,
        "services": _degraded_services if active else _healthy_services,
        "signals": signals,
        "incident": sample_incident_payload() if active else None,
        "telemetry_source": "prometheus",
    }


def _drill_ops_state() -> dict[str, object]:
    incident = sample_incident_payload() if _is_incident_active() else None
    return {
        "scenario": _active_scenario,
        "active": _is_incident_active(),
        "services": _degraded_services if _is_incident_active() else _healthy_services,
        "signals": _degraded_signals if _is_incident_active() else _healthy_signals,
        "incident": incident,
        "telemetry_source": "incident_drill",
    }


@app.get("/")
def index() -> dict[str, object]:
    return {
        "name": "Nidaryx",
        "mode": "incident-intelligence",
        "links": ["/health", "/ready", "/ops/state", "/incidents", "/models"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {
        "ready": True,
        "scenario": _active_scenario,
        "dependencies": {"mongodb": "observed", "intelligence": "online"},
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
                "status": "ready",
            }
        ]
    }


@app.get("/ops/state")
def ops_state() -> dict[str, object]:
    if _live_telemetry_enabled():
        try:
            return _prometheus_ops_state()
        except TelemetryQueryError as exc:
            state = _drill_ops_state()
            state["telemetry_source"] = "incident_drill"
            state["telemetry_error"] = str(exc)
            return state
    return _drill_ops_state()


@app.post("/ops/scenario")
def set_ops_scenario(payload: dict[str, object]) -> dict[str, object]:
    global _active_scenario
    scenario = str(payload.get("scenario", "healthy"))
    if scenario not in {"healthy", "db_pool_saturation"}:
        scenario = "healthy"
    _active_scenario = scenario
    return ops_state()


@app.get("/demo/state")
def legacy_demo_state() -> dict[str, object]:
    return ops_state()


@app.post("/demo/scenario")
def legacy_demo_scenario(payload: dict[str, object]) -> dict[str, object]:
    return set_ops_scenario(payload)
