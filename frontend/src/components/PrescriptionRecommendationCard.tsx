import React from "react";
import type { AssessmentResponse, ClinicalCase, DoseProposal, EvidenceSource } from "../types";

interface PrescriptionRecommendationCardProps {
  currentCase: ClinicalCase | null;
  assessment: AssessmentResponse | null;
  onApprovePlan: () => void;
  onExportPrescription: () => void;
  onOpenBrandModal: (brandInfo: { generic: string; strength?: string; route?: string }) => void;
  onOpenCitationModal: (source: EvidenceSource) => void;
  onOpenChat: () => void;
}

export const PrescriptionRecommendationCard: React.FC<PrescriptionRecommendationCardProps> = ({
  currentCase,
  assessment,
  onApprovePlan,
  onExportPrescription,
  onOpenBrandModal,
  onOpenCitationModal,
  onOpenChat
}) => {
  if (!assessment) return null;

  const proposals = assessment.proposals || [];
  const primaryProposal: DoseProposal | undefined = proposals[0];
  const isApproved = currentCase?.approved_by_doctor;

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "AUTHORIZED":
        return "badge-authorized";
      case "WITHHELD_CONTRAINDICATION":
        return "badge-contraindicated";
      case "WITHHELD_INSUFFICIENT_DATA":
        return "badge-more-info";
      default:
        return "badge-review";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "AUTHORIZED":
        return "✓ GUIDELINE AUTHORIZED";
      case "WITHHELD_CONTRAINDICATION":
        return "✕ CONTRAINDICATED (WITHHELD)";
      case "WITHHELD_INSUFFICIENT_DATA":
        return "⚠ MORE CLINICAL DATA NEEDED";
      default:
        return "CLINICIAN REVIEW REQUIRED";
    }
  };

  return (
    <div className="prescription-recommendation-card">
      <div className="prescription-card-header">
        <div className="rx-badge-group">
          <span className="step-badge rx-step">STEP 2</span>
          <div>
            <h3 className="rx-title">Clinical Prescription & Dosage Decision</h3>
            <p className="rx-subtitle">
              Guideline-concordant therapy proposal for <strong>{assessment.diagnosis_name}</strong>
            </p>
          </div>
        </div>

        <div className="rx-header-actions">
          {isApproved ? (
            <span className="approved-pill">✓ Clinician Approved</span>
          ) : (
            <button
              onClick={onApprovePlan}
              className="rx-approve-btn"
              title="Officially record clinician review"
            >
              ✓ Review & Approve
            </button>
          )}

          <button
            onClick={onExportPrescription}
            className="rx-export-btn"
            title="Export printable prescription report"
          >
            📄 Print / Export
          </button>
        </div>
      </div>

      {/* Main Proposed Drug Banner */}
      {primaryProposal ? (
        <div className="rx-main-banner">
          <div className="rx-drug-header">
            <div>
              <span className="rx-drug-type">FIRST-LINE THERAPY</span>
              <h2 className="rx-drug-name">{primaryProposal.generic_name}</h2>
              {primaryProposal.suggested_brand && (
                <div className="rx-suggested-brand">
                  Common Branded Reference: <strong>{primaryProposal.suggested_brand}</strong>
                </div>
              )}
            </div>

            <div className={`rx-status-pill ${getStatusBadgeClass(primaryProposal.dose_status)}`}>
              {getStatusLabel(primaryProposal.dose_status)}
            </div>
          </div>

          {/* Dosage Specification */}
          <div className="rx-dosage-box">
            <div className="dosage-metric">
              <span className="dosage-metric-label">PROPOSED STARTING DOSE</span>
              <span className="dosage-metric-value">
                {primaryProposal.dose_display
                  ? `${primaryProposal.dose_display} ${primaryProposal.unit || ""}`
                  : "Dose Withheld"}
              </span>
            </div>

            <div className="dosage-metric">
              <span className="dosage-metric-label">ROUTE & FREQUENCY</span>
              <span className="dosage-metric-text">
                {primaryProposal.route || "Oral (PO)"} • {primaryProposal.frequency || "Daily"}
              </span>
            </div>

            <div className="dosage-metric">
              <span className="dosage-metric-label">ADMINISTRATION</span>
              <span className="dosage-metric-text">
                {primaryProposal.instructions || "Administer as per clinical guidance with meals"}
              </span>
            </div>
          </div>

          {/* Clinical Rationale & Guidelines */}
          <div className="rx-rationale-box">
            <strong>Clinical Practice Rationale:</strong> {primaryProposal.rationale}
          </div>

          {/* Alternative Indian Brands Chips */}
          {primaryProposal.brand_names && primaryProposal.brand_names.length > 0 && (
            <div className="rx-brands-strip">
              <span className="brands-strip-label">Verified Indian Formulations:</span>
              <div className="brands-chips">
                {primaryProposal.brand_names.map((b, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="brand-chip"
                    onClick={() =>
                      onOpenBrandModal({
                        generic: primaryProposal.generic_name,
                        strength: primaryProposal.dose_display || undefined,
                        route: primaryProposal.route || undefined
                      })
                    }
                  >
                    💊 {b}
                  </button>
                ))}
                <button
                  type="button"
                  className="brand-browse-all-btn"
                  onClick={() =>
                    onOpenBrandModal({
                      generic: primaryProposal.generic_name,
                      strength: primaryProposal.dose_display || undefined,
                      route: primaryProposal.route || undefined
                    })
                  }
                >
                  Browse all commercial brands ↗
                </button>
              </div>
            </div>
          )}

          {/* Retrospective SHAP attribution if present */}
          {primaryProposal.shap_contributions && (
            <div className="rx-shap-box">
              <span className="shap-title">MIMIC-IV Retrospective Inpatient Model Attribution (SHAP):</span>
              <div className="shap-tags">
                {Object.entries(primaryProposal.shap_contributions).map(([k, v]) => (
                  <span key={k} className="shap-tag">
                    {k.replace("pre_", "")}: <strong>{v > 0 ? `+${v.toFixed(1)}` : v.toFixed(1)}</strong>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="rx-empty-banner">
          <p>No active drug proposals currently generated. Complete the intake above and click evaluate.</p>
        </div>
      )}

      {/* Additional Alternative Therapies */}
      {proposals.length > 1 && (
        <div className="rx-additional-proposals">
          <h4 className="additional-proposals-title">Alternative / Adjunctive Regimens ({proposals.length - 1})</h4>
          <div className="additional-proposals-grid">
            {proposals.slice(1).map((prop, idx) => (
              <div key={idx} className="alt-proposal-card">
                <div className="alt-header">
                  <strong>{prop.generic_name}</strong>
                  <span className={`status-pill-small ${getStatusBadgeClass(prop.dose_status)}`}>
                    {prop.dose_status === "AUTHORIZED" ? "Authorized" : "Withheld"}
                  </span>
                </div>
                <div className="alt-dose">
                  {prop.dose_display ? `${prop.dose_display} ${prop.unit || ""}` : "Withheld"} • {prop.route || "Oral"} • {prop.frequency || "Daily"}
                </div>
                <div className="alt-rationale">{prop.rationale}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safety Checks Summary Bar */}
      <div className="rx-safety-checks-section">
        <h4 className="safety-section-title">
          Multi-Tier Clinical Safety Gate ({assessment.safety_checks.length} Checks)
        </h4>
        <div className="safety-checks-grid">
          {assessment.safety_checks.map((chk, idx) => (
            <div key={idx} className={`safety-check-item ${chk.status.toLowerCase()}`}>
              <div className="safety-check-left">
                <span className="check-icon">
                  {chk.status === "PASS" ? "✓" : chk.status === "FAIL" ? "✕" : "⚠"}
                </span>
                <div>
                  <strong>{chk.check_name}</strong>
                  <div className="check-findings">{chk.findings}</div>
                </div>
              </div>
              <span className={`check-badge-pill ${chk.status.toLowerCase()}`}>
                {chk.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence Sources & Citations */}
      {assessment.sources && assessment.sources.length > 0 && (
        <div className="rx-sources-strip">
          <span className="sources-label">Verified Guideline Citations:</span>
          <div className="sources-chips">
            {assessment.sources.map((src, idx) => (
              <button
                key={idx}
                type="button"
                className="source-citation-btn"
                onClick={() => onOpenCitationModal(src)}
              >
                📖 {src.title} ({src.organization})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Consultation Banner */}
      <div className="rx-bottom-consult-banner">
        <span>Need deeper clinical explanations or want to ask follow-up questions?</span>
        <button onClick={onOpenChat} className="consult-chat-cta">
          💬 Consult Clinical Assistant in Chat ⬇
        </button>
      </div>
    </div>
  );
};
