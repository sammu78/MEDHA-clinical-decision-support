import React, { useState, useEffect } from "react";
import { exportDraftAssessment } from "../services/api";

interface ExportDraftModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
}

export const ExportDraftModal: React.FC<ExportDraftModalProps> = ({
  isOpen,
  onClose,
  caseId
}) => {
  const [exportData, setExportData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && caseId) {
      setLoading(true);
      exportDraftAssessment(caseId)
        .then((data) => setExportData(data))
        .catch((err) => setError(err.message || "Failed to generate assessment export."))
        .finally(() => setLoading(false));
    }
  }, [isOpen, caseId]);

  if (!isOpen) return null;

  return (
    <div className="citation-modal-overlay" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(9, 30, 58, 0.65)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <div className="citation-modal-content" style={{ background: "var(--bg-card)", maxWidth: "800px", width: "100%", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-lg)", overflow: "hidden", display: "flex", flexDirection: "column", maxHeight: "90vh" }}>
        {/* Header */}
        <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border-light)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--hospital-navy)", color: "white" }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.1rem" }}>📄 Draft Clinical Assessment Summary</h3>
            <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Case: {caseId} • Research Decision Support Record</div>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: "white", fontSize: "1.2rem", cursor: "pointer" }}>✕</button>
        </div>

        {/* Content */}
        <div style={{ padding: "1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem" }}>
          {loading && <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Compiling draft export...</div>}
          {error && <div style={{ padding: "1rem", background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)" }}>{error}</div>}

          {exportData && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem", fontSize: "0.85rem", lineHeight: 1.5 }}>
              {/* Metadata */}
              <div style={{ background: "var(--bg-subtle)", padding: "0.85rem 1rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
                <div><strong>Diagnosis:</strong> {exportData.diagnosis}</div>
                <div><strong>Patient Data Version:</strong> v{exportData.patient_version}</div>
                <div><strong>Assessment Status:</strong> <span className={`status-badge ${exportData.status.toLowerCase().replace('_', '-')}`}>{exportData.status}</span></div>
                <div><strong>Doctor Approval Status:</strong> {exportData.approved_by_doctor ? "✓ Approved by Attending Physician" : "Pending Physician Review"}</div>
                <div><strong>Export Timestamp:</strong> {exportData.export_timestamp}</div>
              </div>

              {/* Proposals */}
              <div>
                <h4 style={{ color: "var(--hospital-navy)", marginBottom: "0.5rem" }}>Candidate Medicine Proposals</h4>
                {exportData.dose_proposals?.map((prop: any, idx: number) => (
                  <div key={idx} style={{ border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", padding: "0.75rem", marginBottom: "0.5rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <div>
                        <strong>{prop.candidate_medicine}</strong>
                        {prop.suggested_brand && (
                          <span style={{ marginLeft: "8px", fontSize: "0.78rem", background: "rgba(13, 148, 136, 0.1)", color: "var(--teal-primary)", padding: "1px 6px", borderRadius: "4px", fontWeight: 700 }}>
                            Brand: {prop.suggested_brand}
                          </span>
                        )}
                      </div>
                      <span className={`status-badge ${prop.dose_status.toLowerCase().replace('_', '-')}`}>{prop.dose_status}</span>
                    </div>
                    {prop.dose_display ? (
                      <div style={{ margin: "4px 0", color: "var(--teal-dark)", fontWeight: 700 }}>
                        Proposed Dose: {prop.dose_display} {prop.unit} ({prop.route}) — {prop.frequency}
                      </div>
                    ) : (
                      <div style={{ margin: "4px 0", color: "var(--badge-fail-text)", fontStyle: "italic" }}>
                        Dose Withheld: {prop.rationale}
                      </div>
                    )}
                    {prop.instructions && (
                      <div style={{ fontSize: "0.8rem", color: "var(--hospital-navy)", margin: "2px 0" }}>
                        Instructions: {prop.instructions}
                      </div>
                    )}
                    <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                      Rationale: {prop.rationale} | Provenance: {prop.provenance}
                    </div>
                  </div>
                ))}
              </div>

              {/* Safety Evaluation & Unchecked Items */}
              <div>
                <h4 style={{ color: "var(--hospital-navy)", marginBottom: "0.5rem" }}>Safety Evaluation Audit</h4>
                {exportData.safety_checks?.map((chk: any, idx: number) => (
                  <div key={idx} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                    <span>{chk.check_name}: {chk.findings}</span>
                    <span className={`safety-badge ${chk.status.toLowerCase()}`}>{chk.status}</span>
                  </div>
                ))}
              </div>

              {exportData.unchecked_safety_items?.length > 0 && (
                <div style={{ background: "var(--badge-warn-bg)", border: "1px solid var(--badge-warn-border)", padding: "0.75rem", borderRadius: "var(--radius-sm)" }}>
                  <strong style={{ color: "var(--badge-warn-text)" }}>⚠️ Incomplete Coverage Items:</strong>
                  <ul style={{ paddingLeft: "1.2rem", marginTop: "4px", color: "var(--badge-warn-text)" }}>
                    {exportData.unchecked_safety_items.map((item: any, idx: number) => (
                      <li key={idx}>{item.check_name}: {item.findings}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Citations */}
              <div>
                <h4 style={{ color: "var(--hospital-navy)", marginBottom: "0.5rem" }}>Supporting Evidence Citations</h4>
                <ul style={{ paddingLeft: "1.2rem" }}>
                  {exportData.evidence_citations?.map((src: any, idx: number) => (
                    <li key={idx} style={{ marginBottom: "4px" }}>
                      <strong>{src.title}</strong> ({src.organization}, {src.publication_year}) — <a href={src.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--teal-primary)" }}>{src.url}</a>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Disclaimer */}
              <div style={{ background: "var(--bg-subtle)", padding: "0.75rem", borderRadius: "var(--radius-sm)", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                <strong>RESEARCH DISCLAIMER:</strong> {exportData.disclaimer}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: "0.75rem 1.5rem", borderTop: "1px solid var(--border-light)", display: "flex", justifyContent: "space-between", background: "var(--bg-card)" }}>
          <button onClick={() => window.print()} className="clinical-btn-secondary" style={{ fontSize: "0.85rem" }}>
            🖨️ Print / Save PDF
          </button>
          <button onClick={onClose} className="clinical-btn-primary" style={{ fontSize: "0.85rem" }}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
