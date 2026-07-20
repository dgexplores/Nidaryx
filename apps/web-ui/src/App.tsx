import { Activity, AlertTriangle, CheckCircle2, Clock3, DatabaseZap, PlayCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { AppShell } from "./components/AppShell";
import { EvidenceTimeline } from "./components/EvidenceTimeline";
import { IncidentTable } from "./components/IncidentTable";
import { RCAPanel } from "./components/RCAPanel";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { StatusBadge } from "./components/StatusBadge";
import { demoIncident, healthyServiceHealth, serviceHealth } from "./data/demoIncident";
import type { DemoState, Incident, ServiceHealth } from "./types/incidents";

const apiUrl = import.meta.env.VITE_NIDARYX_API_URL?.replace(/\/$/, "");

async function fetchDemoState(): Promise<DemoState | null> {
  if (!apiUrl) return null;
  const response = await fetch(`${apiUrl}/demo/state`);
  if (!response.ok) return null;
  const payload = await response.json();
  const item = payload.incident;
  if (!item) return { ...payload, incident: null };
  return {
    ...payload,
    incident: {
      ...demoIncident,
      ...item,
      recommendation: item.recommendation ?? demoIncident.recommendation,
      timeline: item.timeline ?? demoIncident.timeline
    }
  };
}

async function updateScenario(scenario: DemoState["scenario"]): Promise<DemoState | null> {
  if (!apiUrl) return null;
  const response = await fetch(`${apiUrl}/demo/scenario`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ scenario })
  });
  return response.ok ? response.json() : null;
}

export function App() {
  const [incident, setIncident] = useState<Incident | null>(apiUrl ? null : demoIncident);
  const [services, setServices] = useState<ServiceHealth[]>(apiUrl ? healthyServiceHealth : serviceHealth);
  const [source, setSource] = useState(apiUrl ? "connecting" : "demo");
  const [scenario, setScenario] = useState<DemoState["scenario"]>(apiUrl ? "healthy" : "db_pool_saturation");
  const topCandidate = incident?.candidates[0] ?? null;
  const tiles = [
    { label: "Open incidents", value: incident ? "1" : "0", detail: incident ? `${incident.affected_services.length} services affected` : "system healthy", icon: AlertTriangle },
    { label: "Top RCA", value: topCandidate?.entity ?? "none", detail: topCandidate ? `${Math.round(topCandidate.confidence * 100)}% weighted evidence` : "waiting for anomaly", icon: DatabaseZap },
    { label: "MTTD", value: incident ? "20s" : "ready", detail: incident ? "inside 30s target" : "monitoring live scenario", icon: Clock3 },
    { label: "Telemetry", value: incident ? "partial" : "live", detail: incident ? "trace present, logs pending" : "all services nominal", icon: Activity }
  ];

  const applyDemoState = (state: DemoState) => {
    setScenario(state.scenario);
    setServices(state.services);
    setIncident(state.incident);
    setSource("api");
  };

  useEffect(() => {
    let active = true;
    fetchDemoState()
      .then((state) => {
        if (!active) return;
        if (state) {
          applyDemoState(state);
        } else {
          setSource("demo");
        }
      })
      .catch(() => {
        if (active) setSource("demo");
      });
    return () => {
      active = false;
    };
  }, []);

  const changeScenario = (nextScenario: DemoState["scenario"]) => {
    updateScenario(nextScenario).then((state) => {
      if (state) applyDemoState(state);
    });
  };

  return (
    <AppShell>
      <header className="topbar">
        <div>
          <p className="eyebrow">Live Incident Workspace</p>
          <h1>Operational intelligence</h1>
        </div>
        <div className="topbar__state">
          <StatusBadge label={incident?.severity ?? "info"} />
          <span className="source-pill">{source === "api" ? "API connected" : source === "connecting" ? "Connecting API" : "Demo fallback"}</span>
          <span>{incident ? "Last scored 20 seconds ago" : "No active incident"}</span>
        </div>
      </header>

      <section className="demo-controls" aria-label="Controlled incident controls">
        <div>
          <p className="eyebrow">Controlled Problem</p>
          <h2>{scenario === "healthy" ? "System is healthy" : "DB pool saturation is active"}</h2>
        </div>
        <div className="demo-controls__actions">
          <button type="button" className="control-button control-button--danger" onClick={() => changeScenario("db_pool_saturation")}>
            <PlayCircle aria-hidden="true" size={18} />
            Trigger DB Saturation
          </button>
          <button type="button" className="control-button" onClick={() => changeScenario("healthy")}>
            <CheckCircle2 aria-hidden="true" size={18} />
            Resolve
          </button>
        </div>
      </section>

      <section className="status-strip" aria-label="Current pipeline state">
        {(incident
          ? ["features ok", "baseline score high", "correlation merged", "rca ranked", "approval gated"]
          : ["features ok", "baseline normal", "no correlation needed", "rca idle", "approval idle"]
        ).map((item) => (
          <span key={item}>{item}</span>
        ))}
      </section>

      <section className="metric-grid" aria-label="Incident metrics">
        {tiles.map((tile, index) => {
          const Icon = tile.icon;
          return (
            <motion.article
              className="metric-tile"
              key={tile.label}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.18, delay: index * 0.03 }}
            >
              <Icon aria-hidden="true" size={20} />
              <span>{tile.label}</span>
              <strong>{tile.value}</strong>
              <p>{tile.detail}</p>
            </motion.article>
          );
        })}
      </section>

      <div className="content-grid">
        <div className="main-column">
          {incident ? (
            <>
              <IncidentTable incident={incident} services={services} />
              <EvidenceTimeline events={incident.timeline} />
              <RecommendationPanel recommendation={incident.recommendation} />
            </>
          ) : (
            <section className="panel" aria-labelledby="healthy-title">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Incident Queue</p>
                  <h2 id="healthy-title">No active operational risk</h2>
                </div>
                <StatusBadge label="live" />
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
                    <strong role="cell">{service.service}</strong>
                    <span role="cell"><StatusBadge label={service.state} /></span>
                    <span role="cell">{service.latency}</span>
                    <span role="cell">{service.errorRate}</span>
                    <span role="cell">{service.owner}</span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
        <aside className="side-column" aria-label="Root cause evidence">
          {incident ? (
            <RCAPanel candidates={incident.candidates} />
          ) : (
            <section className="panel panel--sticky">
              <p className="eyebrow">Root Cause Evidence</p>
              <h2>Idle until a real scenario is triggered</h2>
              <p className="summary-copy">Click Trigger DB Saturation to create a controlled fault and watch Nidaryx open an incident.</p>
            </section>
          )}
        </aside>
      </div>
    </AppShell>
  );
}
