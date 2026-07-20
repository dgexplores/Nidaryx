import { ArrowUpRight } from "lucide-react";
import type { Incident, ServiceHealth } from "../types/incidents";
import { StatusBadge } from "./StatusBadge";

interface IncidentTableProps {
  incident: Incident;
  services: ServiceHealth[];
}

export function IncidentTable({ incident, services }: IncidentTableProps) {
  return (
    <section className="panel" aria-labelledby="incident-queue-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Incident Queue</p>
          <h2 id="incident-queue-title">Active operational risk</h2>
        </div>
        <a className="icon-button" href="#rca" aria-label="Open incident detail">
          <ArrowUpRight size={18} aria-hidden="true" />
        </a>
      </div>
      <div className="incident-row" tabIndex={0}>
        <div>
          <strong>{incident.id}</strong>
          <span>{incident.affected_services.join(" / ")}</span>
        </div>
        <StatusBadge label={incident.severity} />
        <StatusBadge label={incident.status} />
        <span className="confidence">{Math.round(incident.candidates[0].confidence * 100)}% RCA</span>
      </div>
      <div className="service-table" role="table" aria-label="Service health">
        <div className="service-table__head" role="row">
          <span role="columnheader">Service</span>
          <span role="columnheader">State</span>
          <span role="columnheader">Latency</span>
          <span role="columnheader">Errors</span>
          <span role="columnheader">Owner</span>
        </div>
        {services.map((service) => (
          <div className="service-table__row" role="row" key={service.service}>
            <span role="cell">{service.service}</span>
            <span role="cell"><StatusBadge label={service.state} /></span>
            <span role="cell">{service.latency}</span>
            <span role="cell">{service.errorRate}</span>
            <span role="cell">{service.owner}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
