
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileSearch,
  Building2,
  Files,
  ShieldCheck,
  Settings,
  HelpCircle,
  ChevronRight,
  Sparkles,
} from "lucide-react";

const navigation = [
  {
    title: "WORKSPACE",
    items: [
      {
        label: "Dashboard",
        path: "/",
        icon: LayoutDashboard,
      },
      {
        label: "Contract Analysis",
        path: "/contracts",
        icon: FileSearch,
      },
      {
        label: "Property Investigation",
        path: "/property",
        icon: Building2,
      },
      {
        label: "Reports",
        path: "/reports",
        icon: Files,
      },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <ShieldCheck size={23} />
        </div>

        <div>
          <h2>CLAUSEWISE</h2>
          <span>AI INTELLIGENCE</span>
        </div>
      </div>

      <div className="workspace-label">
        <span>MAIN MENU</span>
      </div>

      {navigation.map((section) => (
        <div className="sidebar-section" key={section.title}>
          <p className="sidebar-section-title">
            {section.title}
          </p>

          {section.items.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? "active" : ""}`
                }
              >
                <Icon size={18} strokeWidth={1.8} />
                <span>{item.label}</span>
                {item.path === "/property" && (
                  <span className="sidebar-new">NEW</span>
                )}
              </NavLink>
            );
          })}
        </div>
      ))}

      <div className="sidebar-spacer" />

      <div className="sidebar-promo">
        <div className="promo-icon">
          <Sparkles size={18} />
        </div>
        <h3>Intelligence that matters.</h3>
        <p>
          Investigate documents. Understand risks.
          Make informed decisions.
        </p>
      </div>

      <div className="sidebar-bottom">
        <button className="sidebar-bottom-link">
          <HelpCircle size={18} />
          <span>Help & Support</span>
        </button>

        <button className="sidebar-bottom-link">
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <div className="sidebar-profile">
          <div className="profile-avatar">CW</div>
          <div className="profile-details">
            <strong>Workspace</strong>
            <span>Personal account</span>
          </div>
          <ChevronRight size={16} />
        </div>
      </div>
    </aside>
  );
}
