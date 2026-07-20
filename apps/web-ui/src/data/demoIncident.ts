import type { Incident, ServiceHealth } from "../types/incidents";

export const demoIncident: Incident = {
  id: "incident_6d91a2d28e11",
  status: "open",
  severity: "critical",
  opened_at: "2026-07-20T09:00:00Z",
  affected_services: ["api-gateway", "checkout-api", "order-service", "mongodb"],
  candidates: [
    {
      entity: "mongodb",
      rank: 1,
      confidence: 0.82,
      evidence: {
        temporal: 1,
        dependency: 1,
        trace: 0.75,
        severity: 0.84,
        history: 0.9,
        data_quality_penalty: 0
      },
      supporting_signals: [
        "candidate anomaly is earliest in the correlated window",
        "candidate is upstream of affected service symptoms",
        "historical incidents support this candidate"
      ],
      limitations: []
    },
    {
      entity: "order-service",
      rank: 2,
      confidence: 0.61,
      evidence: {
        temporal: 0.55,
        dependency: 0.65,
        trace: 0.75,
        severity: 0.74,
        history: 0.3,
        data_quality_penalty: 0
      },
      supporting_signals: ["candidate is anomalous during the incident window", "candidate is directly affected"],
      limitations: []
    },
    {
      entity: "api-gateway",
      rank: 3,
      confidence: 0.39,
      evidence: {
        temporal: 0.55,
        dependency: 0.65,
        trace: 0.75,
        severity: 0.45,
        history: 0,
        data_quality_penalty: 0
      },
      supporting_signals: ["candidate is directly affected"],
      limitations: ["dependency evidence suggests downstream symptom propagation"]
    }
  ],
  recommendation: {
    summary: "Investigate mongodb first; remediation remains approval-gated.",
    investigation_steps: [
      "Inspect telemetry for mongodb before changing downstream services.",
      "Compare current dominant anomaly features with trace and log context.",
      "Check data-quality flags before treating the RCA ranking as actionable.",
      "Review matching incident incident_previous_db_pool_saturation and confirm whether its resolution still applies."
    ],
    actions: [
      {
        runbook_id: "rb-reduce-ingress-load",
        title: "Reduce ingress load by percentage",
        recommendation_type: "remediation",
        action_identifier: "traffic.load.reduce",
        preconditions: ["Environment has an approved traffic-control policy.", "Incident has active saturation evidence."],
        verification: ["Request rate returns within baseline band."],
        rollback: ["Restore the previous load-generator rate."],
        enabled: true
      }
    ],
    evidence_refs: ["mongodb", "order-service", "api-gateway"],
    similar_incident_refs: ["incident_previous_db_pool_saturation"]
  },
  timeline: [
    {
      time: "08:54:40",
      service: "mongodb",
      title: "Database pool utilization crossed anomaly threshold",
      detail: "db_pool_utilization=0.96, p95_latency_ms=420, trace=trace-checkout-001",
      state: "live"
    },
    {
      time: "08:55:00",
      service: "order-service",
      title: "Checkout latency and error ratio deviated together",
      detail: "p95_latency_ms=390, error_rate=8%, downstream symptom linked to mongodb",
      state: "live"
    },
    {
      time: "08:55:00",
      service: "api-gateway",
      title: "Client-facing errors detected",
      detail: "correlator merged gateway symptom into the existing dependency incident",
      state: "partial"
    }
  ]
};

export const serviceHealth: ServiceHealth[] = [
  { service: "api-gateway", state: "partial", latency: "360 ms", errorRate: "5.0%", owner: "edge-platform" },
  { service: "checkout-api", state: "partial", latency: "180 ms", errorRate: "1.7%", owner: "checkout-platform" },
  { service: "order-service", state: "degraded", latency: "390 ms", errorRate: "8.0%", owner: "checkout" },
  { service: "mongodb", state: "degraded", latency: "420 ms", errorRate: "3.0%", owner: "data-platform" }
];

export const healthyServiceHealth: ServiceHealth[] = [
  { service: "api-gateway", state: "live", latency: "42 ms", errorRate: "0.1%", owner: "edge-platform" },
  { service: "checkout-api", state: "live", latency: "55 ms", errorRate: "0.0%", owner: "checkout-platform" },
  { service: "order-service", state: "live", latency: "73 ms", errorRate: "0.2%", owner: "checkout" },
  { service: "mongodb", state: "live", latency: "31 ms", errorRate: "0.0%", owner: "data-platform" }
];
