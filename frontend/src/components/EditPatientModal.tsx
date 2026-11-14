import React, { useState, useEffect } from "react";
import type { ClinicalCase } from "../types";

interface EditPatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentCase: ClinicalCase;
  onSave: (updatedPatient: Record<string, any>) => Promise<void>;
}

export const DISEASE_OPTIONS = [
  { id: "asthma", name: "Asthma (Bronchial Asthma & Acute Exacerbation)" },
  { id: "viral_infection", name: "Acute Viral Infection (URTI, Viral Fever & Influenza)" },
  { id: "type_2_diabetes", name: "Type 2 Diabetes Mellitus" },
  { id: "essential_hypertension", name: "Essential Hypertension" },
  { id: "heart_failure", name: "Congestive Heart Failure" },
  { id: "dengue", name: "Dengue Fever" },
  { id: "malaria", name: "Malaria (P. falciparum & P. vivax)" },
  { id: "tuberculosis", name: "Tuberculosis (Pulmonary / Drug-Sensitive)" },
  { id: "pneumonia", name: "Community-Acquired Pneumonia" },
  { id: "typhoid", name: "Enteric Fever (Typhoid)" },
  { id: "cholera", name: "Cholera" },
  { id: "scurvy", name: "Scurvy (Vitamin C Deficiency)" },
  { id: "rickets", name: "Nutritional Rickets (Vitamin D Deficiency)" },
  { id: "beriberi", name: "Beriberi (Thiamine Deficiency)" },
  { id: "night_blindness", name: "Night Blindness / Xerophthalmia" },
  { id: "anaemia", name: "Iron Deficiency Anaemia" },
  { id: "arthritis", name: "Arthritis (OA, RA, Gout)" },
  { id: "cancer", name: "Oncology (Solid Tumors & Hematologic)" }
];

export const EditPatientModal: React.FC<EditPatientModalProps> = ({
  isOpen,
  onClose,
  currentCase,
  onSave
}) => {
  const initial = currentCase.patient_data || {};
  const [age, setAge] = useState<number>(initial.age || 50);
  const [weightKg, setWeightKg] = useState<string>(initial.weight_kg ? String(initial.weight_kg) : "70");
  const [gender, setGender] = useState<string>(initial.gender || "M");
  const [diagnosisId, setDiagnosisId] = useState<string>(initial.diagnosis_id || "asthma");
  
  // Labs
  const [glucose, setGlucose] = useState<string>("");
  const [creatinine, setCreatinine] = useState<string>("");
  const [potassium, setPotassium] = useState<string>("");
  const [platelets, setPlatelets] = useState<string>("");
  const [spo2, setSpo2] = useState<string>("");
  const [peakFlow, setPeakFlow] = useState<string>("");
  const [systolicBp, setSystolicBp] = useState<string>("");
  const [diastolicBp, setDiastolicBp] = useState<string>("");
  const [hemoglobin, setHemoglobin] = useState<string>("");
  const [alt, setAlt] = useState<string>("");
  const [ast, setAst] = useState<string>("");

  const [allergiesText, setAllergiesText] = useState<string>("");
  const [medsText, setMedsText] = useState<string>("");
  const [isSaving, setIsSaving] = useState<boolean>(false);

  // Sync state whenever modal opens or case changes
  useEffect(() => {
    if (!isOpen || !currentCase) return;
    const p = currentCase.patient_data || {};
    const l = p.labs || {};

    setAge(p.age ?? 50);
    setWeightKg(p.weight_kg ? String(p.weight_kg) : "70");
    setGender(p.gender || "M");
    setDiagnosisId(p.diagnosis_id || currentCase.diagnosis_id || "type_2_diabetes");

    setGlucose(l.glucose?.value !== undefined ? String(l.glucose.value) : "");
    setCreatinine(l.creatinine?.value !== undefined ? String(l.creatinine.value) : "");
    setPotassium(l.potassium?.value !== undefined ? String(l.potassium.value) : "");
    setPlatelets(l.platelet?.value !== undefined ? String(l.platelet.value) : "");
    setSpo2(l.spo2?.value !== undefined ? String(l.spo2.value) : "");
    setPeakFlow(l.peak_flow?.value !== undefined ? String(l.peak_flow.value) : "");
    setSystolicBp(l.systolic_bp?.value !== undefined ? String(l.systolic_bp.value) : "");
    setDiastolicBp(l.diastolic_bp?.value !== undefined ? String(l.diastolic_bp.value) : "");
    setHemoglobin(l.hemoglobin?.value !== undefined ? String(l.hemoglobin.value) : "");
    setAlt(l.alt?.value !== undefined ? String(l.alt.value) : "");
    setAst(l.ast?.value !== undefined ? String(l.ast.value) : "");

    setAllergiesText((p.allergies || []).join(", "));
    setMedsText((p.current_medications || []).join(", "));
  }, [isOpen, currentCase]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    const mergedLabs: Record<string, any> = { ...(initial.labs || {}) };

    if (glucose) mergedLabs["glucose"] = { name: "Blood Glucose", value: parseFloat(glucose), unit: "mg/dL" };
    else delete mergedLabs["glucose"];

    if (creatinine) mergedLabs["creatinine"] = { name: "Serum Creatinine", value: parseFloat(creatinine), unit: "mg/dL" };
    else delete mergedLabs["creatinine"];

    if (potassium) mergedLabs["potassium"] = { name: "Serum Potassium", value: parseFloat(potassium), unit: "mEq/L" };
    else delete mergedLabs["potassium"];

    if (platelets) mergedLabs["platelet"] = { name: "Platelets", value: parseFloat(platelets), unit: "/mcL" };
    else delete mergedLabs["platelet"];

    if (spo2) mergedLabs["spo2"] = { name: "Oxygen Saturation (SpO2)", value: parseFloat(spo2), unit: "%" };
    else delete mergedLabs["spo2"];

    if (peakFlow) mergedLabs["peak_flow"] = { name: "Peak Expiratory Flow", value: parseFloat(peakFlow), unit: "L/min" };
    else delete mergedLabs["peak_flow"];

    if (systolicBp) mergedLabs["systolic_bp"] = { name: "Systolic BP", value: parseFloat(systolicBp), unit: "mmHg" };
    else delete mergedLabs["systolic_bp"];

    if (diastolicBp) mergedLabs["diastolic_bp"] = { name: "Diastolic BP", value: parseFloat(diastolicBp), unit: "mmHg" };
    else delete mergedLabs["diastolic_bp"];

    if (hemoglobin) mergedLabs["hemoglobin"] = { name: "Hemoglobin", value: parseFloat(hemoglobin), unit: "g/dL" };
    else delete mergedLabs["hemoglobin"];

    if (alt) mergedLabs["alt"] = { name: "ALT (SGPT)", value: parseFloat(alt), unit: "U/L" };
    else delete mergedLabs["alt"];

    if (ast) mergedLabs["ast"] = { name: "AST (SGOT)", value: parseFloat(ast), unit: "U/L" };
    else delete mergedLabs["ast"];

    const allergies = allergiesText.split(",").map((s) => s.trim()).filter(Boolean);
    const meds = medsText.split(",").map((s) => s.trim()).filter(Boolean);

    const matchedOption = DISEASE_OPTIONS.find((o) => o.id === diagnosisId);
    const diagnosisName = matchedOption ? matchedOption.name : (initial.diagnosis_name || diagnosisId);

    const updated = {
      ...initial,
      age: Number(age),
      weight_kg: weightKg ? parseFloat(weightKg) : undefined,
      gender,
      diagnosis_id: diagnosisId,
      diagnosis_name: diagnosisName,
      allergies,
      current_medications: meds,
      labs: mergedLabs
    };

    try {
      await onSave(updated);
      onClose();
    } catch (err) {
      console.error("Failed to update patient data:", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      className="citation-modal-overlay"
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(9, 30, 58, 0.7)",
        backdropFilter: "blur(4px)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1rem"
      }}
    >
      <div
        className="citation-modal-content"
        style={{
          background: "var(--bg-card)",
          maxWidth: "620px",
          width: "100%",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.25), 0 10px 10px -5px rgba(0, 0, 0, 0.15)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          maxHeight: "92vh"
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "1.25rem 1.5rem",
            borderBottom: "1px solid rgba(255,255,255,0.1)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "linear-gradient(135deg, #091e3a 0%, #0f766e 100%)",
            color: "white"
          }}
        >
          <div>
            <h3 style={{ margin: 0, fontSize: "1.15rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>✏️</span> Edit Patient Clinical Facts
            </h3>
            <div style={{ fontSize: "0.75rem", color: "#cbd5e1", marginTop: "2px" }}>
              Case ID: <strong>{currentCase.case_id}</strong> (v{currentCase.patient_version}) • Real-time clinical safety re-evaluation
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,0.15)",
              border: "none",
              color: "white",
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              fontSize: "1rem",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            ✕
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: "1.25rem 1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem" }}>
          
          {/* Confirmed Disease Selector */}
          <div>
            <label className="form-label" style={{ fontWeight: 600, color: "var(--teal-dark)", fontSize: "0.82rem" }}>
              Confirmed Clinical Diagnosis / Presentation
            </label>
            <select
              className="form-input"
              value={diagnosisId}
              onChange={(e) => setDiagnosisId(e.target.value)}
              style={{ fontWeight: 600, background: "var(--bg-subtle)" }}
              required
            >
              {DISEASE_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.name}
                </option>
              ))}
            </select>
          </div>

          {/* Demographics Row */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
            <div>
              <label className="form-label">Age (years)</label>
              <input
                type="number"
                className="form-input"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                min={0}
                max={125}
                required
              />
            </div>
            <div>
              <label className="form-label">Weight (kg)</label>
              <input
                type="number"
                step="0.5"
                className="form-input"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
                placeholder="70"
              />
            </div>
            <div>
              <label className="form-label">Biological Sex</label>
              <select className="form-input" value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="M">Male (M)</option>
                <option value="F">Female (F)</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          {/* Respiratory & Vitals Section */}
          <div style={{ background: "rgba(13, 148, 136, 0.06)", border: "1px solid var(--teal-border)", padding: "0.85rem", borderRadius: "var(--radius-sm)" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--teal-dark)", textTransform: "uppercase", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span>🫁</span> Respiratory & Vital Signs (Asthma & Viral Focus)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "0.6rem" }}>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>SpO2 (%)</label>
                <input
                  type="number"
                  step="1"
                  className="form-input"
                  value={spo2}
                  onChange={(e) => setSpo2(e.target.value)}
                  placeholder="e.g. 96"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Peak Flow (L/min)</label>
                <input
                  type="number"
                  step="5"
                  className="form-input"
                  value={peakFlow}
                  onChange={(e) => setPeakFlow(e.target.value)}
                  placeholder="e.g. 380"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Systolic BP</label>
                <input
                  type="number"
                  className="form-input"
                  value={systolicBp}
                  onChange={(e) => setSystolicBp(e.target.value)}
                  placeholder="e.g. 120"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Diastolic BP</label>
                <input
                  type="number"
                  className="form-input"
                  value={diastolicBp}
                  onChange={(e) => setDiastolicBp(e.target.value)}
                  placeholder="e.g. 80"
                />
              </div>
            </div>
          </div>

          {/* Laboratory Parameters Section */}
          <div style={{ background: "var(--bg-subtle)", padding: "0.85rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-light)" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--hospital-navy)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
              🧪 Renal, Metabolic & Blood Markers
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.6rem" }}>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Serum Creatinine (mg/dL)</label>
                <input
                  type="number"
                  step="0.05"
                  className="form-input"
                  value={creatinine}
                  onChange={(e) => setCreatinine(e.target.value)}
                  placeholder="e.g. 1.0"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Blood Glucose (mg/dL)</label>
                <input
                  type="number"
                  className="form-input"
                  value={glucose}
                  onChange={(e) => setGlucose(e.target.value)}
                  placeholder="e.g. 110"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Potassium (mEq/L)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-input"
                  value={potassium}
                  onChange={(e) => setPotassium(e.target.value)}
                  placeholder="e.g. 4.2"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Platelets (/mcL)</label>
                <input
                  type="number"
                  className="form-input"
                  value={platelets}
                  onChange={(e) => setPlatelets(e.target.value)}
                  placeholder="e.g. 210000"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>Hemoglobin (g/dL)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-input"
                  value={hemoglobin}
                  onChange={(e) => setHemoglobin(e.target.value)}
                  placeholder="e.g. 13.5"
                />
              </div>
              <div>
                <label className="form-label" style={{ fontSize: "0.72rem" }}>ALT / SGPT (U/L)</label>
                <input
                  type="number"
                  className="form-input"
                  value={alt}
                  onChange={(e) => setAlt(e.target.value)}
                  placeholder="e.g. 28"
                />
              </div>
            </div>
          </div>

          {/* Current Medications */}
          <div>
            <label className="form-label">Current Active Medications (comma separated)</label>
            <input
              type="text"
              className="form-input"
              value={medsText}
              onChange={(e) => setMedsText(e.target.value)}
              placeholder="e.g. Budesonide-Formoterol Inhaler, Paracetamol 650mg, Telmisartan 40mg"
            />
          </div>

          {/* Allergies */}
          <div>
            <label className="form-label">Documented Allergies (comma separated, or blank for NKDA)</label>
            <input
              type="text"
              className="form-input"
              value={allergiesText}
              onChange={(e) => setAllergiesText(e.target.value)}
              placeholder="e.g. Aspirin (AERD), Penicillin, Sulfa drugs"
            />
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "0.5rem" }}>
            <button type="button" onClick={onClose} className="clinical-btn-secondary">
              Cancel
            </button>
            <button
              type="submit"
              className="clinical-btn-primary"
              disabled={isSaving}
              style={{ minWidth: "220px", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}
            >
              {isSaving ? "Saving & Re-evaluating..." : "Update Patient Facts & Recalculate"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
