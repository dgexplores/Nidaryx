from __future__ import annotations

from dataclasses import dataclass

from tracesentry_contracts import AnomalyEvent, Incident, SimilarIncident


@dataclass(frozen=True)
class IncidentMemoryRecord:
    incident_id: str
    services: frozenset[str]
    signals: frozenset[str]
    confirmed_cause: str
    resolution: str
    outcome: str


def jaccard(left: set[str] | frozenset[str], right: set[str] | frozenset[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left.intersection(right)) / len(left.union(right))


class IncidentMemoryIndex:
    def __init__(self, records: list[IncidentMemoryRecord] | None = None) -> None:
        self.records = records or []

    def add_resolved_incident(
        self,
        incident: Incident,
        anomalies: list[AnomalyEvent],
        confirmed_cause: str,
        resolution: str,
        outcome: str,
    ) -> None:
        self.records.append(
            IncidentMemoryRecord(
                incident_id=incident.id,
                services=frozenset(incident.affected_services),
                signals=frozenset(_dominant_signals(anomalies)),
                confirmed_cause=confirmed_cause,
                resolution=resolution,
                outcome=outcome,
            )
        )

    def find_similar(
        self,
        incident: Incident,
        anomalies: list[AnomalyEvent],
        top_k: int = 3,
    ) -> list[SimilarIncident]:
        query_services = frozenset(incident.affected_services)
        query_signals = frozenset(_dominant_signals(anomalies))
        matches: list[SimilarIncident] = []
        for record in self.records:
            service_score = jaccard(query_services, record.services)
            signal_score = jaccard(query_signals, record.signals)
            score = round(0.65 * service_score + 0.35 * signal_score, 4)
            if score <= 0:
                continue
            matches.append(
                SimilarIncident(
                    incident_id=record.incident_id,
                    score=score,
                    confirmed_cause=record.confirmed_cause,
                    matching_signals=tuple(sorted(query_signals.intersection(record.signals))),
                    resolution=record.resolution,
                    outcome=record.outcome,
                )
            )
        return sorted(matches, key=lambda item: item.score, reverse=True)[:top_k]


def _dominant_signals(anomalies: list[AnomalyEvent]) -> set[str]:
    signals: set[str] = set()
    for anomaly in anomalies:
        for feature in anomaly.contributing_features[:3]:
            signals.add(feature.name)
    return signals

