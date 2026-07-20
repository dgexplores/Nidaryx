from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response

from aegisops_common.settings import ServiceSettings

settings = ServiceSettings.from_env("demo-api")
app = FastAPI(title="AegisOps Demo API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "faults_enabled": settings.faults_enabled}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'aegisops_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.post("/faults/inject")
def inject_fault(payload: dict[str, object]) -> dict[str, object]:
    if not settings.faults_enabled:
        raise HTTPException(status_code=403, detail="fault injection is disabled")
    scenario = str(payload.get("scenario", "unknown"))
    return {"accepted": True, "scenario": scenario, "mode": "development-only"}
