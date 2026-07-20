import { Check, ShieldAlert } from "lucide-react";
import { useState } from "react";
import type { Recommendation } from "../types/incidents";

interface RecommendationPanelProps {
  recommendation: Recommendation;
}

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
  const [requestedRunbook, setRequestedRunbook] = useState<string | null>(null);

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
          <button className="primary-action" onClick={() => setRequestedRunbook(action.runbook_id)}>
            {requestedRunbook === action.runbook_id ? "Approval queued" : "Request approval"}
          </button>
        </article>
      ))}
    </section>
  );
}
