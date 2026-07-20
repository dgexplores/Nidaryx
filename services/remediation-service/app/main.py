from __future__ import annotations

from fastapi import FastAPI, Response

from aegisops_common.settings import ServiceSettings
from aegisops_contracts import Role, to_primitive
from aegisops_intelligence.demo_data import default_runbooks
from aegisops_intelligence.remediation import Approval, RemediationPolicy, RunbookRegistry

settings = ServiceSettings.from_env("remediation-service")
app = FastAPI(title="AegisOps Remediation Service", version="0.1.0")
policy = RemediationPolicy(RunbookRegistry(default_runbooks()))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"ready": True, "executor": "dry-run"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(
        f'aegisops_service_ready{{service="{settings.service_name}"}} 1\n',
        media_type="text/plain; version=0.0.4",
    )


@app.post("/remediations/demo/approve")
def approve_demo(payload: dict[str, object]) -> dict[str, object]:
    approval = Approval(
        incident_id=str(payload.get("incident_id", "incident_demo")),
        runbook_id=str(payload.get("runbook_id", "rb-demo-reduce-load")),
        actor=str(payload.get("actor", "demo-user")),
        role=Role(str(payload.get("role", Role.VIEWER.value))),
        parameters=dict(payload.get("parameters", {"percentage": 25})),
    )
    return to_primitive(policy.approve(approval))
