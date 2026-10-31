
import {
  Bell,
  Search,
  ChevronDown,
  Command,
} from "lucide-react";

export default function Topbar() {
  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Workspace</span>
        <span className="breadcrumb-divider">/</span>
        <strong>Overview</strong>
      </div>

      <div className="topbar-actions">
        <div className="topbar-search">
          <Search size={16} />
          <span>Search investigations...</span>
          <kbd>
            <Command size={11} /> K
          </kbd>
        </div>

        <button className="notification-button" aria-label="Notifications">
          <Bell size={19} />
          <span className="notification-dot" />
        </button>

        <button className="topbar-user">
          <div className="topbar-avatar">CW</div>
          <ChevronDown size={15} />
        </button>
      </div>
    </header>
  );
}
