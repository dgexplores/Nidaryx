from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, Response

from tracesentry_common.settings import ServiceSettings
from tracesentry_intelligence.demo_data import sample_feature_vectors

settings = ServiceSettings.from_env("feature-service")
app = FastAPI(title="TraceSentry Feature Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "feature_schema_version": settings.feature_schema_version}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'tracesentry_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.post("/features/demo-window")
def demo_window() -> dict[str, object]:
    vectors = sample_feature_vectors(datetime.now(timezone.utc))
    return {"items": [vector.entity for vector in vectors], "schema_version": settings.feature_schema_version}
