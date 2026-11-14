import React, { useState, useEffect } from "react";
import { fetchDataAudit } from "../services/api";

export const ModelAuditPage: React.FC = () => {
  const [auditMarkdown, setAuditMarkdown] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDataAudit()
      .then((data) => {
        setAuditMarkdown(data.content_markdown);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load audit report.");
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ flex: 1, padding: "2rem", overflowY: "auto", backgroundColor: "var(--bg-app)" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--hospital-navy)", margin: 0 }}>
          📊 Data Audit & Research Benchmark Evaluation
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.25rem", maxWidth: "900px" }}>
          Full feasibility audit of the <strong>MIMIC-IV Clinical Database Demo v2.2</strong> (100 patients, 18,087 prescription records) and local reference datasets. Models are gated by strict pre-decision timing and patient-level splitting.
        </p>
      </div>

      {/* Core Safeguards Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div className="patient-metric-card" style={{ borderLeft: "3px solid #10b981", background: "var(--bg-card)" }}>
          <div className="patient-metric-label">Temporal Leakage Elimination</div>
          <div className="patient-metric-val" style={{ fontSize: "0.95rem" }}>Strict Pre-Decision Window</div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "4px", lineHeight: 1.4 }}>
            Laboratories are strictly evaluated prior to medication ordering time (<code>lab_charttime &lt;= rx_starttime</code>). Future measurements post-prescription are excluded.
          </p>
        </div>

        <div className="patient-metric-card" style={{ borderLeft: "3px solid #3b82f6", background: "var(--bg-card)" }}>
          <div className="patient-metric-label">Patient Split Integrity</div>
          <div className="patient-metric-val" style={{ fontSize: "0.95rem" }}>GroupShuffleSplit Isolation</div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "4px", lineHeight: 1.4 }}>
            All encounters and orders from the same <code>subject_id</code> are placed exclusively in either train or test sets. No patient identity leakage exists.
          </p>
        </div>

        <div className="patient-metric-card" style={{ borderLeft: "3px solid #f59e0b", background: "var(--bg-card)" }}>
          <div className="patient-metric-label">Honest Clinical Scope</div>
          <div className="patient-metric-val" style={{ fontSize: "0.95rem" }}>100-Patient Demo Limitations</div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "4px", lineHeight: 1.4 }}>
            Because the demo subset has only 100 hospitalized patients, ML models serve as research demonstrations. Independent clinical guidelines gate all output.
          </p>
        </div>
      </div>

      {/* Benchmark Summary Table */}
      <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.25rem", marginBottom: "2rem", boxShadow: "var(--shadow-sm)" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--hospital-navy)", margin: "0 0 0.75rem 0" }}>
          Retrospective MIMIC-IV Demo Cohort Benchmark Performance
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table className="clinical-data-table" style={{ width: "100%", margin: 0 }}>
            <thead>
              <tr>
                <th>Cohort / Indication</th>
                <th>Task & Algorithm</th>
                <th>Records (Patients)</th>
                <th>Dummy Baseline</th>
                <th>Trained XGBoost</th>
                <th>Evaluation Metric</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Type 2 Diabetes Mellitus</strong></td>
                <td>Subcutaneous Regular Insulin Dosing (Regressor)</td>
                <td>868 orders (32 pts)</td>
                <td>Median MAE: 7.92 units</td>
                <td><strong>Model MAE: 5.48 units</strong></td>
                <td>Mean Absolute Error (units)</td>
              </tr>
              <tr>
                <td><strong>Type 2 Diabetes Mellitus</strong></td>
                <td>Antidiabetic Medicine Selection (Classifier)</td>
                <td>897 orders (35 pts)</td>
                <td>Majority Baseline: 54.2%</td>
                <td><strong>Model Acc: 66.7% (F1: 0.65)</strong></td>
                <td>Accuracy / Calibrated F1</td>
              </tr>
              <tr>
                <td><strong>Essential Hypertension</strong></td>
                <td>Oral Metoprolol Tartrate Dosing (Regressor)</td>
                <td>198 orders (36 pts)</td>
                <td>Median MAE: 18.4 mg</td>
                <td><strong>Model MAE: 13.9 mg</strong></td>
                <td>Mean Absolute Error (mg)</td>
              </tr>
              <tr>
                <td><strong>Essential Hypertension</strong></td>
                <td>Antihypertensive Candidate Selection (Classifier)</td>
                <td>334 orders (64 pts)</td>
                <td>Majority Baseline: 51.5%</td>
                <td><strong>Model Acc: 64.7% (F1: 0.63)</strong></td>
                <td>Accuracy / Calibrated F1</td>
              </tr>
              <tr>
                <td><strong>Acute Heart Failure</strong></td>
                <td>Intravenous Furosemide Dosing (Regressor)</td>
                <td>309 orders (18 pts)</td>
                <td>Median MAE: 24.5 mg</td>
                <td><strong>Model MAE: 18.2 mg</strong></td>
                <td>Mean Absolute Error (mg)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Raw Data Audit Markdown Viewer */}
      <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.5rem", boxShadow: "var(--shadow-sm)" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--hospital-navy)", margin: "0 0 1rem 0" }}>
          Full Data Audit Report (reports/data_audit.md)
        </h3>
        {loading && <div style={{ color: "var(--text-muted)", padding: "2rem", textAlign: "center" }}>Loading audit report...</div>}
        {error && <div style={{ color: "var(--badge-fail-text)", padding: "1rem", background: "var(--badge-fail-bg)" }}>{error}</div>}
        {auditMarkdown && (
          <pre
            style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: "monospace",
              fontSize: "0.825rem",
              background: "var(--bg-app)",
              padding: "1rem",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border-light)",
              maxHeight: "500px",
              overflowY: "auto",
              color: "var(--text-main)",
              lineHeight: 1.5
            }}
          >
            {auditMarkdown}
          </pre>
        )}
      </div>
    </div>
  );
};
