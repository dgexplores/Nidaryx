from __future__ import annotations

from fastapi import FastAPI, Response

from nidaryx_common.settings import ServiceSettings

settings = ServiceSettings.from_env("order-service")
app = FastAPI(title="Nidaryx Order Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "dependencies": {"mongodb": "unchecked"}}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'nidaryx_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.post("/orders")
def create_order(payload: dict[str, object]) -> dict[str, object]:
    customer_id = str(payload.get("customer_id", "anonymous"))
    return {
        "order_id": f"demo-{customer_id}",
        "status": "accepted",
        "dependencies": ["mongodb"],
    }
