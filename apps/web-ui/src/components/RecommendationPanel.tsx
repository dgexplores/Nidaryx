import { Check, ShieldAlert } from "lucide-react";
import { useState } from "react";
import type { Recommendation, RemediationApprovalResult } from "../types/incidents";

interface RecommendationPanelProps {
  recommendation: Recommendation;
  incidentId: string;
  onRequestApproval: (runbookId: string) => Promise<RemediationApprovalResult>;
}

export function RecommendationPanel({ recommendation, incidentId, onRequestApproval }: RecommendationPanelProps) {
  const [requestedRunbook, setRequestedRunbook] = useState<string | null>(null);
  const [result, setResult] = useState<RemediationApprovalResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const requestApproval = async (runbookId: string) => {
    setRequestedRunbook(runbookId);
    setError(null);
    try {
      setResult(await onRequestApproval(runbookId));
    } catch {
      setError("Approval API unavailable");
    }
  };

  return (
    <section className="panel" id="runbooks" aria-labelledby="recommendation-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Recommendation</p>
          <h2 id="recommendation-title">Investigation before action</h2>
        </div>
      </div>
      <p className="summary-copy">{recommendation.summary}</p>
      <ol className="check-list">
        {recommendation.investigation_steps.map((step) => (
          <li key={step}>
            <Check aria-hidden="true" size={17} />
            <span>{step}</span>
          </li>
        ))}
      </ol>
      {recommendation.actions.map((action) => (
        <article className="runbook-action" key={action.runbook_id}>
          <header>
            <ShieldAlert aria-hidden="true" size={20} />
            <div>
              <h3>{action.title}</h3>
              <p>{action.action_identifier}</p>
            </div>
          </header>
          <dl>
            <div>
              <dt>Preconditions</dt>
              <dd>{action.preconditions.join(" ")}</dd>
            </div>
            <div>
              <dt>Verification</dt>
              <dd>{action.verification.join(" ")}</dd>
            </div>
            <div>
              <dt>Rollback</dt>
              <dd>{action.rollback.join(" ")}</dd>
            </div>
          </dl>
          <button className="primary-action" onClick={() => requestApproval(action.runbook_id)} disabled={!action.action_identifier}>
            {!action.action_identifier ? "Investigation only" : requestedRunbook === action.runbook_id ? "Approval requested" : "Request approval"}
          </button>
        </article>
      ))}
      {(result || error) && (
        <div className="audit-result" role="status">
          <span>Incident {incidentId}</span>
          <strong>{result?.execution?.decision ?? result?.approval.decision ?? error}</strong>
          {result?.execution ? <p>Dry-run action: {result.execution.action_identifier}</p> : null}
        </div>
      )}
    </section>
  );
}
