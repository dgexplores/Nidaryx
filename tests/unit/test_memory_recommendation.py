from __future__ import annotations

import unittest
from dataclasses import replace

from nidaryx_intelligence.anomaly import BaselineDetector, BaselineProfile
from nidaryx_intelligence.correlation import IncidentCorrelator
from nidaryx_intelligence.demo_data import default_graph, default_runbooks, sample_feature_vectors
from nidaryx_intelligence.memory import IncidentMemoryIndex
from nidaryx_intelligence.rca import RCARanker
from nidaryx_intelligence.recommendations import RecommendationEngine


class MemoryRecommendationTests(unittest.TestCase):
    def test_similar_incident_informs_investigation_first_recommendation(self) -> None:
        detector = BaselineDetector(
            BaselineProfile(
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
        )
        anomalies = [detector.score(vector) for vector in sample_feature_vectors()]
        incident = IncidentCorrelator(default_graph()).correlate(anomalies)[0]

        memory = IncidentMemoryIndex()
        memory.add_resolved_incident(
            replace(incident, id="incident-history"),
            anomalies,
            confirmed_cause="mongodb",
            resolution="Reduced database pool pressure.",
            outcome="Recovered.",
        )
        similar = memory.find_similar(incident, anomalies)
        candidates = RCARanker(default_graph()).rank(
            incident,
            anomalies,
            history_scores={match.confirmed_cause: match.score for match in similar},
        )
        incident = replace(incident, candidates=candidates)

        recommendation = RecommendationEngine(default_runbooks()).recommend(incident, similar)

        self.assertEqual(similar[0].incident_id, "incident-history")
        self.assertIn("Inspect telemetry for mongodb", recommendation.investigation_steps[0])
        self.assertEqual(recommendation.actions[0].action_identifier, "demo.load.reduce")


if __name__ == "__main__":
    unittest.main()

