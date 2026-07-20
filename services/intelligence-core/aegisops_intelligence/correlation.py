from __future__ import annotations

from collections.abc import Iterable

from aegisops_common.ids import stable_id
from aegisops_contracts import AnomalyEvent, Incident, IncidentStatus, Severity

from .service_catalog import DependencyGraph

SEVERITY_ORDER = {
    Severity.INFO: 0,
    Severity.WARNING: 1,
    Severity.CRITICAL: 2,
}


class IncidentCorrelator:
    def __init__(self, graph: DependencyGraph, merge_window_seconds: int = 300) -> None:
        if merge_window_seconds <= 0:
            raise ValueError("merge_window_seconds must be positive")
        self.graph = graph
        self.merge_window_seconds = merge_window_seconds

    def correlate(self, events: Iterable[AnomalyEvent]) -> list[Incident]:
        anomalous_events = sorted(
            (event for event in events if event.is_anomalous), key=lambda event: event.detected_at
        )
        groups: list[list[AnomalyEvent]] = []
        for event in anomalous_events:
            target_group = self._find_group(event, groups)
            if target_group is None:
                groups.append([event])
            else:
                target_group.append(event)

        return [self._to_incident(group) for group in groups]

    def _find_group(
        self, event: AnomalyEvent, groups: list[list[AnomalyEvent]]
    ) -> list[AnomalyEvent] | None:
        for group in groups:
            if not group:
                continue
            within_window = any(
                abs((event.detected_at - existing.detected_at).total_seconds())
                <= self.merge_window_seconds
                for existing in group
            )
            related = any(
                event.entity == existing.entity
                or self.graph.are_adjacent(event.entity, existing.entity)
                or self._shares_trace(event, existing)
                for existing in group
            )
            if within_window and related:
                return group
        return None

    @staticmethod
    def _shares_trace(left: AnomalyEvent, right: AnomalyEvent) -> bool:
        return bool(set(left.trace_ids).intersection(right.trace_ids))

    def _to_incident(self, group: list[AnomalyEvent]) -> Incident:
        affected_services = tuple(sorted({event.entity for event in group}))
        anomaly_ids = tuple(event.id for event in sorted(group, key=lambda event: event.id))
        severity = max((event.severity for event in group), key=lambda item: SEVERITY_ORDER[item])
        opened_at = min(event.detected_at for event in group)
        incident_id = stable_id(
            "incident",
            opened_at.replace(second=0, microsecond=0).isoformat(),
            ",".join(affected_services),
            ",".join(anomaly_ids),
        )
        return Incident(
            id=incident_id,
            status=IncidentStatus.OPEN,
            severity=severity,
            opened_at=opened_at,
            affected_services=affected_services,
            anomaly_ids=anomaly_ids,
        )

