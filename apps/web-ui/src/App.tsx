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
import type { Incident, OpsState, ServiceHealth, TelemetrySignal } from "./types/incidents";

const apiUrl = import.meta.env.VITE_NIDARYX_API_URL?.replace(/\/$/, "");

const healthySignals: TelemetrySignal[] = [
  { name: "request_rate", value: "110 req/min", baseline: "100-140 req/min", state: "live" },
  { name: "p95_latency_ms", value: "73 ms", baseline: "< 180 ms", state: "live" },
  { name: "error_rate", value: "0.2%", baseline: "< 1.0%", state: "live" },
  { name: "db_pool_utilization", value: "35%", baseline: "< 70%", state: "live" }
];

const degradedSignals: TelemetrySignal[] = [
  { name: "request_rate", value: "118 req/min", baseline: "100-140 req/min", state: "live" },
  { name: "p95_latency_ms", value: "420 ms", baseline: "< 180 ms", state: "degraded" },
  { name: "error_rate", value: "8.0%", baseline: "< 1.0%", state: "degraded" },
  { name: "db_pool_utilization", value: "96%", baseline: "< 70%", state: "degraded" }
];

async function fetchOpsState(): Promise<OpsState | null> {
  if (!apiUrl) return null;
  const response = await fetch(`${apiUrl}/ops/state`);
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

async function updateScenario(scenario: OpsState["scenario"]): Promise<OpsState | null> {
  if (!apiUrl) return null;
  const response = await fetch(`${apiUrl}/ops/scenario`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ scenario })
  });
  return response.ok ? response.json() : null;
}

export function App() {
  const [incident, setIncident] = useState<Incident | null>(apiUrl ? null : demoIncident);
  const [services, setServices] = useState<ServiceHealth[]>(apiUrl ? healthyServiceHealth : serviceHealth);
  const [signals, setSignals] = useState<TelemetrySignal[]>(apiUrl ? healthySignals : degradedSignals);
  const [source, setSource] = useState(apiUrl ? "connecting" : "local");
  const [scenario, setScenario] = useState<OpsState["scenario"]>(apiUrl ? "healthy" : "db_pool_saturation");
  const topCandidate = incident?.candidates[0] ?? null;
  const tiles = [
    { label: "Open incidents", value: incident ? "1" : "0", detail: incident ? `${incident.affected_services.length} services affected` : "system healthy", icon: AlertTriangle },
    { label: "Top RCA", value: topCandidate?.entity ?? "none", detail: topCandidate ? `${Math.round(topCandidate.confidence * 100)}% weighted evidence` : "waiting for anomaly", icon: DatabaseZap },
    { label: "MTTD", value: incident ? "20s" : "ready", detail: incident ? "inside 30s target" : "monitoring live telemetry", icon: Clock3 },
    { label: "Telemetry", value: incident ? "partial" : "live", detail: incident ? "trace present, logs pending" : "all services nominal", icon: Activity }
  ];

  const applyOpsState = (state: OpsState) => {
    setScenario(state.scenario);
    setServices(state.services);
    setSignals(state.signals);
    setIncident(state.incident);
    setSource("api");
  };

  useEffect(() => {
    let active = true;
    fetchOpsState()
      .then((state) => {
        if (!active) return;
        if (state) {
          applyOpsState(state);
        } else {
          setSource("local");
        }
      })
      .catch(() => {
        if (active) setSource("local");
      });
    return () => {
      active = false;
    };
  }, []);

  const changeScenario = (nextScenario: OpsState["scenario"]) => {
    updateScenario(nextScenario).then((state) => {
      if (state) applyOpsState(state);
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
          <span className="source-pill">{source === "api" ? "Telemetry API connected" : source === "connecting" ? "Connecting telemetry API" : "Local telemetry mode"}</span>
          <span>{incident ? "Last scored 20 seconds ago" : "No active incident"}</span>
        </div>
      </header>

      <section className="demo-controls" aria-label="Incident drill controls">
        <div>
          <p className="eyebrow">Production Incident Drill</p>
          <h2>{scenario === "healthy" ? "Checkout path is healthy" : "MongoDB pool saturation is active"}</h2>
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

      <section className="panel telemetry-panel" aria-labelledby="telemetry-title">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Telemetry Parameters</p>
            <h2 id="telemetry-title">Current signal window</h2>
          </div>
          <StatusBadge label={incident ? "degraded" : "live"} />
        </div>
        <div className="signal-grid">
          {signals.map((signal) => (
            <div className="signal-card" key={signal.name}>
              <span>{signal.name}</span>
              <strong>{signal.value}</strong>
              <p>baseline {signal.baseline}</p>
              <StatusBadge label={signal.state} />
            </div>
          ))}
        </div>
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
              <h2>Idle until telemetry crosses threshold</h2>
              <p className="summary-copy">Trigger DB Saturation to push latency, error rate, and pool utilization beyond baseline.</p>
            </section>
          )}
        </aside>
      </div>
    </AppShell>
  );
}
