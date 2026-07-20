import { Activity, AlertTriangle, Clock3, DatabaseZap } from "lucide-react";
import { motion } from "framer-motion";
import { AppShell } from "./components/AppShell";
import { EvidenceTimeline } from "./components/EvidenceTimeline";
import { IncidentTable } from "./components/IncidentTable";
import { RCAPanel } from "./components/RCAPanel";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { StatusBadge } from "./components/StatusBadge";
import { demoIncident, serviceHealth } from "./data/demoIncident";

const tiles = [
  { label: "Open incidents", value: "1", detail: "3 anomalies merged", icon: AlertTriangle },
  { label: "Top RCA", value: "mongodb", detail: "82% weighted evidence", icon: DatabaseZap },
  { label: "MTTD", value: "20s", detail: "inside 30s target", icon: Clock3 },
  { label: "Telemetry", value: "partial", detail: "trace present, logs pending", icon: Activity }
];

export function App() {
  return (
    <AppShell>
      <header className="topbar">
        <div>
          <p className="eyebrow">Live Incident Workspace</p>
          <h1>Operational intelligence</h1>
        </div>
        <div className="topbar__state">
          <StatusBadge label="critical" />
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
          <IncidentTable incident={demoIncident} services={serviceHealth} />
          <EvidenceTimeline events={demoIncident.timeline} />
          <RecommendationPanel recommendation={demoIncident.recommendation} />
        </div>
        <aside className="side-column" aria-label="Root cause evidence">
          <RCAPanel candidates={demoIncident.candidates} />
        </aside>
      </div>
    </AppShell>
  );
}

