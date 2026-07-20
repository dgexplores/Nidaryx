export type Severity = "info" | "warning" | "critical";
export type IncidentStatus = "open" | "investigating" | "mitigated" | "resolved" | "closed";
export type DataState = "live" | "stale" | "degraded" | "partial";

export interface EvidenceScore {
  temporal: number;
  dependency: number;
  trace: number;
  severity: number;
  history: number;
  data_quality_penalty: number;
}

export interface RCACandidate {
  entity: string;
  rank: number;
  confidence: number;
  evidence: EvidenceScore;
  supporting_signals: string[];
  limitations: string[];
}

export interface RunbookAction {
  runbook_id: string;
  title: string;
  recommendation_type: "investigation" | "remediation";
  action_identifier: string | null;
  preconditions: string[];
  verification: string[];
  rollback: string[];
  enabled: boolean;
}

export interface Recommendation {
  summary: string;
  investigation_steps: string[];
  actions: RunbookAction[];
  evidence_refs: string[];
  similar_incident_refs: string[];
}

export interface TimelineEvent {
  time: string;
  service: string;
  title: string;
  detail: string;
  state: DataState;
}

export interface Incident {
  id: string;
  status: IncidentStatus;
  severity: Severity;
  opened_at: string;
  affected_services: string[];
  candidates: RCACandidate[];
  recommendation: Recommendation;
  timeline: TimelineEvent[];
}

export interface ServiceHealth {
  service: string;
  state: DataState;
  latency: string;
  errorRate: string;
  owner: string;
}

export interface DemoState {
  scenario: "healthy" | "db_pool_saturation";
  active: boolean;
  services: ServiceHealth[];
  incident: Incident | null;
}
