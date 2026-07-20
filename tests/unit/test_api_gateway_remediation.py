from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api-gateway"))

from app import main  # noqa: E402


class ApiGatewayRemediationTests(unittest.TestCase):
    def test_approval_endpoint_dry_runs_allow_listed_action(self) -> None:
        response = main.approve_remediation(
            "incident-1",
            {
                "runbook_id": "rb-reduce-ingress-load",
                "actor": "showcase-operator",
                "role": "approver",
                "parameters": {"percentage": 25},
                "execute": True,
            },
        )

        self.assertEqual(response["approval"]["decision"], "approved")
        self.assertEqual(response["execution"]["decision"], "executed")
        self.assertEqual(response["execution"]["result"]["mode"], "dry_run")
        self.assertFalse(response["execution"]["result"]["executed"])


if __name__ == "__main__":
    unittest.main()
