from __future__ import annotations

import unittest

from nidaryx_contracts import RemediationDecision, Role
from nidaryx_intelligence.demo_data import default_runbooks
from nidaryx_intelligence.remediation import Approval, RemediationPolicy, RunbookRegistry


class RemediationPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = RemediationPolicy(RunbookRegistry(default_runbooks()))

    def test_rejects_viewer_approval(self) -> None:
        record = self.policy.approve(
            Approval(
                incident_id="incident-1",
                runbook_id="rb-reduce-ingress-load",
                actor="viewer",
                role=Role.VIEWER,
                parameters={"percentage": 25},
            )
        )

        self.assertEqual(record.decision, RemediationDecision.REJECTED)
        self.assertEqual(record.result["reason"], "role cannot approve remediation")

    def test_rejects_invalid_parameters(self) -> None:
        record = self.policy.approve(
            Approval(
                incident_id="incident-1",
                runbook_id="rb-reduce-ingress-load",
                actor="approver",
                role=Role.APPROVER,
                parameters={},
            )
        )

        self.assertEqual(record.decision, RemediationDecision.REJECTED)
        self.assertIn("missing required parameters", record.result["reason"])

    def test_approves_and_dry_run_executes_allow_listed_action(self) -> None:
        approved = self.policy.approve(
            Approval(
                incident_id="incident-1",
                runbook_id="rb-reduce-ingress-load",
                actor="approver",
                role=Role.APPROVER,
                parameters={"percentage": 25},
            )
        )
        executed = self.policy.execute(approved)

        self.assertEqual(approved.decision, RemediationDecision.APPROVED)
        self.assertEqual(executed.decision, RemediationDecision.EXECUTED)
        self.assertFalse(executed.result["executed"])


if __name__ == "__main__":
    unittest.main()
