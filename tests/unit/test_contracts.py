from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from aegisops_contracts import (
    DataQuality,
    DataQualityState,
    FeatureVector,
    TelemetryWindow,
    contract_hash,
    stable_json,
)


class ContractTests(unittest.TestCase):
    def test_stable_json_and_hash_are_order_insensitive(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}

        self.assertEqual(stable_json(left), stable_json(right))
        self.assertEqual(contract_hash(left), contract_hash(right))

    def test_feature_vector_validates_window_and_quality(self) -> None:
        now = datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
        vector = FeatureVector(
            entity="api-gateway",
            schema_version="feature-schema.v1",
            window=TelemetryWindow(now - timedelta(minutes=1), now, 60),
            values={"request_rate": 10},
            data_quality=DataQuality(DataQualityState.OK, 0.0, 1.0),
        )

        vector.validate()


if __name__ == "__main__":
    unittest.main()

