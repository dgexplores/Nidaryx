import { Activity, AlertTriangle, Clock3, DatabaseZap } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { AppShell } from "./components/AppShell";
import { EvidenceTimeline } from "./components/EvidenceTimeline";
import { IncidentTable } from "./components/IncidentTable";
import { RCAPanel } from "./components/RCAPanel";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { StatusBadge } from "./components/StatusBadge";
import { demoIncident, serviceHealth } from "./data/demoIncident";
import type { Incident } from "./types/incidents";

const apiUrl = import.meta.env.VITE_NIDARYX_API_URL?.replace(/\/$/, "");

async function fetchIncident(): Promise<Incident | null> {
  if (!apiUrl) return null;
  const response = await fetch(`${apiUrl}/incidents`);
  if (!response.ok) return null;
  const payload = await response.json();
  const item = payload.items?.[0];
  if (!item) return null;
  return {
    ...demoIncident,
    ...item,
    recommendation: item.recommendation ?? demoIncident.recommendation,
    timeline: item.timeline ?? demoIncident.timeline
  };
}

export function App() {
  const [incident, setIncident] = useState<Incident>(demoIncident);
  const [source, setSource] = useState(apiUrl ? "connecting" : "demo");
  const topCandidate = incident.candidates[0] ?? demoIncident.candidates[0];
  const tiles = [
    { label: "Open incidents", value: "1", detail: `${incident.affected_services.length} services affected`, icon: AlertTriangle },
    { label: "Top RCA", value: topCandidate.entity, detail: `${Math.round(topCandidate.confidence * 100)}% weighted evidence`, icon: DatabaseZap },
    { label: "MTTD", value: "20s", detail: "inside 30s target", icon: Clock3 },
    { label: "Telemetry", value: "partial", detail: "trace present, logs pending", icon: Activity }
  ];

  useEffect(() => {
    let active = true;
    fetchIncident()
      .then((nextIncident) => {
        if (!active) return;
        if (nextIncident) {
          setIncident(nextIncident);
          setSource("api");
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

  return (
    <AppShell>
      <header className="topbar">
        <div>
          <p className="eyebrow">Live Incident Workspace</p>
          <h1>Operational intelligence</h1>
        </div>
        <div className="topbar__state">
          <StatusBadge label="critical" />
          <span className="source-pill">{source === "api" ? "API connected" : source === "connecting" ? "Connecting API" : "Demo fallback"}</span>
          <span>Last scored 20 seconds ago</span>
        </div>
      </header>

      <section className="status-strip" aria-label="Current pipeline state">
        {["features ok", "baseline score high", "correlation merged", "rca ranked", "approval gated"].map((item) => (
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
          <IncidentTable incident={incident} services={serviceHealth} />
          <EvidenceTimeline events={incident.timeline} />
          <RecommendationPanel recommendation={incident.recommendation} />
        </div>
        <aside className="side-column" aria-label="Root cause evidence">
          <RCAPanel candidates={incident.candidates} />
        </aside>
      </div>
    </AppShell>
  );
}
