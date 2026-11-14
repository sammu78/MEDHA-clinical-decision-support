import React from "react";
import type { ClinicalCase } from "../types";

interface PatientPanelProps {
  currentCase: ClinicalCase | null;
  onEditPatient: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const PatientPanel: React.FC<PatientPanelProps> = ({
  currentCase,
  onEditPatient,
  isOpen,
  onClose
}) => {
  if (!currentCase) {
    return (
      <aside className={`patient-facts-panel ${isOpen ? "open" : ""}`}>
        <div className="patient-panel-header">
          <div className="patient-panel-title">👤 Patient Context</div>
        </div>
        <div style={{ padding: "1.5rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
          No active patient case selected.
        </div>
      </aside>
    );
  }

  const p = currentCase.patient_data || {};
  const labs = p.labs || {};

  // Renal calculations
  const creatinine = labs.creatinine?.value;
  const age = p.age || 0;
  const gender = p.gender || "M";
  const weight = p.weight_kg || 0;

  let calculatedEgfr: number | null = null;
  if (creatinine && creatinine > 0 && age > 0) {
    const isFemale = gender === "F";
    const kappa = isFemale ? 0.7 : 0.9;
    const alpha = isFemale ? -0.241 : -0.302;
    const genderMult = isFemale ? 1.012 : 1.0;
    const scrRatio = creatinine / kappa;
    const val = 142 * Math.pow(Math.min(scrRatio, 1.0), alpha) * Math.pow(Math.max(scrRatio, 1.0), -1.2) * Math.pow(0.9938, age) * genderMult;
    calculatedEgfr = Math.round(val * 10) / 10;
  }

  let calculatedCrcl: number | null = null;
  if (creatinine && creatinine > 0 && age > 0 && weight > 0) {
    const factor = gender === "F" ? 0.85 : 1.0;
    const crcl = ((140.0 - age) * weight * factor) / (72.0 * creatinine);
    calculatedCrcl = Math.round(crcl * 10) / 10;
  }

  return (
    <aside className={`patient-facts-panel ${isOpen ? "open" : ""}`}>
      <div className="patient-panel-header">
        <div className="patient-panel-title">
          <span>👤 Patient Facts</span>
          <span className="case-badge">v{currentCase.patient_version}</span>
        </div>
        <div style={{ display: "flex", gap: "6px" }}>
          <button
            onClick={onEditPatient}
            className="clinical-btn-secondary"
            style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
            title="Edit patient parameters"
          >
            ✏️ Edit
          </button>
          <button
            onClick={onClose}
            className="sidebar-collapse-btn"
            style={{ color: "var(--text-muted)" }}
            title="Close patient panel"
          >
            ✕
          </button>
        </div>
      </div>

      <div className="patient-facts-content">
        {/* Confirmed Diagnosis */}
        <div className="patient-metric-card" style={{ borderLeft: "3px solid var(--teal-primary)" }}>
          <div className="patient-metric-label">Confirmed Clinical Case</div>
          <div className="patient-metric-val">{currentCase.diagnosis_name || p.diagnosis_name || "General Evaluation"}</div>
          <div className="patient-metric-sub">Case ID: {currentCase.case_id}</div>
        </div>

        {/* Demographics */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
          <div className="patient-metric-card">
            <div className="patient-metric-label">Age & Sex</div>
            <div className="patient-metric-val">{p.age || "—"} yrs ({p.gender || "Unknown"})</div>
          </div>
          <div className="patient-metric-card">
            <div className="patient-metric-label">Body Weight</div>
            <div className="patient-metric-val">{p.weight_kg ? `${p.weight_kg} kg` : "Unknown"}</div>
          </div>
        </div>

        {/* Renal Function Section */}
        <div className="patient-metric-card">
          <div className="patient-metric-label">Renal Function Profile</div>
          <div style={{ marginTop: "4px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span>Serum Creatinine:</span>
              <strong>{creatinine ? `${creatinine} mg/dL` : "Unknown"}</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span>eGFR (CKD-EPI 2021):</span>
              <strong style={{ color: calculatedEgfr && calculatedEgfr < 30 ? "var(--badge-fail-text)" : calculatedEgfr && calculatedEgfr < 60 ? "var(--badge-warn-text)" : "var(--badge-pass-text)" }}>
                {calculatedEgfr ? `${calculatedEgfr} mL/min/1.73m²` : (labs.egfr ? `${labs.egfr.value} mL/min` : "Not calculated")}
              </strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
              <span>CrCl (Cockcroft-Gault):</span>
              <strong>{calculatedCrcl ? `${calculatedCrcl} mL/min` : "Weight/Cr needed"}</strong>
            </div>
          </div>
          <div className="patient-metric-sub" style={{ marginTop: "6px", fontSize: "0.68rem" }}>
            *Renal clearance assumes stable baseline creatinine without acute renal replacement therapy.
          </div>
        </div>

        {/* Hepatic Markers */}
        <div className="patient-metric-card">
          <div className="patient-metric-label">Hepatic Integrity</div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.825rem", marginTop: "4px" }}>
            <span>ALT: <strong>{labs.alt ? `${labs.alt.value} U/L` : "Unknown"}</strong></span>
            <span>AST: <strong>{labs.ast ? `${labs.ast.value} U/L` : "Unknown"}</strong></span>
            <span>Bilirubin: <strong>{labs.bilirubin ? `${labs.bilirubin.value} mg/dL` : "Unknown"}</strong></span>
          </div>
        </div>

        {/* Metabolic & Vitals */}
        <div className="patient-metric-card">
          <div className="patient-metric-label">Vitals & Clinical Labs</div>
          <div style={{ marginTop: "4px", display: "flex", flexDirection: "column", gap: "4px", fontSize: "0.85rem" }}>
            {labs.spo2 && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Oxygen Saturation (SpO2):</span>
                <strong style={{ color: labs.spo2.value < 93 ? "var(--badge-fail-text)" : labs.spo2.value < 95 ? "var(--badge-warn-text)" : "var(--badge-pass-text)" }}>
                  {labs.spo2.value}%
                </strong>
              </div>
            )}
            {labs.peak_flow && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Peak Flow (PEF):</span>
                <strong>{labs.peak_flow.value} L/min</strong>
              </div>
            )}
            {labs.systolic_bp && labs.diastolic_bp && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Blood Pressure:</span>
                <strong>{labs.systolic_bp.value}/{labs.diastolic_bp.value} mmHg</strong>
              </div>
            )}
            {labs.glucose && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Blood Glucose:</span>
                <strong>{labs.glucose.value} {labs.glucose.unit}</strong>
              </div>
            )}
            {labs.potassium && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Serum Potassium:</span>
                <strong>{labs.potassium.value} {labs.potassium.unit}</strong>
              </div>
            )}
            {labs.platelet && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Platelets:</span>
                <strong>{labs.platelet.value} {labs.platelet.unit}</strong>
              </div>
            )}
            {labs.hemoglobin && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Hemoglobin:</span>
                <strong>{labs.hemoglobin.value} {labs.hemoglobin.unit}</strong>
              </div>
            )}
          </div>
        </div>

        {/* Active Medications */}
        <div className="patient-metric-card">
          <div className="patient-metric-label">Current Active Medications ({p.current_medications?.length || 0})</div>
          {p.current_medications && p.current_medications.length > 0 ? (
            <ul style={{ paddingLeft: "1.1rem", marginTop: "4px", fontSize: "0.8rem", color: "var(--text-main)" }}>
              {p.current_medications.map((m: string, idx: number) => (
                <li key={idx}>{m}</li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "4px" }}>
              None reported (or not entered).
            </div>
          )}
        </div>

        {/* Allergies Profile */}
        <div className="patient-metric-card">
          <div className="patient-metric-label">Documented Hypersensitivities</div>
          {p.allergies && p.allergies.length > 0 ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "4px" }}>
              {p.allergies.map((a: string, idx: number) => (
                <span key={idx} className="status-badge contraindicated" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
                  ⚠️ {a}
                </span>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: "0.78rem", color: "var(--badge-pass-text)", marginTop: "4px" }}>
              ✓ No known drug allergies confirmed (NKDA).
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
