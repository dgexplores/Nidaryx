import { AlertTriangle, CheckCircle2, Clock3, RadioTower } from "lucide-react";
import type { DataState, IncidentStatus, Severity } from "../types/incidents";

interface StatusBadgeProps {
  label: DataState | IncidentStatus | Severity;
}

const iconByLabel = {
  live: RadioTower,
  stale: Clock3,
  degraded: AlertTriangle,
  partial: AlertTriangle,
  open: RadioTower,
  investigating: Clock3,
  mitigated: CheckCircle2,
  resolved: CheckCircle2,
  closed: CheckCircle2,
  info: RadioTower,
  warning: AlertTriangle,
  critical: AlertTriangle
};

export function StatusBadge({ label }: StatusBadgeProps) {
  const Icon = iconByLabel[label];
  return (
    <span className={`status-badge status-badge--${label}`}>
      <Icon aria-hidden="true" size={15} strokeWidth={2.2} />
      {label.replace("_", " ")}
    </span>
  );
}

