from __future__ import annotations

import unittest

from aegisops_intelligence.anomaly import BaselineDetector, BaselineProfile
from aegisops_intelligence.correlation import IncidentCorrelator
from aegisops_intelligence.demo_data import default_graph, sample_feature_vectors
from aegisops_intelligence.rca import RCARanker


class CorrelationAndRCATests(unittest.TestCase):
    def test_correlates_propagated_symptoms_into_one_incident_and_ranks_root(self) -> None:
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
        graph = default_graph()

        incidents = IncidentCorrelator(graph, merge_window_seconds=300).correlate(anomalies)
        self.assertEqual(len(incidents), 1)

        candidates = RCARanker(graph).rank(incidents[0], anomalies)
        self.assertEqual(candidates[0].entity, "mongodb")
        self.assertGreaterEqual(candidates[0].confidence, candidates[1].confidence)
        self.assertIn("candidate anomaly is earliest in the correlated window", candidates[0].supporting_signals)


if __name__ == "__main__":
    unittest.main()

