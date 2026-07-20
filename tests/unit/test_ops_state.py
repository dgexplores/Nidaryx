from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from nidaryx_telemetry.prometheus import PrometheusSample

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api-gateway"))

from app import main  # noqa: E402


class FakePrometheusClient:
    values = {
        "request_rate": 118,
        "p95_latency_ms": 420,
        "error_rate": 0.08,
        "db_pool_utilization": 0.96,
    }

    def __init__(self, _: str) -> None:
        pass

    def instant_query(self, query):
        for name, expression in main._signal_queries.items():
            if query.expression == expression:
                return [PrometheusSample(metric={}, value=self.values[name], timestamp=0)]
        return []


class OpsStateTests(unittest.TestCase):
    def test_prometheus_state_opens_incident_when_thresholds_cross(self) -> None:
        with patch.object(main, "PrometheusClient", FakePrometheusClient):
            state = main._prometheus_ops_state()

        self.assertTrue(state["active"])
        self.assertEqual(state["telemetry_source"], "prometheus")
        self.assertEqual(state["signals"][1]["value"], "420 ms")
        self.assertEqual(state["signals"][3]["state"], "degraded")
        self.assertIsNotNone(state["incident"])


if __name__ == "__main__":
    unittest.main()
