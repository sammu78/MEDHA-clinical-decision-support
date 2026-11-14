import React, { useState, useEffect } from "react";
import type { ClinicalCase } from "../types";
import { DISEASE_OPTIONS } from "./EditPatientModal";

interface ClinicalIntakeCardProps {
  currentCase: ClinicalCase | null;
  onSaveAndAssess: (updatedPatient: Record<string, any>) => Promise<void>;
  isLoading: boolean;
}

export const OPD_PRESETS = [
  {
    label: "⚡ T2D (Normal Renal)",
    diseaseId: "type_2_diabetes",
    age: 54,
    gender: "M",
    weight: 74,
    labs: {
      glucose: 178,
      creatinine: 1.0,
      potassium: 4.3,
      systolic_bp: 132,
      diastolic_bp: 82
    },
    allergies: "",
    meds: ""
  },
  {
    label: "⚡ T2D + CKD (eGFR 42)",
    diseaseId: "type_2_diabetes",
    age: 62,
    gender: "M",
    weight: 68,
    labs: {
      glucose: 195,
      creatinine: 1.8,
      potassium: 4.8,
      systolic_bp: 138,
      diastolic_bp: 86
    },
    allergies: "Sulfa drugs",
    meds: "Amlodipine 5mg"
  },
  {
    label: "⚡ HTN + High K+ (5.8)",
    diseaseId: "essential_hypertension",
    age: 65,
    gender: "F",
    weight: 64,
    labs: {
      potassium: 5.8,
      creatinine: 1.3,
      systolic_bp: 158,
      diastolic_bp: 96
    },
    allergies: "",
    meds: ""
  },
  {
    label: "⚡ Dengue (Platelets 45k)",
    diseaseId: "dengue",
    age: 28,
    gender: "F",
    weight: 56,
    labs: {
      platelet: 45000,
      systolic_bp: 110,
      diastolic_bp: 74
    },
    allergies: "",
    meds: ""
  },
  {
    label: "⚡ Asthma (Acute Exacerbation)",
    diseaseId: "asthma",
    age: 34,
    gender: "M",
    weight: 70,
    labs: {
      spo2: 93,
      peak_flow: 260
    },
    allergies: "Aspirin",
    meds: "Salbutamol inhaler"
  },
  {
    label: "⚡ Pulmonary TB (54 kg)",
    diseaseId: "tuberculosis",
    age: 42,
    gender: "M",
    weight: 54,
    labs: {
      alt: 28,
      ast: 32,
      hemoglobin: 11.2
    },
    allergies: "",
    meds: ""
  },
  {
    label: "⚡ Scurvy (Pediatric 8yo)",
    diseaseId: "scurvy",
    age: 8,
    gender: "M",
    weight: 22,
    labs: {
      hemoglobin: 9.5
    },
    allergies: "",
    meds: ""
  }
];

export const ClinicalIntakeCard: React.FC<ClinicalIntakeCardProps> = ({
  currentCase,
  onSaveAndAssess,
  isLoading
}) => {
  const initial = currentCase?.patient_data || {};
  const [age, setAge] = useState<number>(initial.age || 52);
  const [weightKg, setWeightKg] = useState<string>(initial.weight_kg ? String(initial.weight_kg) : "70");
  const [gender, setGender] = useState<string>(initial.gender || "M");
  const [diagnosisId, setDiagnosisId] = useState<string>(
    initial.diagnosis_id || currentCase?.diagnosis_id || "type_2_diabetes"
  );

  // Labs
  const [glucose, setGlucose] = useState<string>("");
  const [creatinine, setCreatinine] = useState<string>("");
  const [potassium, setPotassium] = useState<string>("");
  const [platelets, setPlatelets] = useState<string>("");
  const [systolicBp, setSystolicBp] = useState<string>("");
  const [diastolicBp, setDiastolicBp] = useState<string>("");
  const [spo2, setSpo2] = useState<string>("");
  const [peakFlow, setPeakFlow] = useState<string>("");
  const [hemoglobin, setHemoglobin] = useState<string>("");
  const [alt, setAlt] = useState<string>("");
  const [ast, setAst] = useState<string>("");

  const [allergiesText, setAllergiesText] = useState<string>("");
  const [medsText, setMedsText] = useState<string>("");

  // Sync with currentCase changes
  useEffect(() => {
    if (!currentCase) return;
    const p = currentCase.patient_data || {};
    const l = p.labs || {};

    setAge(p.age ?? 52);
    setWeightKg(p.weight_kg ? String(p.weight_kg) : "70");
    setGender(p.gender || "M");
    setDiagnosisId(p.diagnosis_id || currentCase.diagnosis_id || "type_2_diabetes");

    setGlucose(l.glucose?.value !== undefined ? String(l.glucose.value) : "");
    setCreatinine(l.creatinine?.value !== undefined ? String(l.creatinine.value) : "");
    setPotassium(l.potassium?.value !== undefined ? String(l.potassium.value) : "");
    setPlatelets(l.platelet?.value !== undefined ? String(l.platelet.value) : "");
    setSystolicBp(l.systolic_bp?.value !== undefined ? String(l.systolic_bp.value) : "");
    setDiastolicBp(l.diastolic_bp?.value !== undefined ? String(l.diastolic_bp.value) : "");
    setSpo2(l.spo2?.value !== undefined ? String(l.spo2.value) : "");
    setPeakFlow(l.peak_flow?.value !== undefined ? String(l.peak_flow.value) : "");
    setHemoglobin(l.hemoglobin?.value !== undefined ? String(l.hemoglobin.value) : "");
    setAlt(l.alt?.value !== undefined ? String(l.alt.value) : "");
    setAst(l.ast?.value !== undefined ? String(l.ast.value) : "");

    setAllergiesText((p.allergies || []).join(", "));
    setMedsText((p.current_medications || []).join(", "));
  }, [currentCase?.case_id, currentCase?.patient_version]);

  // Live eGFR estimation
  const crVal = parseFloat(creatinine);
  let liveEgfr: number | null = null;
  if (!isNaN(crVal) && crVal > 0 && age > 0) {
    const isFemale = gender === "F";
    const kappa = isFemale ? 0.7 : 0.9;
    const alpha = isFemale ? -0.241 : -0.302;
    const genderMult = isFemale ? 1.012 : 1.0;
    const scrRatio = crVal / kappa;
    const val =
      142 *
      Math.pow(Math.min(scrRatio, 1.0), alpha) *
      Math.pow(Math.max(scrRatio, 1.0), -1.2) *
      Math.pow(0.9938, age) *
      genderMult;
    liveEgfr = Math.round(val * 10) / 10;
  }

  const applyPreset = (preset: typeof OPD_PRESETS[0]) => {
    setDiagnosisId(preset.diseaseId);
    setAge(preset.age);
    setGender(preset.gender);
    setWeightKg(String(preset.weight));
    setGlucose(preset.labs.glucose !== undefined ? String(preset.labs.glucose) : "");
    setCreatinine(preset.labs.creatinine !== undefined ? String(preset.labs.creatinine) : "");
    setPotassium(preset.labs.potassium !== undefined ? String(preset.labs.potassium) : "");
    setPlatelets(preset.labs.platelet !== undefined ? String(preset.labs.platelet) : "");
    setSystolicBp(preset.labs.systolic_bp !== undefined ? String(preset.labs.systolic_bp) : "");
    setDiastolicBp(preset.labs.diastolic_bp !== undefined ? String(preset.labs.diastolic_bp) : "");
    setSpo2(preset.labs.spo2 !== undefined ? String(preset.labs.spo2) : "");
    setPeakFlow(preset.labs.peak_flow !== undefined ? String(preset.labs.peak_flow) : "");
    setHemoglobin(preset.labs.hemoglobin !== undefined ? String(preset.labs.hemoglobin) : "");
    setAlt(preset.labs.alt !== undefined ? String(preset.labs.alt) : "");
    setAst(preset.labs.ast !== undefined ? String(preset.labs.ast) : "");
    setAllergiesText(preset.allergies);
    setMedsText(preset.meds);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    const mergedLabs: Record<string, any> = {};

    if (glucose) mergedLabs["glucose"] = { name: "Blood Glucose", value: parseFloat(glucose), unit: "mg/dL" };
    if (creatinine) mergedLabs["creatinine"] = { name: "Serum Creatinine", value: parseFloat(creatinine), unit: "mg/dL" };
    if (potassium) mergedLabs["potassium"] = { name: "Serum Potassium", value: parseFloat(potassium), unit: "mEq/L" };
    if (platelets) mergedLabs["platelet"] = { name: "Platelets", value: parseFloat(platelets), unit: "/mcL" };
    if (systolicBp) mergedLabs["systolic_bp"] = { name: "Systolic BP", value: parseFloat(systolicBp), unit: "mmHg" };
    if (diastolicBp) mergedLabs["diastolic_bp"] = { name: "Diastolic BP", value: parseFloat(diastolicBp), unit: "mmHg" };
    if (spo2) mergedLabs["spo2"] = { name: "SpO2", value: parseFloat(spo2), unit: "%" };
    if (peakFlow) mergedLabs["peak_flow"] = { name: "Peak Flow", value: parseFloat(peakFlow), unit: "L/min" };
    if (hemoglobin) mergedLabs["hemoglobin"] = { name: "Hemoglobin", value: parseFloat(hemoglobin), unit: "g/dL" };
    if (alt) mergedLabs["alt"] = { name: "ALT", value: parseFloat(alt), unit: "U/L" };
    if (ast) mergedLabs["ast"] = { name: "AST", value: parseFloat(ast), unit: "U/L" };

    const selectedDisease = DISEASE_OPTIONS.find((d) => d.id === diagnosisId);
    const diagnosisName = selectedDisease ? selectedDisease.name : diagnosisId;

    const updatedPatient: Record<string, any> = {
      diagnosis_id: diagnosisId,
      diagnosis_name: diagnosisName,
      age: Number(age),
      weight_kg: weightKg ? parseFloat(weightKg) : null,
      gender: gender,
      allergies: allergiesText.split(",").map((s) => s.trim()).filter(Boolean),
      current_medications: medsText.split(",").map((s) => s.trim()).filter(Boolean),
      labs: mergedLabs
    };

    await onSaveAndAssess(updatedPatient);
  };

  return (
    <div className="clinical-intake-card">
      <div className="intake-card-header">
        <div className="intake-step-indicator">
          <span className="step-badge">STEP 1</span>
          <div>
            <h3 className="intake-title">Patient Clinical Intake & Parameters</h3>
            <p className="intake-subtitle">
              Enter patient details or click a preset below. Dosage is evaluated against verified clinical practice guidelines.
            </p>
          </div>
        </div>
      </div>

      {/* OPD Presets Strip */}
      <div className="opd-presets-strip">
        <span className="presets-label">⚡ Fast-Fill OPD Scenarios:</span>
        <div className="presets-chips-container">
          {OPD_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip-btn"
              onClick={() => applyPreset(preset)}
              title={`Load ${preset.label}`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleFormSubmit} className="intake-form">
        {/* Section 1: Demographics & Indication */}
        <div className="intake-form-grid">
          <div className="form-group col-span-2">
            <label className="form-label">
              Clinical Diagnosis / Primary Indication <span className="req-star">*</span>
            </label>
            <select
              className="form-input form-select"
              value={diagnosisId}
              onChange={(e) => setDiagnosisId(e.target.value)}
              required
            >
              {DISEASE_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Age (Years) *</label>
            <input
              type="number"
              className="form-input"
              value={age}
              min="0"
              max="125"
              onChange={(e) => setAge(parseInt(e.target.value) || 0)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Sex</label>
            <select
              className="form-input form-select"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Weight (kg) *</label>
            <input
              type="number"
              step="0.5"
              className="form-input"
              placeholder="e.g. 70"
              value={weightKg}
              onChange={(e) => setWeightKg(e.target.value)}
            />
          </div>
        </div>

        {/* Section 2: Vitals & Key Safety Labs */}
        <div className="intake-labs-box">
          <div className="labs-box-header">
            <span>Essential Vitals & Organ Clearance Markers</span>
            {liveEgfr !== null && (
              <span
                className="live-egfr-tag"
                style={{
                  color: liveEgfr < 30 ? "#ef4444" : liveEgfr < 60 ? "#f59e0b" : "#10b981"
                }}
              >
                Computed eGFR: <strong>{liveEgfr} mL/min/1.73m²</strong>
              </span>
            )}
          </div>

          <div className="labs-inputs-grid">
            <div className="lab-input-cell">
              <label className="cell-label">Blood Glucose (mg/dL)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 175"
                value={glucose}
                onChange={(e) => setGlucose(e.target.value)}
              />
            </div>

            <div className="lab-input-cell highlight-cell">
              <label className="cell-label">
                Serum Creatinine (mg/dL) <span>(Renal Gate)</span>
              </label>
              <input
                type="number"
                step="0.05"
                className="form-input"
                placeholder="e.g. 1.1"
                value={creatinine}
                onChange={(e) => setCreatinine(e.target.value)}
              />
            </div>

            <div className="lab-input-cell">
              <label className="cell-label">Serum Potassium (mEq/L)</label>
              <input
                type="number"
                step="0.1"
                className="form-input"
                placeholder="e.g. 4.3"
                value={potassium}
                onChange={(e) => setPotassium(e.target.value)}
              />
            </div>

            <div className="lab-input-cell">
              <label className="cell-label">Platelets (/mcL)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 180000"
                value={platelets}
                onChange={(e) => setPlatelets(e.target.value)}
              />
            </div>

            <div className="lab-input-cell">
              <label className="cell-label">Blood Pressure (Systolic / Diastolic)</label>
              <div style={{ display: "flex", gap: "6px" }}>
                <input
                  type="number"
                  className="form-input"
                  placeholder="Sys (120)"
                  value={systolicBp}
                  onChange={(e) => setSystolicBp(e.target.value)}
                />
                <span style={{ alignSelf: "center", color: "var(--text-muted)" }}>/</span>
                <input
                  type="number"
                  className="form-input"
                  placeholder="Dia (80)"
                  value={diastolicBp}
                  onChange={(e) => setDiastolicBp(e.target.value)}
                />
              </div>
            </div>

            <div className="lab-input-cell">
              <label className="cell-label">SpO2 (%) / Peak Flow (L/min)</label>
              <div style={{ display: "flex", gap: "6px" }}>
                <input
                  type="number"
                  className="form-input"
                  placeholder="SpO2 %"
                  value={spo2}
                  onChange={(e) => setSpo2(e.target.value)}
                />
                <input
                  type="number"
                  className="form-input"
                  placeholder="Peak Flow"
                  value={peakFlow}
                  onChange={(e) => setPeakFlow(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Safety Flags (Allergies & Current Meds) */}
        <div className="intake-flags-grid">
          <div className="form-group">
            <label className="form-label">Known Drug Allergies (comma separated)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Penicillin, Sulfa, Aspirin"
              value={allergiesText}
              onChange={(e) => setAllergiesText(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Current Medications (comma separated)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Amlodipine 5mg, Atorvastatin 20mg"
              value={medsText}
              onChange={(e) => setMedsText(e.target.value)}
            />
          </div>
        </div>

        {/* CTA Button Strip */}
        <div className="intake-cta-strip">
          <button
            type="submit"
            className="clinical-cta-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner-inline" /> Evaluating Safety & Dosing Engine...
              </>
            ) : (
              <>
                ⚡ Evaluate Safety & Recommend Dosage
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
