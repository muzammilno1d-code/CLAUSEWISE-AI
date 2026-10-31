
import {
  FileText,
  SearchCheck,
  ShieldAlert,
  CheckCircle2,
  ArrowUpRight,
  FileSearch,
  Building2,
  Plus,
  Clock3,
  ChevronRight,
} from "lucide-react";

import StatCard from "../components/StatCard";

export default function Dashboard() {
  return (
    <div className="page-container">
      <section className="dashboard-welcome">
        <div>
          <div className="welcome-eyebrow">
            <span className="status-indicator" />
            YOUR INTELLIGENCE WORKSPACE
          </div>

          <h1>
            Investigate with <span>confidence.</span>
          </h1>

          <p>
            Understand documents, uncover potential risks,
            and make better-informed decisions.
          </p>
        </div>

        <div className="welcome-decoration">
          <ShieldAlert size={75} strokeWidth={0.8} />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Workspace overview</h2>
            <p>Your investigation activity at a glance.</p>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard
            title="Documents analysed"
            value="—"
            description="No completed analyses yet"
            icon={FileText}
            color="green"
          />

          <StatCard
            title="Potential risks"
            value="—"
            description="Findings will appear here"
            icon={ShieldAlert}
            color="orange"
          />

          <StatCard
            title="Investigations"
            value="—"
            description="Your investigation history"
            icon={SearchCheck}
            color="blue"
          />

          <StatCard
            title="Reports generated"
            value="—"
            description="Exported investigation reports"
            icon={CheckCircle2}
            color="purple"
          />
        </div>
        <p className="data-note">
          Statistics will be populated from actual investigation data
          once history tracking is implemented.
        </p>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>Start an investigation</h2>
            <p>Choose the type of document you want to examine.</p>
          </div>
        </div>

        <div className="investigation-grid">
          <div className="investigation-card contract-card">
            <div className="investigation-icon">
              <FileSearch size={24} />
            </div>

            <span className="card-kicker">CONTRACT INTELLIGENCE</span>
            <h3>Analyse a contract</h3>
            <p>
              Examine clauses, identify potential risks,
              discover inconsistencies, and review recommendations.
            </p>

            <a href="/contracts" className="investigation-action">
              Start contract analysis
              <ArrowUpRight size={17} />
            </a>
          </div>

          <div className="investigation-card property-card">
            <div className="investigation-icon">
              <Building2 size={24} />
            </div>

            <span className="card-kicker">PROPERTY INTELLIGENCE</span>
            <h3>Investigate property documents</h3>
            <p>
              Extract property details and compare sale documents
              with encumbrance-related records.
            </p>

            <a href="/property" className="investigation-action">
              Start property investigation
              <ArrowUpRight size={17} />
            </a>
          </div>
        </div>
      </section>

      <section className="dashboard-section recent-section">
        <div className="section-heading">
          <div>
            <h2>Recent investigations</h2>
            <p>Your latest document reviews.</p>
          </div>
        </div>

        <div className="empty-state">
          <div className="empty-state-icon">
            <Clock3 size={25} />
          </div>
          <h3>No investigations yet</h3>
          <p>
            Your completed investigations will appear here.
            Start by uploading a document.
          </p>
        </div>
      </section>

      <footer className="dashboard-footer">
        <span>CLAUSEWISE AI</span>
        <span>
          Preliminary document intelligence · Professional review may be required
        </span>
      </footer>
    </div>
  );
}
