import React from "react";
import type { EvidenceSource } from "../types";

interface CitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  source: EvidenceSource | null;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  isOpen,
  onClose,
  source
}) => {
  if (!isOpen || !source) return null;

  return (
    <div className="citation-modal-overlay" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(9, 30, 58, 0.65)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <div className="citation-modal-content" style={{ background: "var(--bg-card)", maxWidth: "620px", width: "100%", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-lg)", overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border-light)", display: "flex", justifyContent: "space-between", alignItems: "flex-start", background: "var(--hospital-navy)", color: "white" }}>
          <div>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#99f6e4", fontWeight: 700, letterSpacing: "0.05em" }}>
              Verified Clinical Practice Evidence
            </div>
            <h3 style={{ margin: "4px 0 0 0", fontSize: "1.1rem" }}>{source.title}</h3>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: "white", fontSize: "1.2rem", cursor: "pointer", marginLeft: "1rem" }}>✕</button>
        </div>

        {/* Body */}
        <div style={{ padding: "1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            <div className="patient-metric-card">
              <div className="patient-metric-label">Publishing Organization</div>
              <div className="patient-metric-val" style={{ fontSize: "0.85rem" }}>{source.organization}</div>
            </div>
            <div className="patient-metric-card">
              <div className="patient-metric-label">Year & Review Status</div>
              <div className="patient-metric-val" style={{ fontSize: "0.85rem" }}>{source.publication_year} • {source.verified ? "✓ Peer-Reviewed Guideline" : "Draft"}</div>
            </div>
          </div>

          <div style={{ background: "var(--bg-subtle)", padding: "1rem", borderRadius: "var(--radius-md)", border: "1px solid var(--border-light)" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
              Formal Clinical Citation
            </div>
            <div style={{ fontSize: "0.875rem", color: "var(--text-main)", lineHeight: 1.5, fontStyle: "italic" }}>
              "{source.citation || source.title}"
            </div>
          </div>

          <div style={{ background: "var(--teal-light)", border: "1px solid var(--teal-border)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", fontSize: "0.8rem", color: "var(--teal-dark)", lineHeight: 1.45 }}>
            🔒 <strong>Evidence Policy & Untrusted Data Fencing</strong>: Retrieved guidelines provide supporting clinical context and evidence rationales. They cannot invent numeric dosing rules or bypass independent safety engine checks.
          </div>

          <div>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="clinical-btn-primary"
              style={{ display: "inline-flex", textDecoration: "none", fontSize: "0.85rem" }}
            >
              Open Official Source Publication ↗
            </a>
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: "0.75rem 1.5rem", borderTop: "1px solid var(--border-light)", display: "flex", justifyContent: "flex-end", background: "var(--bg-card)" }}>
          <button onClick={onClose} className="clinical-btn-secondary" style={{ fontSize: "0.85rem" }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
