import React from "react";
import type { AssessmentResponse } from "../types";

interface AssessmentResultPageProps {
  result: AssessmentResponse;
  onBackToForm: () => void;
}

export const AssessmentResultPage: React.FC<AssessmentResultPageProps> = ({
  result,
  onBackToForm
}) => {
  const getStatusHero = () => {
    switch (result.status) {
      case "PROPOSAL_AVAILABLE":
        return {
          icon: "✅",
          title: "Dose Proposal Authorized by Safety Engine",
          desc: result.clinical_explanation,
          badgeClass: "PROPOSAL_AVAILABLE"
        };
      case "MORE_INFO_NEEDED":
        return {
          icon: "⚠️",
          title: "Clinical Dosing Withheld — Additional Data Required",
          desc: result.clinical_explanation,
          badgeClass: "MORE_INFO_NEEDED"
        };
      case "CONTRAINDICATED":
        return {
          icon: "⛔",
          title: "Critical Safety Contraindication / Acute Risk Detected",
          desc: result.clinical_explanation,
          badgeClass: "CONTRAINDICATED"
        };
      default:
        return {
          icon: "ℹ️",
          title: "Unsupported Clinical Indication",
          desc: result.clinical_explanation,
          badgeClass: "UNSUPPORTED_CASE"
        };
    }
  };

  const hero = getStatusHero();

  return (
    <div>
      {/* Top Clinical Actions Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <button type="button" className="clinical-btn-secondary" onClick={onBackToForm}>
          ← Modify Patient Chart & Lab Parameters
        </button>
        <div style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>
          Case: <strong style={{ color: "var(--hospital-navy)" }}>{result.diagnosis_name}</strong>
        </div>
      </div>

      {/* Prominent Clinical Status Hero Banner */}
      <div className={`result-hero ${hero.badgeClass}`}>
        <div className="result-hero-icon">{hero.icon}</div>
        <div>
          <div className="result-hero-title">{hero.title}</div>
          <div className="result-hero-desc">{hero.desc}</div>
        </div>
      </div>

      {/* Information Still Needed Alert (if any) */}
      {result.missing_information && result.missing_information.length > 0 && (
        <div className="ehr-card" style={{ borderLeft: "5px solid #f59e0b", backgroundColor: "#fffbeb" }}>
          <div className="ehr-card-title" style={{ color: "#b45309", marginBottom: "0.375rem" }}>
            <span>⚠️</span> Required Clinical Inputs Still Missing
          </div>
          <p style={{ fontSize: "0.8125rem", color: "#92400e" }}>
            The safety engine requires the following laboratory or vital measurements before dose display can be authorized:
          </p>
          <ul style={{ marginLeft: "1.5rem", marginTop: "0.375rem", fontSize: "0.8125rem", color: "#92400e" }}>
            {result.missing_information.map((item, i) => (
              <li key={i}><strong>{item}</strong></li>
            ))}
          </ul>
        </div>
      )}

      {/* Medication Orders & Proposed Dosage Card */}
      <div className="ehr-card">
        <div className="ehr-card-header">
          <div>
            <div className="ehr-card-title">
              <span>💊</span> Candidate Medications & Patient-Specific Dose Proposals
            </div>
            <div className="ehr-card-subtitle">
              Screened against verified guidelines (ADA 2024, ACC/AHA 2020) and retrospective MIMIC-IV inpatient demo prescribing benchmarks.
            </div>
          </div>
        </div>

        {result.proposals && result.proposals.length > 0 ? (
          <div className="rx-orders-grid">
            {result.proposals.map((proposal, idx) => {
              const isAuth = proposal.dose_status === "AUTHORIZED";

              return (
                <div key={idx} className={`rx-order-card ${isAuth ? "AUTHORIZED" : "WITHHELD"}`}>
                  <div className="rx-order-header">
                    <div>
                      <div className="rx-drug-name">{proposal.candidate_medicine}</div>
                      <div className="rx-generic-name">Active Generic: {proposal.generic_name}</div>
                      {proposal.suggested_brand && (
                        <div style={{ marginTop: "4px", fontSize: "0.78rem", color: "var(--teal-primary)", fontWeight: 700 }}>
                          🏷️ Prescribed Indian Brand: <span style={{ background: "white", padding: "1px 6px", borderRadius: "4px", border: "1px solid var(--teal-primary)" }}>{proposal.suggested_brand}</span>
                        </div>
                      )}
                    </div>
                    <div>
                      <span className={`lab-status-badge ${isAuth ? "normal" : "abnormal"}`}>
                        {isAuth ? "AUTHORIZED" : "WITHHELD"}
                      </span>
                    </div>
                  </div>

                  <div className="rx-body">
                    {/* Dose Container */}
                    <div className="rx-dose-container">
                      <div>
                        <div className="rx-section-label">Patient Specific Dose</div>
                        {isAuth && proposal.dose_display ? (
                          <div className="rx-dose-val">
                            {proposal.dose_display} <span style={{ fontSize: "1.1rem", fontWeight: 600 }}>{proposal.unit}</span>
                          </div>
                        ) : (
                          <div className="rx-dose-withheld-label">
                            ⛔ Dose Display Withheld
                          </div>
                        )}
                      </div>

                      {isAuth && (
                        <div style={{ textAlign: "right" }}>
                          <div className="rx-section-label">Route / Frequency</div>
                          <div style={{ fontWeight: 700, fontSize: "0.8125rem" }}>
                            {proposal.route || "PO"} • {proposal.frequency || "Daily"}
                          </div>
                        </div>
                      )}
                    </div>

                    {proposal.instructions && (
                      <div style={{ fontSize: "0.78rem", color: "var(--hospital-navy)", background: "rgba(13, 148, 136, 0.08)", border: "1px solid rgba(13, 148, 136, 0.2)", padding: "4px 8px", borderRadius: "4px" }}>
                        ⏱️ <strong>Instructions:</strong> {proposal.instructions}
                      </div>
                    )}

                    {proposal.brand_names && proposal.brand_names.length > 0 && (
                      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        <strong>Alternative Brands:</strong> {proposal.brand_names.join(", ")}
                      </div>
                    )}

                    {/* Why this candidate */}
                    <div>
                      <div className="rx-section-label">Why This Candidate?</div>
                      <div className="rx-section-text">{proposal.why_candidate}</div>
                    </div>

                    {/* Clinical Rationale */}
                    <div>
                      <div className="rx-section-label">Guideline Dosing Rationale</div>
                      <div className="rx-section-text">{proposal.rationale}</div>
                    </div>

                    {/* SHAP Factor Attributions */}
                    {proposal.shap_contributions && Object.keys(proposal.shap_contributions).length > 0 && (
                      <div className="shap-container">
                        <div className="rx-section-label" style={{ marginBottom: "6px" }}>
                          SHAP Feature Attributions (Patient Factor Influence)
                        </div>
                        {Object.entries(proposal.shap_contributions).map(([feat, val]) => (
                          <div key={feat} className="shap-bar-row">
                            <span className="shap-label">
                              {feat.replace("pre_", "").toUpperCase()}
                            </span>
                            <div className="shap-track">
                              <div
                                className={val >= 0 ? "shap-fill-pos" : "shap-fill-neg"}
                                style={{ width: `${Math.min(Math.abs(val) * 8, 100)}%` }}
                              />
                            </div>
                            <span className="shap-val" style={{ color: val >= 0 ? "var(--teal-dark)" : "#ea580c" }}>
                              {val > 0 ? `+${val}` : val}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Provenance Pill */}
                    <div style={{ marginTop: "auto", paddingTop: "0.5rem" }}>
                      <span className={`provenance-pill ${proposal.provenance}`}>
                        Provenance: {proposal.provenance.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
            No candidate medicines eligible under current clinical parameters.
          </div>
        )}
      </div>

      {/* Multi-Tier Safety Audit Checklist */}
      <div className="ehr-card">
        <div className="ehr-card-header">
          <div className="ehr-card-title">
            <span>🛡️</span> Multi-Tier Safety Engine Audit Log
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--teal-dark)", fontWeight: 700 }}>Independent Clinical Checks</span>
        </div>

        <div className="audit-list">
          {result.safety_checks.map((check, i) => (
            <div key={i} className={`audit-item ${check.status}`}>
              <div style={{ width: "95px" }}>
                <span className={`lab-status-badge ${check.status === "PASS" ? "normal" : check.status === "FAIL" ? "critical" : "abnormal"}`}>
                  {check.status}
                </span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: "0.875rem", color: "var(--hospital-navy)" }}>
                  {check.check_name}
                </div>
                <div style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", marginTop: "2px" }}>
                  {check.findings}
                </div>
                {check.source_reference && (
                  <div style={{ fontSize: "0.7rem", color: "var(--teal-dark)", fontWeight: 600, marginTop: "4px" }}>
                    Verified Clinical Rule: {check.source_reference}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Verified Guideline Citations */}
      <div className="ehr-card">
        <div className="ehr-card-header">
          <div className="ehr-card-title">
            <span>📚</span> Verified Guideline Sources & Published Evidence
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {result.sources.map((src, i) => (
            <div key={i} style={{ padding: "0.875rem", backgroundColor: "var(--bg-subtle)", borderRadius: 6, border: "1px solid var(--border-light)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ fontWeight: 700, color: "var(--hospital-navy)", fontSize: "0.875rem" }}>
                  {src.title}
                </div>
                <span className="lab-status-badge normal">Verified Source</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "3px" }}>
                {src.citation}
              </p>
              <div style={{ marginTop: "6px" }}>
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--teal-primary)", fontSize: "0.75rem", fontWeight: 700, textDecoration: "none" }}
                >
                  🔗 View Full Practice Guideline ({src.organization}, {src.publication_year}) →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Clinical Disclaimer Banner */}
      <div className="clinical-footer">
        <p><strong>Clinical Research Notice:</strong> {result.disclaimer}</p>
        <p style={{ marginTop: "2px" }}>Dataset: {result.model_provenance.dataset} • {result.model_provenance.patient_split}</p>
      </div>
    </div>
  );
};
