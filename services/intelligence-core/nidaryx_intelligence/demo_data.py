from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from nidaryx_contracts import (
    DataQuality,
    DataQualityState,
    FeatureVector,
    Incident,
    RecommendationType,
    RunbookAction,
    ServiceDependency,
    Severity,
    TelemetryWindow,
    to_primitive,
)

from .anomaly import BaselineDetector, BaselineProfile
from .correlation import IncidentCorrelator
from .memory import IncidentMemoryIndex
from .rca import RCARanker
from .recommendations import RecommendationEngine
from .service_catalog import DependencyGraph


def default_graph() -> DependencyGraph:
    return DependencyGraph(
        [
            ServiceDependency(upstream="mongodb", downstream="order-service", kind="database"),
            ServiceDependency(upstream="order-service", downstream="checkout-api", kind="http"),
            ServiceDependency(upstream="checkout-api", downstream="api-gateway", kind="http"),
        ]
    )


def default_runbooks() -> list[RunbookAction]:
    return [
        RunbookAction(
            runbook_id="rb-investigate-db-pool",
            title="Inspect database connection pool pressure",
            recommendation_type=RecommendationType.INVESTIGATION,
            action_identifier=None,
            parameters_schema={},
            preconditions=("Incident has database latency or saturation evidence.",),
            verification=("Pool utilization and query latency are reviewed.",),
            rollback=(),
            enabled=True,
        ),
        RunbookAction(
            runbook_id="rb-reduce-ingress-load",
            title="Reduce ingress load by percentage",
            recommendation_type=RecommendationType.REMEDIATION,
            action_identifier="traffic.load.reduce",
            parameters_schema={
                "type": "object",
                "required": ["percentage"],
                "properties": {"percentage": {"type": "integer"}},
            },
            preconditions=(
                "Environment has an approved traffic-control policy.",
                "Incident has active saturation evidence.",
            ),
            verification=("Request rate returns within baseline band.",),
            rollback=("Restore the previous load-generator rate.",),
            enabled=True,
        ),
    ]


def sample_feature_vectors(now: datetime | None = None) -> list[FeatureVector]:
    now = now or datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
    quality = DataQuality(
        state=DataQualityState.OK,
        missing_ratio=0.0,
        staleness_seconds=15,
        notes=(),
    )
    db_window = TelemetryWindow(
        started_at=now - timedelta(minutes=5),
        ended_at=now - timedelta(seconds=20),
        lookback_seconds=300,
    )
    service_window = TelemetryWindow(
        started_at=now - timedelta(minutes=5),
        ended_at=now,
        lookback_seconds=300,
    )
    return [
        FeatureVector(
            entity="mongodb",
            schema_version="feature-schema.v1",
            window=db_window,
            values={
                "request_rate": 120,
                "p95_latency_ms": 420,
                "error_rate": 0.03,
                "db_pool_utilization": 0.96,
            },
            data_quality=quality,
            trace_ids=("trace-checkout-001",),
            labels={"tier": "storage"},
        ),
        FeatureVector(
            entity="order-service",
            schema_version="feature-schema.v1",
            window=service_window,
            values={
                "request_rate": 118,
                "p95_latency_ms": 390,
                "error_rate": 0.08,
                "db_pool_utilization": 0.88,
            },
            data_quality=quality,
            trace_ids=("trace-checkout-001",),
            labels={"tier": "application"},
        ),
        FeatureVector(
            entity="api-gateway",
            schema_version="feature-schema.v1",
            window=service_window,
            values={
                "request_rate": 116,
                "p95_latency_ms": 360,
                "error_rate": 0.05,
                "db_pool_utilization": 0.0,
            },
            data_quality=quality,
            trace_ids=("trace-checkout-001",),
            labels={"tier": "edge"},
        ),
    ]


def sample_incident() -> Incident:
    graph = default_graph()
    profile = BaselineProfile(
        means={
            "request_rate": 110,
            "p95_latency_ms": 120,
            "error_rate": 0.01,
            "db_pool_utilization": 0.35,
        },
        stddevs={
            "request_rate": 20,
            "p95_latency_ms": 45,
            "error_rate": 0.02,
            "db_pool_utilization": 0.15,
        },
        threshold=3.0,
    )
    detector = BaselineDetector(profile)
    anomalies = [detector.score(vector) for vector in sample_feature_vectors()]
    incident = IncidentCorrelator(graph, merge_window_seconds=300).correlate(anomalies)[0]

    memory = IncidentMemoryIndex()
    historical = replace(incident, id="incident_previous_db_pool_saturation")
    memory.add_resolved_incident(
        historical,
        anomalies,
        confirmed_cause="mongodb",
        resolution="Reduced connection-pool pressure and scaled the database tier.",
        outcome="Latency returned to baseline within 6 minutes.",
    )
    similar = memory.find_similar(incident, anomalies)
    candidates = RCARanker(graph).rank(
        incident,
        anomalies,
        history_scores={match.confirmed_cause: match.score for match in similar},
        top_n=3,
    )
    incident = replace(incident, candidates=candidates)
    recommendation = RecommendationEngine(default_runbooks()).recommend(incident, similar)
    return replace(incident, recommendation=recommendation)


def sample_incident_payload() -> dict[str, object]:
    return to_primitive(sample_incident())
