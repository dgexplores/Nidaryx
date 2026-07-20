from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

CONTRACT_VERSION = "nidaryx.contracts.v1"


class IncidentStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DataQualityState(StrEnum):
    OK = "ok"
    PARTIAL = "partial"
    STALE = "stale"
    BLOCKED = "blocked"


class RecommendationType(StrEnum):
    INVESTIGATION = "investigation"
    REMEDIATION = "remediation"


class Role(StrEnum):
    VIEWER = "viewer"
    INVESTIGATOR = "investigator"
    APPROVER = "approver"
    ADMINISTRATOR = "administrator"


class RemediationDecision(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass(frozen=True)
class TelemetryWindow:
    started_at: datetime
    ended_at: datetime
    lookback_seconds: int

    def validate(self) -> None:
        if self.started_at >= self.ended_at:
            raise ValueError("telemetry window start must be before end")
        if self.lookback_seconds <= 0:
            raise ValueError("lookback_seconds must be positive")


@dataclass(frozen=True)
class DataQuality:
    state: DataQualityState
    missing_ratio: float
    staleness_seconds: float
    notes: tuple[str, ...] = ()

    def validate(self) -> None:
        if not 0 <= self.missing_ratio <= 1:
            raise ValueError("missing_ratio must be between 0 and 1")
        if self.staleness_seconds < 0:
            raise ValueError("staleness_seconds cannot be negative")

    @property
    def scoring_allowed(self) -> bool:
        return self.state in {DataQualityState.OK, DataQualityState.PARTIAL}


@dataclass(frozen=True)
class FeatureVector:
    entity: str
    schema_version: str
    window: TelemetryWindow
    values: dict[str, float]
    data_quality: DataQuality
    trace_ids: tuple[str, ...] = ()
    labels: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.entity:
            raise ValueError("feature vector entity is required")
        if not self.schema_version:
            raise ValueError("feature schema_version is required")
        self.window.validate()
        self.data_quality.validate()
        if not self.values:
            raise ValueError("feature vector values are required")
        for name, value in self.values.items():
            if not name:
                raise ValueError("feature name cannot be empty")
            if not isinstance(value, int | float):
                raise TypeError(f"feature {name} must be numeric")


@dataclass(frozen=True)
class ContributingFeature:
    name: str
    value: float
    baseline: float
    deviation: float
    direction: str


@dataclass(frozen=True)
class ModelMetadata:
    model_version: str
    feature_schema_version: str
    preprocessing_version: str
    threshold: float
    explanation_version: str


@dataclass(frozen=True)
class AnomalyEvent:
    id: str
    entity: str
    detected_at: datetime
    window: TelemetryWindow
    score: float
    threshold: float
    severity: Severity
    contributing_features: tuple[ContributingFeature, ...]
    data_quality: DataQuality
    model: ModelMetadata
    idempotency_key: str
    trace_ids: tuple[str, ...] = ()

    @property
    def is_anomalous(self) -> bool:
        return self.score >= self.threshold


@dataclass(frozen=True)
class EvidenceScore:
    temporal: float
    dependency: float
    trace: float
    severity: float
    history: float
    data_quality_penalty: float

    def total(self, weights: dict[str, float] | None = None) -> float:
        configured = weights or {
            "temporal": 0.25,
            "dependency": 0.25,
            "trace": 0.15,
            "severity": 0.20,
            "history": 0.10,
            "data_quality_penalty": 0.15,
        }
        value = (
            configured["temporal"] * self.temporal
            + configured["dependency"] * self.dependency
            + configured["trace"] * self.trace
            + configured["severity"] * self.severity
            + configured["history"] * self.history
            - configured["data_quality_penalty"] * self.data_quality_penalty
        )
        return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class RCACandidate:
    entity: str
    rank: int
    confidence: float
    evidence: EvidenceScore
    supporting_signals: tuple[str, ...]
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimilarIncident:
    incident_id: str
    score: float
    confirmed_cause: str
    matching_signals: tuple[str, ...]
    resolution: str
    outcome: str


@dataclass(frozen=True)
class RunbookAction:
    runbook_id: str
    title: str
    recommendation_type: RecommendationType
    action_identifier: str | None
    parameters_schema: dict[str, Any]
    preconditions: tuple[str, ...]
    verification: tuple[str, ...]
    rollback: tuple[str, ...]
    enabled: bool = True


@dataclass(frozen=True)
class Recommendation:
    incident_id: str
    summary: str
    investigation_steps: tuple[str, ...]
    actions: tuple[RunbookAction, ...]
    evidence_refs: tuple[str, ...]
    similar_incident_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Incident:
    id: str
    status: IncidentStatus
    severity: Severity
    opened_at: datetime
    affected_services: tuple[str, ...]
    anomaly_ids: tuple[str, ...]
    candidates: tuple[RCACandidate, ...] = ()
    recommendation: Recommendation | None = None
    final_cause: str | None = None
    resolution: str | None = None
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class Feedback:
    incident_id: str
    actor: str
    confirmed_cause: str | None
    rejected_candidates: tuple[str, ...]
    action: str | None
    outcome: str
    notes: str
    timestamp: datetime


@dataclass(frozen=True)
class AuditRecord:
    id: str
    incident_id: str
    actor: str
    role: Role
    decision: RemediationDecision
    action_identifier: str
    request: dict[str, Any]
    result: dict[str, Any]
    timestamp: datetime


@dataclass(frozen=True)
class ServiceDependency:
    upstream: str
    downstream: str
    kind: str = "http"


@dataclass(frozen=True)
class ServiceCatalogEntry:
    service: str
    owners: tuple[str, ...]
    dependencies: tuple[str, ...]
    criticality: Severity
    telemetry_labels: dict[str, str]


def to_primitive(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if is_dataclass(value):
        return to_primitive(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in sorted(value.items())}
    if isinstance(value, tuple | list):
        return [to_primitive(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    return json.dumps(to_primitive(value), sort_keys=True, separators=(",", ":"))


def contract_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()

