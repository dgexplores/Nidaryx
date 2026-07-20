from __future__ import annotations

from collections.abc import Iterable

from nidaryx_contracts import AnomalyEvent, EvidenceScore, Incident, RCACandidate

from .service_catalog import DependencyGraph


class RCARanker:
    def __init__(self, graph: DependencyGraph, weights: dict[str, float] | None = None) -> None:
        self.graph = graph
        self.weights = weights

    def rank(
        self,
        incident: Incident,
        anomalies: Iterable[AnomalyEvent],
        history_scores: dict[str, float] | None = None,
        top_n: int = 3,
    ) -> tuple[RCACandidate, ...]:
        anomaly_by_entity = {event.entity: event for event in anomalies}
        history_scores = history_scores or {}
        candidates = self._candidate_entities(incident, anomaly_by_entity.keys())
        scored: list[tuple[str, EvidenceScore, tuple[str, ...], tuple[str, ...]]] = []
        for entity in candidates:
            evidence, signals, limitations = self._evidence_for(
                entity, incident, anomaly_by_entity, history_scores
            )
            scored.append((entity, evidence, signals, limitations))

        ranked = sorted(scored, key=lambda item: item[1].total(self.weights), reverse=True)[:top_n]
        result: list[RCACandidate] = []
        for index, (entity, evidence, signals, limitations) in enumerate(ranked, start=1):
            confidence = round(evidence.total(self.weights), 4)
            result.append(
                RCACandidate(
                    entity=entity,
                    rank=index,
                    confidence=confidence,
                    evidence=evidence,
                    supporting_signals=signals,
                    limitations=limitations,
                )
            )
        return tuple(result)

    def _candidate_entities(
        self, incident: Incident, anomalous_entities: Iterable[str]
    ) -> tuple[str, ...]:
        candidates = set(incident.affected_services).union(anomalous_entities)
        for service in incident.affected_services:
            candidates.update(self.graph.upstreams(service))
        return tuple(sorted(candidates))

    def _evidence_for(
        self,
        entity: str,
        incident: Incident,
        anomaly_by_entity: dict[str, AnomalyEvent],
        history_scores: dict[str, float],
    ) -> tuple[EvidenceScore, tuple[str, ...], tuple[str, ...]]:
        event = anomaly_by_entity.get(entity)
        first_symptom = min(
            (anomaly.detected_at for anomaly in anomaly_by_entity.values()), default=incident.opened_at
        )
        signals: list[str] = []
        limitations: list[str] = []

        temporal = 0.25
        if event and event.detected_at <= first_symptom:
            temporal = 1.0
            signals.append("candidate anomaly is earliest in the correlated window")
        elif event:
            temporal = 0.55
            signals.append("candidate is anomalous during the incident window")
        else:
            limitations.append("no direct anomaly event for candidate")

        dependency = 0.35
        if any(self.graph.is_upstream(entity, service) for service in incident.affected_services):
            dependency = 1.0
            signals.append("candidate is upstream of affected service symptoms")
        elif entity in incident.affected_services:
            dependency = 0.65
            signals.append("candidate is directly affected")
        else:
            limitations.append("dependency evidence is weak")

        trace = 0.0
        if event and event.trace_ids:
            trace = 0.75
            signals.append("trace identifiers link candidate to the incident")
        else:
            limitations.append("trace evidence unavailable")

        severity = 0.0
        data_quality_penalty = 0.2
        if event:
            severity = min(1.0, event.score / max(event.threshold * 2, 1.0))
            data_quality_penalty = max(
                event.data_quality.missing_ratio,
                1.0 if not event.data_quality.scoring_allowed else 0.0,
            )
            if severity >= 0.7:
                signals.append("candidate has persistent high-magnitude deviation")

        history = max(0.0, min(1.0, history_scores.get(entity, 0.0)))
        if history > 0:
            signals.append("historical incidents support this candidate")

        evidence = EvidenceScore(
            temporal=round(temporal, 4),
            dependency=round(dependency, 4),
            trace=round(trace, 4),
            severity=round(severity, 4),
            history=round(history, 4),
            data_quality_penalty=round(data_quality_penalty, 4),
        )
        return evidence, tuple(signals), tuple(limitations)

