import { Check, ShieldAlert } from "lucide-react";
import type { Recommendation } from "../types/incidents";

interface RecommendationPanelProps {
  recommendation: Recommendation;
}

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
  return (
    <section className="panel" aria-labelledby="recommendation-title">
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
          <button className="primary-action">Request approval</button>
        </article>
      ))}
    </section>
  );
}

