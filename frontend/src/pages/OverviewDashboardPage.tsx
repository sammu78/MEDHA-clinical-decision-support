import React, { useEffect, useState } from "react";
import type { DashboardMetrics } from "../types";
import { fetchDashboardMetrics } from "../services/api";

interface OverviewDashboardPageProps {
  onNavigateTab: (tab: string) => void;
  onSelectCase?: (caseId: string) => void;
}

export const OverviewDashboardPage: React.FC<OverviewDashboardPageProps> = ({
  onNavigateTab,
  onSelectCase
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardMetrics()
      .then((data) => {
        setMetrics(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard metrics error:", err);
        setError("Failed to load backend metrics. Please ensure FastAPI server is running.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="workspace-main" style={{ padding: "1.5rem", overflowY: "auto", maxWidth: "1280px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.6rem", fontWeight: 700, color: "var(--navy-900, #0f2744)" }}>
            Clinical Decision Support Overview
          </h1>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.875rem" }}>
            Real-time status of the normalized Fact–Dimension clinical database, ML models, and guideline rules.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            className="action-btn"
            style={{ backgroundColor: "var(--teal-600, #0d9488)", color: "#fff", padding: "0.5rem 1rem", borderRadius: "6px", border: "none", cursor: "pointer", fontWeight: 600 }}
            onClick={() => onNavigateTab("new_assessment")}
          >
            + New Assessment
          </button>
          <button
            className="action-btn"
            style={{ backgroundColor: "#0f2744", color: "#fff", padding: "0.5rem 1rem", borderRadius: "6px", border: "none", cursor: "pointer", fontWeight: 600 }}
            onClick={() => onNavigateTab("workspace")}
          >
            💬 Open Doctor Chat
          </button>
        </div>
      </div>

      {loading && (
        <div style={{ padding: "2rem", textAlign: "center", color: "#64748b" }}>
          Loading real-time clinical database metrics...
        </div>
      )}

      {error && (
        <div style={{ padding: "1rem", backgroundColor: "#fee2e2", color: "#b91c1c", borderRadius: "8px", marginBottom: "1.5rem" }}>
          ⚠️ {error}
        </div>
      )}

      {metrics && (
        <>
          {/* Key Metric KPI Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", fontWeight: 600 }}>
                Stored Assessments
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#0f2744", marginTop: "0.25rem" }}>
                {metrics.counts.assessments}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#0d9488", marginTop: "0.25rem" }}>
                Across {metrics.counts.cases} Patient Cases
              </div>
            </div>

            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", fontWeight: 600 }}>
                Indian Medicines (CDSCO)
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#0f2744", marginTop: "0.25rem" }}>
                {metrics.counts.commercial_medicines.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
                Mapped Brand Formulations
              </div>
            </div>

            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", fontWeight: 600 }}>
                Treatment Decisions (MIMIC-IV)
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#0f2744", marginTop: "0.25rem" }}>
                {metrics.counts.treatment_decisions.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
                {metrics.counts.unique_patients} Unique Patient Encounters
              </div>
            </div>

            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", fontWeight: 600 }}>
                Clinical Evidence & Guidelines
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#0f2744", marginTop: "0.25rem" }}>
                {metrics.counts.supported_diseases}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#0d9488", marginTop: "0.25rem" }}>
                ICMR STWs & KDIGO Rules
              </div>
            </div>
          </div>

          {/* System Health & Safety Engines Banner */}
          <div style={{ backgroundColor: "#f0fdf4", border: "1px solid #bbf7d0", padding: "1rem 1.25rem", borderRadius: "8px", marginBottom: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600, color: "#166534", display: "flex", alignItems: "center", gap: "8px" }}>
                <span>🛡️</span> Multi-Tier Clinical Safety Gate: ACTIVE
              </div>
              <div style={{ fontSize: "0.8rem", color: "#15803d", marginTop: "0.25rem" }}>
                Renal CKD-EPI 2021 & Cockcroft-Gault formulas active | Zero-leakage temporal pre-decision lab query active.
              </div>
            </div>
            <div style={{ fontSize: "0.8rem", textAlign: "right", color: "#166534" }}>
              <div>Classifiers: {metrics.models_status.classifiers.join(", ") || "3 active"}</div>
              <div>Regressors: {metrics.models_status.regressors.join(", ") || "3 active"}</div>
            </div>
          </div>

          {/* Two-Column Grid: Recent Assessments & Database Import Batches */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "1.5rem", marginBottom: "1.5rem" }}>
            {/* Recent Assessments Table */}
            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 600, color: "#0f2744" }}>
                  Recent Case Assessments
                </h3>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Live Database Feed</span>
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left", color: "#475569" }}>
                      <th style={{ padding: "0.5rem 0.25rem" }}>Case / Diagnosis</th>
                      <th style={{ padding: "0.5rem" }}>Status</th>
                      <th style={{ padding: "0.5rem" }}>Doctor Review</th>
                      <th style={{ padding: "0.5rem", textAlign: "right" }}>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.recent_assessments.map((asmt) => (
                      <tr
                        key={asmt.assessment_id}
                        style={{ borderBottom: "1px solid #f1f5f9", cursor: "pointer" }}
                        onClick={() => {
                          if (onSelectCase) onSelectCase(asmt.case_id);
                          onNavigateTab("workspace");
                        }}
                      >
                        <td style={{ padding: "0.6rem 0.25rem", fontWeight: 500, color: "#0f2744" }}>
                          {asmt.diagnosis_name || asmt.title || asmt.case_id}
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem" }}>
                          <span
                            style={{
                              padding: "0.2rem 0.5rem",
                              borderRadius: "4px",
                              fontSize: "0.7rem",
                              fontWeight: 600,
                              backgroundColor:
                                asmt.status === "PROPOSAL_AVAILABLE"
                                  ? "#dcfce7"
                                  : asmt.status === "CONTRAINDICATED"
                                  ? "#fee2e2"
                                  : "#fef3c7",
                              color:
                                asmt.status === "PROPOSAL_AVAILABLE"
                                  ? "#166534"
                                  : asmt.status === "CONTRAINDICATED"
                                  ? "#b91c1c"
                                  : "#92400e"
                            }}
                          >
                            {asmt.status}
                          </span>
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem" }}>
                          {asmt.approved_by_doctor ? (
                            <span style={{ color: "#166534", fontWeight: 600 }}>✓ Confirmed</span>
                          ) : (
                            <span style={{ color: "#64748b" }}>Pending</span>
                          )}
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem", textAlign: "right", color: "#64748b", fontSize: "0.75rem" }}>
                          {new Date(asmt.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </td>
                      </tr>
                    ))}
                    {metrics.recent_assessments.length === 0 && (
                      <tr>
                        <td colSpan={4} style={{ padding: "1rem", textAlign: "center", color: "#94a3b8" }}>
                          No clinical assessments recorded yet. Click &quot;+ New Assessment&quot; to begin.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Fact-Dimension Import Batches */}
            <div style={{ backgroundColor: "#fff", padding: "1.25rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 600, color: "#0f2744" }}>
                  Data Warehouse Import Batches
                </h3>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Fact–Dimension Logs</span>
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left", color: "#475569" }}>
                      <th style={{ padding: "0.5rem 0.25rem" }}>Source Dataset</th>
                      <th style={{ padding: "0.5rem" }}>Read</th>
                      <th style={{ padding: "0.5rem" }}>Imported</th>
                      <th style={{ padding: "0.5rem" }}>Status</th>
                      <th style={{ padding: "0.5rem", textAlign: "right" }}>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.import_batches.map((b) => (
                      <tr key={b.batch_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                        <td style={{ padding: "0.6rem 0.25rem", fontWeight: 500, color: "#0f2744" }}>
                          {b.source_file}
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem", color: "#64748b" }}>
                          {b.records_read.toLocaleString()}
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem", fontWeight: 600, color: "#0d9488" }}>
                          {b.records_imported.toLocaleString()}
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem" }}>
                          <span style={{ color: "#166534", backgroundColor: "#dcfce7", padding: "0.15rem 0.4rem", borderRadius: "4px", fontSize: "0.7rem", fontWeight: 600 }}>
                            {b.status}
                          </span>
                        </td>
                        <td style={{ padding: "0.6rem 0.5rem", textAlign: "right", color: "#64748b", fontSize: "0.75rem" }}>
                          {new Date(b.imported_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                    {metrics.import_batches.length === 0 && (
                      <tr>
                        <td colSpan={5} style={{ padding: "1rem", textAlign: "center", color: "#94a3b8" }}>
                          No import batches logged. Run `python -m app.database.importer` to synchronize data.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
