from __future__ import annotations

from aegisops_contracts import Incident, Recommendation, RecommendationType, RunbookAction, SimilarIncident


class RecommendationEngine:
    def __init__(self, runbooks: list[RunbookAction]) -> None:
        self.runbooks = runbooks

    def recommend(
        self, incident: Incident, similar_incidents: list[SimilarIncident] | None = None
    ) -> Recommendation:
        similar_incidents = similar_incidents or []
        lead_candidate = incident.candidates[0] if incident.candidates else None
        lead_entity = lead_candidate.entity if lead_candidate else "the highest-confidence component"

        steps = [
            f"Inspect telemetry for {lead_entity} before changing downstream services.",
            "Compare current dominant anomaly features with trace and log context.",
            "Check data-quality flags before treating the RCA ranking as actionable.",
        ]
        if similar_incidents:
            steps.append(
                f"Review matching incident {similar_incidents[0].incident_id} and confirm whether its resolution still applies."
            )

        actions = tuple(
            runbook
            for runbook in self.runbooks
            if runbook.enabled and runbook.recommendation_type is RecommendationType.REMEDIATION
        )
        evidence_refs = tuple(candidate.entity for candidate in incident.candidates[:3])
        return Recommendation(
            incident_id=incident.id,
            summary=f"Investigate {lead_entity} first; remediation remains approval-gated.",
            investigation_steps=tuple(steps),
            actions=actions,
            evidence_refs=evidence_refs,
            similar_incident_refs=tuple(match.incident_id for match in similar_incidents),
        )

