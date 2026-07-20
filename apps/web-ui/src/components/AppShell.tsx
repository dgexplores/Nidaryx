import { Activity, DatabaseZap, GitBranch, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";

interface AppShellProps {
  children: ReactNode;
}

const navItems = [
  { label: "Incidents", icon: Activity, href: "#incidents" },
  { label: "Topology", icon: GitBranch, href: "#topology" },
  { label: "Runbooks", icon: ShieldCheck, href: "#runbooks" },
  { label: "Models", icon: DatabaseZap, href: "#models" }
];

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">AO</span>
          <span>Nidaryx</span>
        </div>
        <nav className="nav-list">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <a className={index === 0 ? "nav-item nav-item--active" : "nav-item"} href={item.href} key={item.label}>
                <Icon aria-hidden="true" size={18} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </aside>
      <main className="workspace">{children}</main>
    </div>
  );
}
