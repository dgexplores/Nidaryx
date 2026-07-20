import { GitCommitHorizontal } from "lucide-react";
import type { TimelineEvent } from "../types/incidents";
import { StatusBadge } from "./StatusBadge";

interface EvidenceTimelineProps {
  events: TimelineEvent[];
}

export function EvidenceTimeline({ events }: EvidenceTimelineProps) {
  return (
    <section className="panel" aria-labelledby="timeline-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Evidence Timeline</p>
          <h2 id="timeline-title">Correlated anomaly path</h2>
        </div>
      </div>
      <ol className="timeline">
        {events.map((event) => (
          <li key={`${event.time}-${event.service}`}>
            <GitCommitHorizontal aria-hidden="true" size={18} />
            <div>
              <div className="timeline__meta">
                <span>{event.time}</span>
                <span>{event.service}</span>
                <StatusBadge label={event.state} />
              </div>
              <h3>{event.title}</h3>
              <p>{event.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

