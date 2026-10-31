
import { useState } from "react";
import {
  FileText,
  Upload,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Languages,
  FileSearch,
  RefreshCw,
  Clock3,
  Scale,
  Search,
  ClipboardList,
  Info,
  Download,
  Layers3,
} from "lucide-react";

import { uploadContract } from "../services/api";

const formatValue = (value, fallback = "Not available") =>
  value === null || value === undefined || value === "" ? fallback : value;

function MetricCard({ icon: Icon, label, value, detail }) {
  return (
    <div className="ca-metric-card">
      <div className="ca-metric-top">
        <span className="ca-metric-icon"><Icon size={19} /></span>
        <span className="ca-metric-label">{label}</span>
      </div>
      <strong className="ca-metric-value">{value}</strong>
      {detail && <span className="ca-metric-detail">{detail}</span>}
    </div>
  );
}

function SectionHeading({ eyebrow, title, count }) {
  return (
    <div className="ca-section-heading">
      <div>
        {eyebrow && <span className="ca-section-eyebrow">{eyebrow}</span>}
        <h3>{title}</h3>
      </div>
      {count !== undefined && (
        <span className="ca-section-count">{count}</span>
      )}
    </div>
  );
}

function StatusBadge({ value }) {
  const normalized = String(value || "NOT ASSESSED").toUpperCase();
  const className = normalized.toLowerCase().replaceAll(" ", "-");

  return (
    <span className={`ca-status-badge ${className}`}>
      {normalized.replaceAll("_", " ")}
    </span>
  );
}

function ClauseCard({ clause, index, expanded, onToggle }) {
  const observations = clause.observations || [];

  return (
    <article className={`ca-clause-card ${expanded ? "expanded" : ""}`}>
      <button
        type="button"
        className="ca-clause-trigger"
        onClick={onToggle}
        aria-expanded={expanded}
      >
        <div className="ca-clause-main">
          <span className="ca-clause-index">
            {String(index + 1).padStart(2, "0")}
          </span>

          <div className="ca-clause-title">
            <h4>{formatValue(clause.heading, "Untitled clause")}</h4>
            <span>{formatValue(clause.category, "Uncategorized")}</span>
          </div>
        </div>

        <div className="ca-clause-right">
          <StatusBadge value={clause.risk_level} />
          {expanded ? <ChevronUp size={19} /> : <ChevronDown size={19} />}
        </div>
      </button>

      {expanded && (
        <div className="ca-clause-content">
          <div className="ca-clause-meta">
            <span><FileText size={14} /> Page {formatValue(clause.start_page)}</span>
            <span><Layers3 size={14} /> {formatValue(clause.category)}</span>
            <span><Info size={14} /> Clause {formatValue(clause.clause_number)}</span>
          </div>

          <div className="ca-evidence-panel">
            <div className="ca-content-label">
              <FileText size={16} />
              <h5>Original clause text</h5>
            </div>
            <blockquote>
              {formatValue(
                clause.original_content,
                "No original clause text was returned by the extractor."
              )}
            </blockquote>
          </div>

          <div className="ca-observations-panel">
            <div className="ca-content-label">
              <Search size={16} />
              <h5>Analysis observations</h5>
            </div>

            {observations.length > 0 ? (
              observations.map((observation, i) => (
                <div className="ca-observation" key={i}>
                  <CheckCircle2 size={16} />
                  <p>{observation}</p>
                </div>
              ))
            ) : (
              <div className="ca-inline-empty">
                No observations were returned by the current analysis checks.
                This does not establish that the clause is risk-free.
              </div>
            )}
          </div>

          <div className="ca-clause-footnote">
            <Info size={15} />
            A clause status represents the checks performed, not a legal
            determination of enforceability or safety.
          </div>
        </div>
      )}
    </article>
  );
}

export default function ContractAnalysis() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedClause, setExpandedClause] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  function handleFileChange(event) {
    const selected = event.target.files?.[0];

    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF document.");
      event.target.value = "";
      return;
    }

    setFile(selected);
    setResult(null);
    setError("");
  }

  async function handleAnalyse() {
    if (!file) {
      setError("Please select a contract PDF first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadContract(file);
      setResult(data);
      setExpandedClause(null);
      setSearchTerm("");
    } catch (err) {
      setError(err.message || "Contract analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  function resetAnalysis() {
    setResult(null);
    setFile(null);
    setError("");
    setExpandedClause(null);
    setSearchTerm("");
  }

  const clauses = result?.analyzed_clauses || [];
  const findings = result?.cross_clause_findings || [];
  const recommendations = result?.recommendations || [];

  const filteredClauses = clauses.filter((clause) => {
    const search = searchTerm.toLowerCase();

    return (
      String(clause.heading || "").toLowerCase().includes(search) ||
      String(clause.category || "").toLowerCase().includes(search) ||
      String(clause.original_content || "").toLowerCase().includes(search)
    );
  });

  const riskSummary = result?.risk_summary || {};

  return (
    <div className="page-container-inner ca-page">
      <div className="page-heading ca-page-heading">
        <div>
          <span className="page-eyebrow">DOCUMENT INTELLIGENCE</span>
          <h1>Contract Analysis</h1>
          <p>
            Investigate contract clauses, understand obligations and identify
            potential concerns before making decisions.
          </p>
        </div>
      </div>

      {!result && (
        <section className="ca-upload-layout">
          <div className="ca-upload-panel">
            <div className="ca-upload-icon">
              <FileSearch size={28} />
            </div>

            <span className="ca-upload-eyebrow">START AN INVESTIGATION</span>
            <h2>Upload your contract</h2>
            <p>
              Select an employment, rental, business, service or NDA agreement
              in PDF format.
            </p>

            <label className="ca-dropzone">
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                hidden
              />
              <Upload size={27} />
              <strong>Choose a PDF file</strong>
              <span>Browse your device to select a document</span>
              <small>PDF documents only</small>
            </label>

            {file && (
              <div className="ca-selected-file">
                <div className="ca-file-icon"><FileText size={20} /></div>
                <div className="ca-file-info">
                  <strong>{file.name}</strong>
                  <span>{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    setError("");
                  }}
                >
                  Remove
                </button>
              </div>
            )}

            {error && (
              <div className="ca-error-message">
                <AlertTriangle size={17} />
                {error}
              </div>
            )}

            <button
              type="button"
              className="primary-button ca-analyse-button"
              onClick={handleAnalyse}
              disabled={!file || loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={17} className="spin" />
                  Analysing document...
                </>
              ) : (
                <>
                  <FileSearch size={17} />
                  Analyse contract
                </>
              )}
            </button>

            <div className="ca-upload-note">
              <ShieldCheck size={16} />
              Your document is processed for preliminary AI-assisted review.
            </div>
          </div>

          <aside className="ca-upload-sidebar">
            <div className="ca-sidebar-card">
              <span className="ca-sidebar-icon"><ClipboardList size={20} /></span>
              <h3>What will be investigated?</h3>
              <ul>
                <li>Contract clause extraction</li>
                <li>Potential risk indicators</li>
                <li>Cross-clause consistency checks</li>
                <li>Important terms and obligations</li>
                <li>Reviewer recommendations</li>
              </ul>
            </div>

            <div className="ca-sidebar-note">
              <ShieldCheck size={18} />
              <div>
                <strong>Evidence-first analysis</strong>
                <p>
                  Findings should be supported by the original document text.
                  AI output requires human review.
                </p>
              </div>
            </div>
          </aside>
        </section>
      )}

      {result && (
        <div className="ca-results">
          <div className="ca-results-header">
            <div className="ca-results-heading">
              <div className="ca-completed-icon">
                <CheckCircle2 size={21} />
              </div>
              <div>
                <span className="ca-section-eyebrow">INVESTIGATION RESULTS</span>
                <h2>{formatValue(result.filename, "Contract document")}</h2>
                <p>{formatValue(result.status, "Analysis completed")}</p>
              </div>
            </div>

            <button
              type="button"
              className="secondary-button ca-another-button"
              onClick={resetAnalysis}
            >
              <RefreshCw size={16} />
              New investigation
            </button>
          </div>

          <div className="ca-document-strip">
            <div><FileText size={16} /><span>{formatValue(result.filename)}</span></div>
            <div><Clock3 size={16} /><span>{formatValue(result.total_pages, "—")} pages</span></div>
            <div><Languages size={16} /><span>{formatValue(result.language_detection?.detected_language, "Unknown")}</span></div>
            <div><ShieldCheck size={16} /><span>{formatValue(result.extraction_quality_summary?.overall_status, "Not assessed")}</span></div>
          </div>

          <section className="ca-metrics-grid">
            <MetricCard
              icon={FileSearch}
              label="Clauses extracted"
              value={result.total_clauses ?? clauses.length}
              detail="Returned by extraction"
            />
            <MetricCard
              icon={AlertTriangle}
              label="High concern flags"
              value={riskSummary.HIGH ?? 0}
              detail="Configured checks only"
            />
            <MetricCard
              icon={Scale}
              label="Moderate concern flags"
              value={riskSummary.MEDIUM ?? 0}
              detail="Configured checks only"
            />
            <MetricCard
              icon={ClipboardList}
              label="Cross-clause findings"
              value={findings.length}
              detail="Potential inconsistencies"
            />
          </section>

          <section className="ca-result-panel">
            <SectionHeading eyebrow="DOCUMENT PROFILE" title="Document classification" />

            <div className="ca-classification-grid">
              <div className="ca-classification-main">
                <span>IDENTIFIED DOCUMENT TYPE</span>
                <strong>
                  {formatValue(
                    result.document_classification?.document_type,
                    "Not classified"
                  )}
                </strong>
                <StatusBadge
                  value={result.document_classification?.status || "UNKNOWN"}
                />
              </div>

              <div className="ca-classification-stat">
                <span>Classification score</span>
                <strong>
                  {formatValue(result.document_classification?.classification_score)}
                </strong>
              </div>

              <div className="ca-classification-stat">
                <span>Language confidence</span>
                <strong>
                  {Math.round(
                    (result.language_detection?.confidence || 0) * 100
                  )}%
                </strong>
              </div>

              <div className="ca-classification-stat">
                <span>Extraction quality</span>
                <strong>
                  {formatValue(
                    result.extraction_quality_summary?.overall_status,
                    "Not assessed"
                  )}
                </strong>
              </div>
            </div>
          </section>

          <section className="ca-result-panel">
            <SectionHeading
              eyebrow="ANALYSIS SUMMARY"
              title="Risk overview"
              count={`${clauses.length} clauses`}
            />

            <div className="ca-risk-grid">
              {[
                { key: "HIGH", label: "High concern", color: "high" },
                { key: "MEDIUM", label: "Moderate concern", color: "medium" },
                { key: "LOW", label: "Low concern", color: "low" },
              ].map((item) => (
                <div className={`ca-risk-card ${item.color}`} key={item.key}>
                  <span>{item.label}</span>
                  <strong>{riskSummary[item.key] ?? 0}</strong>
                  <small>Configured risk flags</small>
                </div>
              ))}
            </div>

            <div className="ca-risk-disclaimer">
              <Info size={17} />
              <p>
                These counts reflect the currently configured checks.
                A low count does not prove that the contract or its clauses
                are legally safe. Unchecked or unsupported issues may remain.
              </p>
            </div>
          </section>

          <section className="ca-result-panel">
            <SectionHeading
              eyebrow="CLAUSE-BY-CLAUSE REVIEW"
              title="Extracted and analysed clauses"
              count={`${filteredClauses.length} of ${clauses.length}`}
            />

            <div className="ca-clause-toolbar">
              <div className="ca-search-box">
                <Search size={17} />
                <input
                  type="search"
                  placeholder="Search clauses, categories or text..."
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                />
              </div>

              <span className="ca-toolbar-hint">
                Select a clause to inspect its evidence
              </span>
            </div>

            {filteredClauses.length > 0 ? (
              <div className="ca-clause-list">
                {filteredClauses.map((clause, index) => (
                  <ClauseCard
                    key={`${clause.clause_number}-${index}`}
                    clause={clause}
                    index={clauses.indexOf(clause)}
                    expanded={expandedClause === clauses.indexOf(clause)}
                    onToggle={() => {
                      const originalIndex = clauses.indexOf(clause);
                      setExpandedClause(
                        expandedClause === originalIndex ? null : originalIndex
                      );
                    }}
                  />
                ))}
              </div>
            ) : (
              <div className="ca-empty-state">
                <FileSearch size={25} />
                <strong>No matching clauses</strong>
                <p>Try another search term.</p>
              </div>
            )}

            {clauses.length === 0 && (
              <div className="ca-risk-disclaimer">
                <AlertTriangle size={17} />
                <p>
                  No clauses were returned. The document may need better OCR,
                  a clearer scan or further extraction review.
                </p>
              </div>
            )}
          </section>

          <section className="ca-result-panel">
            <SectionHeading
              eyebrow="CONSISTENCY REVIEW"
              title="Cross-clause findings"
              count={findings.length}
            />

            {findings.length > 0 ? (
              <div className="ca-findings-list">
                {findings.map((finding, index) => (
                  <article className="ca-finding-card" key={index}>
                    <div className="ca-finding-icon">
                      <AlertTriangle size={19} />
                    </div>
                    <div>
                      <div className="ca-finding-title">
                        <strong>
                          {formatValue(finding.finding_type, "Potential inconsistency")}
                        </strong>
                        {finding.risk_level && (
                          <StatusBadge value={finding.risk_level} />
                        )}
                      </div>
                      <p>
                        {formatValue(
                          finding.explanation || finding.description,
                          "Further review is required."
                        )}
                      </p>
                      {finding.evidence && (
                        <div className="ca-finding-evidence">
                          <span>Supporting evidence</span>
                          {finding.evidence}
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="ca-empty-state">
                <CheckCircle2 size={25} />
                <strong>No findings returned by current checks</strong>
                <p>
                  The configured cross-clause checks did not return a
                  potential inconsistency. This is not a guarantee that
                  all provisions are consistent.
                </p>
              </div>
            )}
          </section>

          <section className="ca-result-panel">
            <SectionHeading
              eyebrow="REVIEW ACTIONS"
              title="Recommendations"
              count={recommendations.length}
            />

            {recommendations.length > 0 ? (
              <div className="ca-recommendations-list">
                {recommendations.map((item, index) => (
                  <article className="ca-recommendation-card" key={index}>
                    <div className="ca-recommendation-number">
                      {String(index + 1).padStart(2, "0")}
                    </div>
                    <div className="ca-recommendation-content">
                      <strong>
                        {formatValue(
                          item.title || item.finding_type,
                          "Reviewer recommendation"
                        )}
                      </strong>
                      <p>
                        {formatValue(
                          item.recommendation || item.action || item.explanation,
                          "Review this provision with the relevant parties."
                        )}
                      </p>
                      {item.suggested_wording && (
                        <div className="ca-suggested-wording">
                          <span>Suggested draft wording — requires legal review</span>
                          <blockquote>{item.suggested_wording}</blockquote>
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="ca-empty-state">
                <ClipboardList size={25} />
                <strong>No recommendations returned</strong>
                <p>
                  The current analysis did not generate recommendations.
                  This does not mean that no review actions are necessary.
                </p>
              </div>
            )}
          </section>

          <div className="ca-final-notice">
            <ShieldCheck size={21} />
            <div>
              <strong>Important legal notice</strong>
              <p>
                CLAUSEWISE AI provides preliminary document analysis, not
                legal advice or a guarantee of legal compliance. Findings
                depend on extraction quality and configured checks. Consult
                a qualified legal professional before making legal or
                contractual decisions.
              </p>
            </div>
          </div>

          <div className="ca-bottom-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() => window.print()}
            >
              <Download size={16} />
              Print / Save report
            </button>
            <button
              type="button"
              className="primary-button"
              onClick={resetAnalysis}
            >
              <Upload size={16} />
              Analyse another document
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
