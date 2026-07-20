import { Gauge } from "lucide-react";
import type { EvidenceScore, RCACandidate } from "../types/incidents";

interface RCAPanelProps {
  candidates: RCACandidate[];
}

const evidenceLabels: Record<keyof EvidenceScore, string> = {
  temporal: "Temporal",
  dependency: "Dependency",
  trace: "Trace",
  severity: "Severity",
  history: "History",
  data_quality_penalty: "Quality penalty"
};

export function RCAPanel({ candidates }: RCAPanelProps) {
  return (
    <section className="panel panel--sticky" id="rca" aria-labelledby="rca-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">RCA Ranking</p>
          <h2 id="rca-title">Probable origin</h2>
        </div>
        <Gauge size={20} aria-hidden="true" />
      </div>
      <div className="candidate-list">
        {candidates.map((candidate) => (
          <article className="candidate" key={candidate.entity}>
            <header>
              <span className="rank">#{candidate.rank}</span>
              <div>
                <h3>{candidate.entity}</h3>
                <p>{Math.round(candidate.confidence * 100)}% confidence</p>
              </div>
            </header>
            <div className="evidence-grid">
              {(Object.entries(candidate.evidence) as Array<[keyof EvidenceScore, number]>).map(([key, value]) => (
                <div className="evidence-meter" key={key}>
                  <span>{evidenceLabels[key]}</span>
                  <meter min="0" max="1" value={key === "data_quality_penalty" ? 1 - value : value} />
                </div>
              ))}
            </div>
            <ul className="signal-list">
              {candidate.supporting_signals.map((signal) => (
                <li key={signal}>{signal}</li>
              ))}
              {candidate.limitations.map((limitation) => (
                <li className="limitation" key={limitation}>{limitation}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
