from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from aegisops_contracts import DataQuality, DataQualityState, FeatureVector, Severity, TelemetryWindow
from aegisops_intelligence.anomaly import BaselineDetector, BaselineProfile


class BaselineDetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = BaselineDetector(
            BaselineProfile(
                means={"p95_latency_ms": 100, "error_rate": 0.01},
                stddevs={"p95_latency_ms": 20, "error_rate": 0.01},
                threshold=3.0,
            )
        )
        now = datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
        self.window = TelemetryWindow(
            started_at=now - timedelta(minutes=5),
            ended_at=now,
            lookback_seconds=300,
        )

    def test_scores_feature_vector_with_explainable_contributors(self) -> None:
        event = self.detector.score(
            FeatureVector(
                entity="order-service",
                schema_version="feature-schema.v1",
                window=self.window,
                values={"p95_latency_ms": 190, "error_rate": 0.05},
                data_quality=DataQuality(DataQualityState.OK, 0.0, 5.0),
            )
        )

        self.assertTrue(event.is_anomalous)
        self.assertEqual(event.severity, Severity.CRITICAL)
        self.assertEqual(event.contributing_features[0].name, "p95_latency_ms")
        self.assertEqual(event.model.feature_schema_version, "feature-schema.v1")
        self.assertTrue(event.idempotency_key.startswith("anomkey_"))

    def test_blocks_scoring_when_data_quality_fails_gate(self) -> None:
        with self.assertRaises(ValueError):
            self.detector.score(
                FeatureVector(
                    entity="order-service",
                    schema_version="feature-schema.v1",
                    window=self.window,
                    values={"p95_latency_ms": 190, "error_rate": 0.05},
                    data_quality=DataQuality(DataQualityState.BLOCKED, 0.8, 5.0),
                )
            )


if __name__ == "__main__":
    unittest.main()

