from __future__ import annotations

from fastapi import FastAPI, Response

from tracesentry_common.settings import ServiceSettings
from tracesentry_contracts import to_primitive
from tracesentry_intelligence.anomaly import BaselineDetector, BaselineProfile
from tracesentry_intelligence.demo_data import sample_feature_vectors

settings = ServiceSettings.from_env("anomaly-service")
app = FastAPI(title="TraceSentry Anomaly Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "model_version": settings.model_version}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'tracesentry_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.post("/score/demo-window")
def score_demo_window() -> dict[str, object]:
    detector = BaselineDetector(
        BaselineProfile(
            means={"request_rate": 110, "p95_latency_ms": 120, "error_rate": 0.01, "db_pool_utilization": 0.35},
            stddevs={"request_rate": 20, "p95_latency_ms": 45, "error_rate": 0.02, "db_pool_utilization": 0.15},
            threshold=3.0,
        )
    )
    return {"items": [to_primitive(detector.score(vector)) for vector in sample_feature_vectors()]}
