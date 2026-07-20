from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from nidaryx_common.ids import stable_id
from nidaryx_contracts import (
    AuditRecord,
    RemediationDecision,
    Role,
    RunbookAction,
)


class ActionExecutor(Protocol):
    def execute(self, action_identifier: str, parameters: dict[str, Any]) -> dict[str, Any]:
        ...


class DryRunExecutor:
    def execute(self, action_identifier: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "mode": "dry_run",
            "action_identifier": action_identifier,
            "parameters": parameters,
            "executed": False,
        }


class RunbookRegistry:
    def __init__(self, runbooks: list[RunbookAction]) -> None:
        self._runbooks = {runbook.runbook_id: runbook for runbook in runbooks}

    def get(self, runbook_id: str) -> RunbookAction:
        try:
            return self._runbooks[runbook_id]
        except KeyError as exc:
            raise ValueError(f"unknown runbook: {runbook_id}") from exc

    def enabled_actions(self) -> list[RunbookAction]:
        return [runbook for runbook in self._runbooks.values() if runbook.enabled]


@dataclass(frozen=True)
class Approval:
    incident_id: str
    runbook_id: str
    actor: str
    role: Role
    parameters: dict[str, Any]


class RemediationPolicy:
    allowed_roles = {Role.APPROVER, Role.ADMINISTRATOR}

    def __init__(self, registry: RunbookRegistry, executor: ActionExecutor | None = None) -> None:
        self.registry = registry
        self.executor = executor or DryRunExecutor()

    def approve(self, approval: Approval) -> AuditRecord:
        runbook = self.registry.get(approval.runbook_id)
        if approval.role not in self.allowed_roles:
            return self._audit(
                approval=approval,
                action_identifier=runbook.action_identifier or "",
                decision=RemediationDecision.REJECTED,
                result={"reason": "role cannot approve remediation"},
            )
        if not runbook.enabled or not runbook.action_identifier:
            return self._audit(
                approval=approval,
                action_identifier=runbook.action_identifier or "",
                decision=RemediationDecision.REJECTED,
                result={"reason": "runbook is not executable"},
            )
        validation_error = validate_parameters(runbook.parameters_schema, approval.parameters)
        if validation_error:
            return self._audit(
                approval=approval,
                action_identifier=runbook.action_identifier,
                decision=RemediationDecision.REJECTED,
                result={"reason": validation_error},
            )
        return self._audit(
            approval=approval,
            action_identifier=runbook.action_identifier,
            decision=RemediationDecision.APPROVED,
            result={"preconditions": runbook.preconditions, "verification": runbook.verification},
        )

    def execute(self, approved_record: AuditRecord) -> AuditRecord:
        if approved_record.decision is not RemediationDecision.APPROVED:
            raise ValueError("only approved remediation records can execute")
        result = self.executor.execute(
            approved_record.action_identifier, approved_record.request.get("parameters", {})
        )
        return AuditRecord(
            id=stable_id("audit", approved_record.id, "execute"),
            incident_id=approved_record.incident_id,
            actor=approved_record.actor,
            role=approved_record.role,
            decision=RemediationDecision.EXECUTED,
            action_identifier=approved_record.action_identifier,
            request=approved_record.request,
            result=result,
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _audit(
        *,
        approval: Approval,
        action_identifier: str,
        decision: RemediationDecision,
        result: dict[str, Any],
    ) -> AuditRecord:
        timestamp = datetime.now(timezone.utc)
        return AuditRecord(
            id=stable_id(
                "audit",
                approval.incident_id,
                approval.runbook_id,
                approval.actor,
                decision.value,
                timestamp.isoformat(),
            ),
            incident_id=approval.incident_id,
            actor=approval.actor,
            role=approval.role,
            decision=decision,
            action_identifier=action_identifier,
            request={"runbook_id": approval.runbook_id, "parameters": approval.parameters},
            result=result,
            timestamp=timestamp,
        )


def validate_parameters(schema: dict[str, Any], parameters: dict[str, Any]) -> str | None:
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    missing = required.difference(parameters.keys())
    if missing:
        return f"missing required parameters: {', '.join(sorted(missing))}"
    for name, value in parameters.items():
        expected = properties.get(name, {}).get("type")
        if expected is None:
            return f"unexpected parameter: {name}"
        if expected == "string" and not isinstance(value, str):
            return f"parameter {name} must be a string"
        if expected == "integer" and not isinstance(value, int):
            return f"parameter {name} must be an integer"
        if expected == "number" and not isinstance(value, int | float):
            return f"parameter {name} must be a number"
        if expected == "boolean" and not isinstance(value, bool):
            return f"parameter {name} must be a boolean"
    return None

