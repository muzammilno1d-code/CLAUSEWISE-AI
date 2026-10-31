
import { useState } from "react";
import {
  FileText,
  Upload,
  Search,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  HelpCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import { investigateProperty } from "../services/api";

const FIELD_LABELS = {
  buyer: "Buyer",
  seller: "Seller",
  survey_number: "Survey Number",
  property_extent: "Property Extent",
  registration_date: "Registration Date",
  document_number: "Document Number",
  registration_office: "Registration Office",
  north_boundary: "North Boundary",
  south_boundary: "South Boundary",
  east_boundary: "East Boundary",
  west_boundary: "West Boundary",
  property_address: "Property Address",
  apartment_name: "Apartment Name",
  flat_number: "Flat Number",
  built_up_area: "Built-up Area",
  consideration_amount: "Consideration Amount",
  applicant: "Applicant",
  application_number: "Application Number",
  search_period: "Search Period",
  registration_year: "Registration Year",
  transaction_details: "Transaction Details",
  agreement_date: "Agreement Date",
  property_type: "Property Type",
  village: "Village",
  street: "Street",
  declared_owner: "Declared Owner",
};

function FieldCard({ field, data }) {
  const [showEvidence, setShowEvidence] = useState(false);
  const found = data?.status === "FOUND";

  return (
    <div className="property-field-card">
      <div className="property-field-top">
        <span>{FIELD_LABELS[field] || field.replaceAll("_", " ")}</span>
        <span className={`field-status ${found ? "found" : "not-found"}`}>
          {found ? "FOUND" : "NOT FOUND"}
        </span>
      </div>

      <strong className={found ? "" : "missing-value"}>
        {data?.value ?? "Not identified in document"}
      </strong>

      {found && (
        <>
          <span className="property-field-page">
            Page {data.page_number ?? "N/A"}
          </span>

          {data.evidence && (
            <button
              className="evidence-toggle"
              onClick={() => setShowEvidence(!showEvidence)}
            >
              {showEvidence ? "Hide evidence" : "View source evidence"}
              {showEvidence ? (
                <ChevronUp size={15} />
              ) : (
                <ChevronDown size={15} />
              )}
            </button>
          )}

          {showEvidence && (
            <blockquote className="property-evidence">
              {data.evidence}
            </blockquote>
          )}
        </>
      )}
    </div>
  );
}

function DocumentCard({
  title,
  document,
  extraction,
  extractionSummary,
}) {
  const fields = extraction?.extracted_fields || {};
  const summary = extraction?.extraction_summary || {};
  const pageSummary = extractionSummary || {};

  const priorityFields = [
    "buyer",
    "seller",
    "survey_number",
    "property_extent",
    "property_address",
    "north_boundary",
    "south_boundary",
    "east_boundary",
    "west_boundary",
    "built_up_area",
    "agreement_date",
    "registration_date",
    "applicant",
    "search_period",
    "village",
    "street",
    "declared_owner",
  ];

  return (
    <section className="property-result-section">
      <div className="property-document-heading">
        <div>
          <span className="page-eyebrow">{title}</span>
          <h3>{document?.filename || "Uploaded document"}</h3>
          <p>{document?.document_type || "Type not identified"}</p>
        </div>
        <FileText size={25} />
      </div>

      <div className="property-document-stats">
        <div>
          <span>Pages</span>
          <strong>{pageSummary.total_pages ?? 0}</strong>
        </div>
        <div>
          <span>Text pages</span>
          <strong>{pageSummary.pdf_text_pages ?? 0}</strong>
        </div>
        <div>
          <span>OCR pages</span>
          <strong>{pageSummary.ocr_pages ?? 0}</strong>
        </div>
        <div>
          <span>Fields found</span>
          <strong>
            {summary.fields_found ?? 0}/{summary.total_fields ?? 26}
          </strong>
        </div>
      </div>

      <div className="property-fields-grid">
        {priorityFields
          .filter((field) => fields[field])
          .map((field) => (
            <FieldCard
              key={field}
              field={field}
              data={fields[field]}
            />
          ))}
      </div>

      {extraction?.limitations?.length > 0 && (
        <details className="property-limitations">
          <summary>
            Extraction limitations ({extraction.limitations.length})
          </summary>
          <ul>
            {extraction.limitations.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}

function ComparisonStatus({ status }) {
  if (status === "MATCH") {
    return (
      <span className="comparison-status match">
        <CheckCircle2 size={15} /> MATCH
      </span>
    );
  }

  if (status === "POTENTIAL_MISMATCH") {
    return (
      <span className="comparison-status mismatch">
        <AlertTriangle size={15} /> POTENTIAL MISMATCH
      </span>
    );
  }

  return (
    <span className="comparison-status not-comparable">
      <HelpCircle size={15} /> NOT COMPARABLE
    </span>
  );
}

export default function PropertyInvestigation() {
  const [saleDocument, setSaleDocument] = useState(null);
  const [ecDocument, setEcDocument] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function selectPdf(event, setter) {
    const selected = event.target.files?.[0];

    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF document.");
      event.target.value = "";
      return;
    }

    setter(selected);
    setResult(null);
    setError("");
  }

  async function handleInvestigation() {
    if (!saleDocument || !ecDocument) {
      setError("Please upload both property documents.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await investigateProperty(saleDocument, ecDocument);
      setResult(data);
    } catch (err) {
      setError(err.message || "Property investigation failed.");
    } finally {
      setLoading(false);
    }
  }

  const investigation = result?.investigation;
  const documents = investigation?.documents;
  const comparison = investigation?.comparison;
  const summary = investigation?.investigation_summary;

  return (
    <div className="page-container-inner">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">PROPERTY INTELLIGENCE</span>
          <h1>Property Investigation</h1>
          <p>
            Compare property information across documents and identify
            discrepancies that may require further verification.
          </p>
        </div>
      </div>

      {!result && (
        <>
          <div className="property-upload-grid">
            <div className="property-upload-card">
              <div className="property-upload-icon">
                <FileText size={24} />
              </div>

              <h3>Property Sale Document</h3>
              <p>Upload a Property Sale Deed or Sale Agreement.</p>

              <label className="property-dropzone">
                <Upload size={23} />
                <strong>Select sale document</strong>
                <span>PDF files only</span>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  hidden
                  onChange={(event) =>
                    selectPdf(event, setSaleDocument)
                  }
                />
              </label>

              {saleDocument && (
                <div className="property-selected-file">
                  <FileText size={17} />
                  <span>{saleDocument.name}</span>
                  <button onClick={() => setSaleDocument(null)}>
                    Remove
                  </button>
                </div>
              )}
            </div>

            <div className="property-upload-card">
              <div className="property-upload-icon">
                <ShieldCheck size={24} />
              </div>

              <h3>Encumbrance Document</h3>
              <p>Upload an issued EC or an EC application/copy.</p>

              <label className="property-dropzone">
                <Upload size={23} />
                <strong>Select EC document</strong>
                <span>PDF files only</span>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  hidden
                  onChange={(event) =>
                    selectPdf(event, setEcDocument)
                  }
                />
              </label>

              {ecDocument && (
                <div className="property-selected-file">
                  <FileText size={17} />
                  <span>{ecDocument.name}</span>
                  <button onClick={() => setEcDocument(null)}>
                    Remove
                  </button>
                </div>
              )}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="primary-button property-investigate-button"
            onClick={handleInvestigation}
            disabled={!saleDocument || !ecDocument || loading}
          >
            {loading ? (
              <>
                <RefreshCw size={17} className="spin" />
                Investigating documents...
              </>
            ) : (
              <>
                <Search size={17} />
                Investigate property
              </>
            )}
          </button>

          <div className="property-note">
            <AlertTriangle size={17} />
            <p>
              This process identifies preliminary document discrepancies.
              It does not establish ownership, title, fraud, or the absence
              of encumbrances. An EC application is not an issued EC.
            </p>
          </div>
        </>
      )}

      {result && investigation && (
        <div className="property-investigation-results">
          <div className="property-result-heading">
            <div>
              <span className="page-eyebrow">INVESTIGATION COMPLETED</span>
              <h2>Property investigation report</h2>
              <p>
                {result.status || "Property investigation completed"}
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={() => {
                setResult(null);
                setSaleDocument(null);
                setEcDocument(null);
                setError("");
              }}
            >
              <Upload size={16} />
              New investigation
            </button>
          </div>

          <div className="property-overview-grid">
            <div className="property-overview-card">
              <FileText size={21} />
              <span>Documents processed</span>
              <strong>{summary?.documents_processed ?? 0}</strong>
            </div>

            <div className="property-overview-card">
              <CheckCircle2 size={21} />
              <span>Matching fields</span>
              <strong>{summary?.matching_fields ?? 0}</strong>
            </div>

            <div className="property-overview-card">
              <AlertTriangle size={21} />
              <span>Potential mismatches</span>
              <strong>{summary?.potential_mismatches ?? 0}</strong>
            </div>

            <div className="property-overview-card">
              <HelpCircle size={21} />
              <span>Need more information</span>
              <strong>
                {summary?.fields_requiring_more_information ?? 0}
              </strong>
            </div>
          </div>

          {summary?.review_required && (
            <div className="property-review-warning">
              <AlertTriangle size={22} />
              <div>
                <strong>Further verification required</strong>
                <p>
                  The available documents do not provide enough information
                  for a complete comparison. Review the extracted fields and
                  verify them against the original records.
                </p>
              </div>
            </div>
          )}

          {summary?.ec_application_detected && (
            <div className="property-application-warning">
              <ShieldCheck size={20} />
              <div>
                <strong>EC application / copy detected</strong>
                <p>
                  The second document is not classified as an issued
                  Encumbrance Certificate. Its contents are not independent
                  confirmation of registered transactions.
                </p>
              </div>
            </div>
          )}

          <section className="property-result-section">
            <h3>Comparison overview</h3>

            <div className="comparison-overview">
              <div>
                <span>Comparison status</span>
                <strong>
                  {comparison?.comparison_status || "Not available"}
                </strong>
              </div>
              <div>
                <span>Verification level</span>
                <strong>
                  {comparison?.verification_level?.replaceAll("_", " ") ||
                    "N/A"}
                </strong>
              </div>
            </div>

            <div className="comparison-counts">
              <div>
                <strong>
                  {comparison?.summary?.total_fields ?? 0}
                </strong>
                <span>Total fields</span>
              </div>
              <div>
                <strong>
                  {comparison?.summary?.comparable_fields ?? 0}
                </strong>
                <span>Comparable</span>
              </div>
              <div>
                <strong>
                  {comparison?.summary?.matching_fields ?? 0}
                </strong>
                <span>Matching</span>
              </div>
              <div>
                <strong>
                  {comparison?.summary?.potential_mismatches ?? 0}
                </strong>
                <span>Potential mismatches</span>
              </div>
            </div>

            <div className="property-comparison-list">
              {(comparison?.comparisons || []).map((item, index) => (
                <div
                  className="property-comparison-row"
                  key={`${item.field}-${index}`}
                >
                  <div className="comparison-field-name">
                    <strong>{item.field_label || item.field}</strong>
                    <ComparisonStatus status={item.status} />
                  </div>

                  <div className="comparison-values">
                    <div>
                      <span>Sale document</span>
                      <strong>
                        {item.first_document_value ?? "Not found"}
                      </strong>
                    </div>
                    <div>
                      <span>EC document</span>
                      <strong>
                        {item.second_document_value ?? "Not found"}
                      </strong>
                    </div>
                  </div>

                  <p>{item.explanation}</p>
                </div>
              ))}
            </div>
          </section>

          <DocumentCard
            title="DOCUMENT 1 · SALE AGREEMENT / DEED"
            document={result.first_property_document}
            extraction={documents?.first_document?.extraction}
            extractionSummary={
              result.extraction_summaries?.first_property_document
            }
          />

          <DocumentCard
            title="DOCUMENT 2 · ENCUMBRANCE DOCUMENT"
            document={result.second_property_document}
            extraction={documents?.second_document?.extraction}
            extractionSummary={
              result.extraction_summaries?.second_property_document
            }
          />

          <section className="property-result-section">
            <h3>Investigation limitations</h3>
            <ul className="investigation-limitations">
              {(comparison?.limitations || []).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </section>

          <div className="legal-disclaimer">
            <ShieldCheck size={19} />
            <p>{investigation.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
}
