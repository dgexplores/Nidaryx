import { Activity, DatabaseZap, GitBranch, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";

interface AppShellProps {
  children: ReactNode;
}

const navItems = [
  { label: "Incidents", icon: Activity },
  { label: "Topology", icon: GitBranch },
  { label: "Runbooks", icon: ShieldCheck },
  { label: "Models", icon: DatabaseZap }
];

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">AO</span>
          <span>TraceSentry</span>
        </div>
        <nav className="nav-list">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button className={index === 0 ? "nav-item nav-item--active" : "nav-item"} key={item.label}>
                <Icon aria-hidden="true" size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="workspace">{children}</main>
    </div>
  );
}

