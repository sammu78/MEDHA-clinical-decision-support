import React, { useState, useEffect } from "react";
import type { PatientAssessmentRequest, AssessmentResponse, SupportedCase } from "../types";
import { assessPatient, fetchSupportedCases } from "../services/api";

export const SimpleInputOutputPage: React.FC = () => {
  // Navigation / Workflow view state: "input" | "loading" | "result"
  const [viewState, setViewState] = useState<"input" | "loading" | "result">("input");
  const [loadingMessage, setLoadingMessage] = useState<string>("Validating patient information…");

  // Form Fields State
  const [patientId, setPatientId] = useState<string>("PT-8492");
  const [diagnosisId, setDiagnosisId] = useState<string>("type_2_diabetes");
  const [age, setAge] = useState<number | "">(58);
  const [gender, setGender] = useState<"M" | "F">("M");
  const [weightKg, setWeightKg] = useState<number | "">(78.5);

  // Default measurement timestamp (today's date and current time in local format)
  const defaultTimestamp = new Date().toISOString().slice(0, 16);
  const [labTimestamp, setLabTimestamp] = useState<string>(defaultTimestamp);

  // The 5 Pre-Decision Lab Results
  const [glucose, setGlucose] = useState<number | "">(185);
  const [creatinine, setCreatinine] = useState<number | "">(1.1);
  const [potassium, setPotassium] = useState<number | "">(4.3);
  const [sodium, setSodium] = useState<number | "">(139);
  const [bun, setBun] = useState<number | "">(18);

  // Optional Clinical Context
  const [allergiesText, setAllergiesText] = useState<string>("");
  const [medicationsText, setMedicationsText] = useState<string>("Atorvastatin 20mg PO daily");
  const [clinicalNotes, setClinicalNotes] = useState<string>("");

  // System & Backend Data
  const [supportedCases, setSupportedCases] = useState<SupportedCase[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [result, setResult] = useState<AssessmentResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  // UI Interactive States
  const [showEvidenceModal, setShowEvidenceModal] = useState<boolean>(false);
  const [explanationOpen, setExplanationOpen] = useState<boolean>(true);

  // Fetch supported cases from backend on mount
  useEffect(() => {
    fetchSupportedCases()
      .then((data) => {
        if (data && data.length > 0) {
          setSupportedCases(data);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch supported cases, using default fallbacks:", err);
      });
  }, []);

  // Quick Clinical Presets for Evaluators & Clinicians
  const applyPreset = (preset: "t2d_normal" | "t2d_hypo" | "t2d_ckd" | "htn_hyperk" | "hf_eligible") => {
    setValidationErrors([]);
    setApiError(null);
    const now = new Date().toISOString().slice(0, 16);
    setLabTimestamp(now);

    if (preset === "t2d_normal") {
      setPatientId("PT-T2D-01");
      setDiagnosisId("type_2_diabetes");
      setAge(58);
      setGender("M");
      setWeightKg(78.5);
      setGlucose(185);
      setCreatinine(1.1);
      setPotassium(4.3);
      setSodium(139);
      setBun(18);
      setAllergiesText("");
      setMedicationsText("Atorvastatin 20mg PO daily");
      setClinicalNotes("Routine outpatient diabetes review. Renal function intact.");
    } else if (preset === "t2d_hypo") {
      setPatientId("PT-HYPO-02");
      setDiagnosisId("type_2_diabetes");
      setAge(64);
      setGender("F");
      setWeightKg(66.0);
      setGlucose(58); // Acute hypoglycemia (< 70 mg/dL)
      setCreatinine(1.0);
      setPotassium(4.1);
      setSodium(138);
      setBun(16);
      setAllergiesText("");
      setMedicationsText("Glipizide 5mg PO");
      setClinicalNotes("Presented with tremors and diaphoresis. Blood glucose critically low.");
    } else if (preset === "t2d_ckd") {
      setPatientId("PT-CKD-03");
      setDiagnosisId("type_2_diabetes");
      setAge(72);
      setGender("M");
      setWeightKg(70.0);
      setGlucose(210);
      setCreatinine(2.8); // Severe CKD (eGFR ~ 22 mL/min/1.73m²)
      setPotassium(4.9);
      setSodium(136);
      setBun(45);
      setAllergiesText("");
      setMedicationsText("Aspirin 81mg PO daily");
      setClinicalNotes("Stage 4 Chronic Kidney Disease. Monitoring for metformin lactic acidosis risk.");
    } else if (preset === "htn_hyperk") {
      setPatientId("PT-HTN-04");
      setDiagnosisId("essential_hypertension");
      setAge(65);
      setGender("M");
      setWeightKg(82.0);
      setGlucose(115);
      setCreatinine(1.4);
      setPotassium(5.8); // Hyperkalemia (> 5.5 mEq/L)
      setSodium(140);
      setBun(24);
      setAllergiesText("");
      setMedicationsText("Spironolactone 25mg PO");
      setClinicalNotes("Hypertension evaluation. Elevated serum potassium.");
    } else if (preset === "hf_eligible") {
      setPatientId("PT-CHF-05");
      setDiagnosisId("heart_failure");
      setAge(67);
      setGender("M");
      setWeightKg(86.0);
      setGlucose(124);
      setCreatinine(1.2);
      setPotassium(4.0);
      setSodium(137);
      setBun(26);
      setAllergiesText("Penicillin");
      setMedicationsText("Metoprolol Succinate 50mg PO");
      setClinicalNotes("Congestive heart failure with peripheral volume overload.");
    }
  };

  // Form Validation
  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!diagnosisId) {
      errors.push("Clinical Diagnosis / Condition is required.");
    }
    if (age === "" || age <= 0 || age > 125) {
      errors.push("Patient age must be between 1 and 125 years.");
    }
    if (weightKg === "" || weightKg <= 2 || weightKg > 400) {
      errors.push("Body weight is required and must be between 2 and 400 kg.");
    }
    if (glucose === "" || glucose < 20 || glucose > 1500) {
      errors.push("Valid Blood Glucose (mg/dL) is required (20–1500 mg/dL).");
    }
    if (creatinine === "" || creatinine < 0.1 || creatinine > 30) {
      errors.push("Valid Serum Creatinine (mg/dL) is required (0.1–30.0 mg/dL).");
    }
    if (potassium === "" || potassium < 1.0 || potassium > 12.0) {
      errors.push("Valid Serum Potassium (mEq/L) is required (1.0–12.0 mEq/L).");
    }
    if (sodium === "" || sodium < 80 || sodium > 200) {
      errors.push("Valid Serum Sodium (mEq/L) is required (80–200 mEq/L).");
    }
    if (bun === "" || bun < 1 || bun > 300) {
      errors.push("Valid Blood Urea Nitrogen / BUN (mg/dL) is required (1–300 mg/dL).");
    }
    if (!labTimestamp) {
      errors.push("Laboratory measurement timestamp is required for audit provenance.");
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Submit Handler with Sequential Clinical Loading Progression
  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!validateForm()) return;

    setViewState("loading");
    setApiError(null);

    // Sequential loading steps as requested in Prompt Section 4
    setLoadingMessage("Validating patient information…");

    const timer1 = setTimeout(() => {
      setLoadingMessage("Checking laboratory data and clinical safety…");
    }, 450);

    const timer2 = setTimeout(() => {
      setLoadingMessage("Evaluating available medicine options…");
    }, 900);

    const timer3 = setTimeout(() => {
      setLoadingMessage("Preparing assessment results…");
    }, 1350);

    const payload: PatientAssessmentRequest = {
      diagnosis_id: diagnosisId,
      age: Number(age),
      gender: gender,
      weight_kg: Number(weightKg),
      allergies: allergiesText
        ? allergiesText.split(",").map((s) => s.trim()).filter(Boolean)
        : [],
      current_medications: medicationsText
        ? medicationsText.split(",").map((s) => s.trim()).filter(Boolean)
        : [],
      existing_conditions: clinicalNotes ? [clinicalNotes] : [],
      labs: {
        glucose: { name: "GLUCOSE", value: Number(glucose), unit: "mg/dL", measurement_date: labTimestamp },
        creatinine: { name: "CREATININE", value: Number(creatinine), unit: "mg/dL", measurement_date: labTimestamp },
        potassium: { name: "POTASSIUM", value: Number(potassium), unit: "mEq/L", measurement_date: labTimestamp },
        sodium: { name: "SODIUM", value: Number(sodium), unit: "mEq/L", measurement_date: labTimestamp },
        bun: { name: "BUN", value: Number(bun), unit: "mg/dL", measurement_date: labTimestamp }
      }
    };

    try {
      const response = await assessPatient(payload);
      // Wait for sequential messages to complete nicely
      setTimeout(() => {
        setResult(response);
        setViewState("result");
      }, 1600);
    } catch (err: any) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      console.error("Assessment request error:", err);
      setApiError(err?.message || "Failed to complete clinical evaluation. Please check backend connection.");
      setViewState("input");
    }
  };

  // Actions
  const handleNewAssessment = () => {
    setPatientId(`PT-${Math.floor(1000 + Math.random() * 9000)}`);
    setAge(58);
    setGender("M");
    setWeightKg(75);
    setGlucose(180);
    setCreatinine(1.1);
    setPotassium(4.2);
    setSodium(139);
    setBun(18);
    setAllergiesText("");
    setMedicationsText("");
    setClinicalNotes("");
    setResult(null);
    setValidationErrors([]);
    setApiError(null);
    setViewState("input");
  };

  const handleEditPatient = () => {
    setViewState("input");
  };

  const handlePrint = () => {
    window.print();
  };

  // Helper to resolve Assessment Status
  const getStatusDisplay = () => {
    if (!result) return { label: "Unable to complete assessment", badgeColor: "#64748b", bg: "#f1f5f9", icon: "❓" };
    switch (result.status) {
      case "PROPOSAL_AVAILABLE":
        return {
          label: "Assessment completed",
          badgeColor: "#166534",
          bg: "#dcfce7",
          border: "#86efac",
          icon: "✅"
        };
      case "MORE_INFO_NEEDED":
        return {
          label: "Additional information required",
          badgeColor: "#92400e",
          bg: "#fef3c7",
          border: "#fcd34d",
          icon: "⚠️"
        };
      case "CONTRAINDICATED":
        return {
          label: "Recommendation withheld by safety checks",
          badgeColor: "#991b1b",
          bg: "#fee2e2",
          border: "#fca5a5",
          icon: "⛔"
        };
      default:
        return {
          label: "Unable to complete assessment",
          badgeColor: "#475569",
          bg: "#f1f5f9",
          border: "#cbd5e1",
          icon: "ℹ️"
        };
    }
  };

  return (
    <div style={{ maxWidth: "1080px", margin: "0 auto", padding: "1.5rem 1rem", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* =========================================================================
          APPLICATION HEADER (Strictly follows Prompt Section 3)
          ========================================================================= */}
      <header style={{ textAlign: "center", marginBottom: "2rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "1.25rem" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "10px", marginBottom: "0.4rem" }}>
          <span style={{ fontSize: "1.8rem" }}>🩺</span>
          <h1 style={{ fontSize: "1.85rem", fontWeight: 800, color: "#0f2744", margin: 0, letterSpacing: "-0.02em" }}>
            MEDHA — Medicine & Dosage Assessment
          </h1>
        </div>
        <p style={{ fontSize: "1rem", color: "#475569", margin: "0.25rem auto 0", maxWidth: "720px", lineHeight: 1.5 }}>
          Enter patient information and available laboratory results to evaluate medicine options and clinical safety.
        </p>

        {/* Quick presets row */}
        {viewState === "input" && (
          <div style={{ marginTop: "1.25rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 600 }}>Clinical Vignettes:</span>
            <button
              type="button"
              onClick={() => applyPreset("t2d_normal")}
              style={{ background: "#f8fafc", border: "1px solid #cbd5e1", borderRadius: "6px", padding: "0.3rem 0.65rem", fontSize: "0.78rem", cursor: "pointer", color: "#0f2744", fontWeight: 500 }}
            >
              🩺 Adult T2D (Normal)
            </button>
            <button
              type="button"
              onClick={() => applyPreset("t2d_hypo")}
              style={{ background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: "6px", padding: "0.3rem 0.65rem", fontSize: "0.78rem", cursor: "pointer", color: "#b91c1c", fontWeight: 600 }}
            >
              ⚠️ Hypoglycemia (&lt;70 mg/dL)
            </button>
            <button
              type="button"
              onClick={() => applyPreset("t2d_ckd")}
              style={{ background: "#fff7ed", border: "1px solid #fed7aa", borderRadius: "6px", padding: "0.3rem 0.65rem", fontSize: "0.78rem", cursor: "pointer", color: "#c2410c", fontWeight: 600 }}
            >
              🚨 Severe CKD (eGFR 22)
            </button>
            <button
              type="button"
              onClick={() => applyPreset("htn_hyperk")}
              style={{ background: "#fff7ed", border: "1px solid #fed7aa", borderRadius: "6px", padding: "0.3rem 0.65rem", fontSize: "0.78rem", cursor: "pointer", color: "#c2410c", fontWeight: 600 }}
            >
              ❤️ Hypertension + High K⁺ (5.8)
            </button>
            <button
              type="button"
              onClick={() => applyPreset("hf_eligible")}
              style={{ background: "#f0fdfa", border: "1px solid #99f6e4", borderRadius: "6px", padding: "0.3rem 0.65rem", fontSize: "0.78rem", cursor: "pointer", color: "#0d9488", fontWeight: 600 }}
            >
              🫀 Heart Failure (Furosemide)
            </button>
          </div>
        )}
      </header>

      {/* API / Backend Error Banner */}
      {apiError && (
        <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", padding: "1rem", color: "#991b1b", marginBottom: "1.5rem" }}>
          <strong>Assessment Error:</strong> {apiError}
        </div>
      )}

      {/* Validation Errors Alert */}
      {validationErrors.length > 0 && viewState === "input" && (
        <div style={{ background: "#fffbeb", border: "1px solid #fde68a", borderRadius: "8px", padding: "1rem", color: "#92400e", marginBottom: "1.5rem" }}>
          <div style={{ fontWeight: 700, marginBottom: "0.4rem" }}>⚠️ Required Information Missing Before Submission:</div>
          <ul style={{ margin: "0 0 0 1.25rem", fontSize: "0.88rem" }}>
            {validationErrors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {/* =========================================================================
          VIEW 1: CLEAN INPUT FORM SCREEN (Prompt Section 3)
          ========================================================================= */}
      {viewState === "input" && (
        <form onSubmit={handleAnalyze} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Card 1: Patient Information */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "1.25rem", borderBottom: "2px solid #0d9488", paddingBottom: "0.5rem" }}>
              <span style={{ fontSize: "1.2rem" }}>👤</span>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#0f2744", margin: 0 }}>
                1. Patient Information
              </h2>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
              {/* Patient or Case ID (optional) */}
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Patient / Case ID <span style={{ color: "#94a3b8", fontWeight: 400 }}>(optional)</span>
                </label>
                <input
                  type="text"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  placeholder="e.g. PT-8492"
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.92rem", color: "#0f172a" }}
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Unique medical record identifier</span>
              </div>

              {/* Diagnosis / Clinical Condition */}
              <div style={{ gridColumn: "span 2" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Diagnosis / Clinical Condition <span style={{ color: "#dc2626" }}>*</span>
                </label>
                <select
                  value={diagnosisId}
                  onChange={(e) => setDiagnosisId(e.target.value)}
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.92rem", color: "#0f172a", backgroundColor: "#fff" }}
                  required
                >
                  <option value="type_2_diabetes">Type 2 Diabetes Mellitus (ICD-10: E11)</option>
                  <option value="essential_hypertension">Essential Hypertension (ICD-10: I10)</option>
                  <option value="heart_failure">Congestive Heart Failure (ICD-10: I50)</option>
                  {supportedCases
                    .filter((c) => !["type_2_diabetes", "essential_hypertension", "heart_failure"].includes(c.case_id))
                    .map((c) => (
                      <option key={c.case_id} value={c.case_id}>
                        {c.diagnosis_name} ({c.case_id})
                      </option>
                    ))}
                </select>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Guides evidence-based clinical candidate filtering</span>
              </div>

              {/* Age */}
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Age (years) <span style={{ color: "#dc2626" }}>*</span>
                </label>
                <input
                  type="number"
                  min={1}
                  max={125}
                  value={age}
                  onChange={(e) => setAge(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="58"
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.92rem", color: "#0f172a" }}
                  required
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Adult dosing baseline (1–125 yrs)</span>
              </div>

              {/* Sex */}
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Sex (Biological) <span style={{ color: "#dc2626" }}>*</span>
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as "M" | "F")}
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.92rem", color: "#0f172a", backgroundColor: "#fff" }}
                  required
                >
                  <option value="M">Male (M)</option>
                  <option value="F">Female (F)</option>
                </select>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Required for CKD-EPI / Cockcroft-Gault</span>
              </div>

              {/* Weight */}
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Weight (kg) <span style={{ color: "#dc2626" }}>*</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min={2}
                  max={400}
                  value={weightKg}
                  onChange={(e) => setWeightKg(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="78.5"
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.92rem", color: "#0f172a" }}
                  required
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Required for creatinine clearance calculations</span>
              </div>
            </div>
          </div>

          {/* Card 2: Laboratory Results */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", borderBottom: "2px solid #0d9488", paddingBottom: "0.5rem", flexWrap: "wrap", gap: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.2rem" }}>🧪</span>
                <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#0f2744", margin: 0 }}>
                  2. Pre-Decision Laboratory Results
                </h2>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <label style={{ fontSize: "0.8rem", color: "#475569", fontWeight: 600 }}>Panel Measurement Timestamp:</label>
                <input
                  type="datetime-local"
                  value={labTimestamp}
                  onChange={(e) => setLabTimestamp(e.target.value)}
                  style={{ padding: "0.35rem 0.55rem", borderRadius: "4px", border: "1px solid #cbd5e1", fontSize: "0.82rem", color: "#0f172a" }}
                />
              </div>
            </div>

            <p style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "-0.5rem", marginBottom: "1.25rem" }}>
              All 5 pre-decision values are evaluated against clinical safety thresholds and feed the 6-feature Random Forest inference engine.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
              {/* Blood Glucose */}
              <div style={{ background: "#f8fafc", padding: "0.85rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f2744" }}>
                    Blood Glucose <span style={{ color: "#dc2626" }}>*</span>
                  </label>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>mg/dL</span>
                </div>
                <input
                  type="number"
                  step="any"
                  value={glucose}
                  onChange={(e) => setGlucose(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="185"
                  style={{ width: "100%", padding: "0.55rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.95rem", fontWeight: 600, color: "#0f172a" }}
                  required
                />
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: "4px" }}>
                  Ref: 70–140 | &lt;70 triggers safety stop
                </div>
              </div>

              {/* Serum Creatinine */}
              <div style={{ background: "#f8fafc", padding: "0.85rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f2744" }}>
                    Serum Creatinine <span style={{ color: "#dc2626" }}>*</span>
                  </label>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>mg/dL</span>
                </div>
                <input
                  type="number"
                  step="0.01"
                  value={creatinine}
                  onChange={(e) => setCreatinine(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="1.1"
                  style={{ width: "100%", padding: "0.55rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.95rem", fontWeight: 600, color: "#0f172a" }}
                  required
                />
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: "4px" }}>
                  Ref: 0.7–1.3 | Evaluates renal clearance
                </div>
              </div>

              {/* Serum Potassium */}
              <div style={{ background: "#f8fafc", padding: "0.85rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f2744" }}>
                    Potassium (K⁺) <span style={{ color: "#dc2626" }}>*</span>
                  </label>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>mEq/L</span>
                </div>
                <input
                  type="number"
                  step="0.1"
                  value={potassium}
                  onChange={(e) => setPotassium(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="4.3"
                  style={{ width: "100%", padding: "0.55rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.95rem", fontWeight: 600, color: "#0f172a" }}
                  required
                />
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: "4px" }}>
                  Ref: 3.5–5.0 | &gt;5.5 stops ACEi/ARBs
                </div>
              </div>

              {/* Serum Sodium */}
              <div style={{ background: "#f8fafc", padding: "0.85rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f2744" }}>
                    Sodium (Na⁺) <span style={{ color: "#dc2626" }}>*</span>
                  </label>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>mEq/L</span>
                </div>
                <input
                  type="number"
                  step="any"
                  value={sodium}
                  onChange={(e) => setSodium(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="139"
                  style={{ width: "100%", padding: "0.55rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.95rem", fontWeight: 600, color: "#0f172a" }}
                  required
                />
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: "4px" }}>
                  Ref: 135–145 | Osmolar & fluid balance
                </div>
              </div>

              {/* Blood Urea Nitrogen */}
              <div style={{ background: "#f8fafc", padding: "0.85rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f2744" }}>
                    BUN (Urea Nitrogen) <span style={{ color: "#dc2626" }}>*</span>
                  </label>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>mg/dL</span>
                </div>
                <input
                  type="number"
                  step="any"
                  value={bun}
                  onChange={(e) => setBun(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="18"
                  style={{ width: "100%", padding: "0.55rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.95rem", fontWeight: 600, color: "#0f172a" }}
                  required
                />
                <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: "4px" }}>
                  Ref: 7–20 | Azotemia & hydration
                </div>
              </div>
            </div>
          </div>

          {/* Card 3: Optional Clinical Context */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "1.25rem", borderBottom: "2px solid #0d9488", paddingBottom: "0.5rem" }}>
              <span style={{ fontSize: "1.2rem" }}>📋</span>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#0f2744", margin: 0 }}>
                3. Optional Clinical Context
              </h2>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Current Medications <span style={{ color: "#94a3b8", fontWeight: 400 }}>(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={medicationsText}
                  onChange={(e) => setMedicationsText(e.target.value)}
                  placeholder="e.g. Atorvastatin 20mg, Amlodipine 5mg"
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.9rem" }}
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Evaluated against drug-drug interaction safety rules</span>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Relevant Allergies <span style={{ color: "#94a3b8", fontWeight: 400 }}>(comma-separated)</span>
                </label>
                <input
                  type="text"
                  value={allergiesText}
                  onChange={(e) => setAllergiesText(e.target.value)}
                  placeholder="e.g. Penicillin, Sulfa, ACE-inhibitors"
                  style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.9rem" }}
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Screened against contraindications</span>
              </div>
            </div>

            <div style={{ marginTop: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                Additional Clinical Notes / Comorbidities <span style={{ color: "#94a3b8", fontWeight: 400 }}>(optional)</span>
              </label>
              <input
                type="text"
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                placeholder="e.g. History of chronic kidney disease; patient denies chest pain or dyspnea."
                style={{ width: "100%", padding: "0.6rem 0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.9rem" }}
              />
            </div>
          </div>

          {/* Prominent Submission Button (Prompt Section 3) */}
          <div style={{ textAlign: "center", marginTop: "0.5rem" }}>
            <button
              type="submit"
              style={{
                backgroundColor: "#0d9488",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "0.95rem 2.5rem",
                fontSize: "1.1rem",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 4px 6px -1px rgba(13, 148, 136, 0.3)",
                transition: "all 0.15s ease-in-out",
                display: "inline-flex",
                alignItems: "center",
                gap: "10px"
              }}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#0f766e")}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#0d9488")}
            >
              <span>⚡</span>
              <span>Analyze Medicine & Dosage</span>
            </button>
            <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.5rem" }}>
              Executes 6-feature Random Forest inference, TreeSHAP explanation, and independent clinical safety checks.
            </div>
          </div>
        </form>
      )}

      {/* =========================================================================
          VIEW 2: LOADING PROGRESS SCREEN (Prompt Section 4)
          ========================================================================= */}
      {viewState === "loading" && (
        <div style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0", padding: "4rem 2rem", textAlign: "center", boxShadow: "0 4px 6px rgba(0,0,0,0.05)", maxWidth: "600px", margin: "2rem auto" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem", animation: "spin 2s linear infinite" }}>⏳</div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, color: "#0f2744", marginBottom: "0.5rem" }}>
            Processing Clinical Assessment
          </h2>
          <p style={{ fontSize: "1.05rem", color: "#0d9488", fontWeight: 600, minHeight: "1.8rem" }}>
            “{loadingMessage}”
          </p>
          <div style={{ width: "100%", height: "6px", backgroundColor: "#f1f5f9", borderRadius: "3px", overflow: "hidden", marginTop: "1.5rem" }}>
            <div style={{ width: "70%", height: "100%", backgroundColor: "#0d9488", borderRadius: "3px", animation: "pulse 1.5s ease-in-out infinite" }} />
          </div>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", display: "block", marginTop: "0.75rem" }}>
            MIMIC-IV Multi-Target Decision Engine • Independent Safety Gates
          </span>
        </div>
      )}

      {/* =========================================================================
          VIEW 3: RESULTS SCREEN (Strictly follows Prompt Section 5)
          ========================================================================= */}
      {viewState === "result" && result && (
        <div id="clinical-assessment-result" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          
          {/* Action Header Bar (Prompt Section 5.F) */}
          <div className="no-print" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#f8fafc", padding: "0.75rem 1rem", borderRadius: "8px", border: "1px solid #e2e8f0", flexWrap: "wrap", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "0.85rem", color: "#475569" }}>Patient: <strong>{patientId}</strong></span>
              <span style={{ color: "#cbd5e1" }}>|</span>
              <span style={{ fontSize: "0.85rem", color: "#475569" }}>Age: <strong>{age} yrs</strong> ({gender})</span>
              <span style={{ color: "#cbd5e1" }}>|</span>
              <span style={{ fontSize: "0.85rem", color: "#475569" }}>Indication: <strong>{result.diagnosis_name}</strong></span>
            </div>

            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={handleEditPatient}
                style={{ padding: "0.45rem 0.85rem", borderRadius: "6px", border: "1px solid #cbd5e1", background: "#ffffff", color: "#0f2744", fontSize: "0.82rem", fontWeight: 600, cursor: "pointer" }}
              >
                ✏️ Edit Patient Information
              </button>
              <button
                type="button"
                onClick={handleNewAssessment}
                style={{ padding: "0.45rem 0.85rem", borderRadius: "6px", border: "1px solid #0d9488", background: "#f0fdfa", color: "#0d9488", fontSize: "0.82rem", fontWeight: 600, cursor: "pointer" }}
              >
                ➕ New Assessment
              </button>
              <button
                type="button"
                onClick={() => setShowEvidenceModal(true)}
                style={{ padding: "0.45rem 0.85rem", borderRadius: "6px", border: "1px solid #cbd5e1", background: "#ffffff", color: "#0f2744", fontSize: "0.82rem", fontWeight: 600, cursor: "pointer" }}
              >
                📚 View Supporting Evidence
              </button>
              <button
                type="button"
                onClick={handlePrint}
                style={{ padding: "0.45rem 0.85rem", borderRadius: "6px", border: "1px solid #0f2744", background: "#0f2744", color: "#ffffff", fontSize: "0.82rem", fontWeight: 600, cursor: "pointer" }}
              >
                🖨️ Print Assessment Summary
              </button>
            </div>
          </div>

          {/* Section A: Assessment Status (Prompt Section 5.A) */}
          {(() => {
            const statusInfo = getStatusDisplay();
            return (
              <div
                style={{
                  background: statusInfo.bg,
                  border: `1px solid ${statusInfo.border || "#cbd5e1"}`,
                  borderRadius: "10px",
                  padding: "1.25rem 1.5rem",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "14px"
                }}
              >
                <span style={{ fontSize: "1.8rem", lineHeight: 1 }}>{statusInfo.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "0.3rem" }}>
                    <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 800, color: statusInfo.badgeColor }}>
                      {statusInfo.label}
                    </h2>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "0.2rem 0.5rem", borderRadius: "4px", backgroundColor: "#ffffff", color: statusInfo.badgeColor, border: `1px solid ${statusInfo.border}` }}>
                      {result.status}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: "0.92rem", color: "#1e293b", lineHeight: 1.5 }}>
                    {result.clinical_explanation}
                  </p>

                  {/* Missing information alert if present */}
                  {result.missing_information && result.missing_information.length > 0 && (
                    <div style={{ marginTop: "0.75rem", padding: "0.6rem 0.85rem", background: "#fffbeb", borderRadius: "6px", border: "1px solid #fde68a" }}>
                      <strong style={{ fontSize: "0.82rem", color: "#b45309" }}>Missing Clinical Information:</strong>
                      <ul style={{ margin: "0.25rem 0 0 1.25rem", fontSize: "0.8rem", color: "#92400e" }}>
                        {result.missing_information.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* Section B & C: Medicine Options & Dosage Information (Prompt Section 5.B & 5.C) */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "1rem", borderBottom: "2px solid #0d9488", paddingBottom: "0.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.2rem" }}>💊</span>
                <h3 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700, color: "#0f2744" }}>
                  Medicine Options & Specific Dosage Information
                </h3>
              </div>
              <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
                Screened against Clinical Guidelines & MIMIC-IV Benchmarks
              </span>
            </div>

            {/* Crucial Clinical Notice */}
            <div style={{ background: "#f8fafc", borderLeft: "4px solid #0d9488", padding: "0.6rem 0.85rem", borderRadius: "4px", fontSize: "0.8rem", color: "#334155", marginBottom: "1.25rem" }}>
              <strong>Notice for Prescribing Clinician:</strong> Model-generated options are clinical decision-support candidates. They do not constitute autonomous or pre-approved prescriptions. Final prescribing decisions remain the sole responsibility of the qualified treating clinician.
            </div>

            {result.proposals && result.proposals.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {result.proposals.map((proposal, idx) => {
                  const isAuth = proposal.dose_status === "AUTHORIZED";

                  return (
                    <div
                      key={idx}
                      style={{
                        borderRadius: "8px",
                        border: `1px solid ${isAuth ? "#bbf7d0" : "#fecaca"}`,
                        background: isAuth ? "#f0fdf4" : "#fff5f5",
                        padding: "1.25rem"
                      }}
                    >
                      {/* Top Row: Medicine Name, Candidate Score, Status Badge */}
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "8px" }}>
                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "#0f2744" }}>
                              {proposal.generic_name}
                            </span>
                            {proposal.candidate_medicine !== proposal.generic_name && (
                              <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                                ({proposal.candidate_medicine})
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: "0.8rem", color: "#475569", marginTop: "2px" }}>
                            Indication: <strong>{result.diagnosis_name}</strong>
                            {proposal.suggested_brand && (
                              <span style={{ marginLeft: "8px", color: "#0d9488", fontWeight: 600 }}>
                                • CDSCO Formulations: {proposal.suggested_brand}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Model Candidate Score & Dose Status */}
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span
                            style={{
                              background: "#e2e8f0",
                              color: "#1e293b",
                              padding: "0.25rem 0.6rem",
                              borderRadius: "4px",
                              fontSize: "0.75rem",
                              fontWeight: 700
                            }}
                          >
                            Model Selection Score: {proposal.model_confidence ? `${Math.round(proposal.model_confidence * 100)}%` : "Guideline-Ranked"}
                          </span>

                          <span
                            style={{
                              background: isAuth ? "#dcfce7" : "#fee2e2",
                              color: isAuth ? "#166534" : "#991b1b",
                              padding: "0.25rem 0.6rem",
                              borderRadius: "4px",
                              fontSize: "0.75rem",
                              fontWeight: 800,
                              border: `1px solid ${isAuth ? "#86efac" : "#fca5a5"}`
                            }}
                          >
                            {isAuth ? "DOSAGE AUTHORIZED" : "DOSE WITHHELD BY SAFETY"}
                          </span>
                        </div>
                      </div>

                      {/* Dosage Details Box (Section 5.C) */}
                      <div
                        style={{
                          marginTop: "0.85rem",
                          padding: "0.85rem",
                          borderRadius: "6px",
                          background: "#ffffff",
                          border: "1px solid #e2e8f0",
                          display: "grid",
                          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                          gap: "0.75rem"
                        }}
                      >
                        {/* Dose Value */}
                        <div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
                            Calculated Dose
                          </div>
                          {isAuth && proposal.dose_display ? (
                            <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#0d9488" }}>
                              {proposal.dose_display}{" "}
                              <span style={{ fontSize: "0.9rem", fontWeight: 600, color: "#334155" }}>
                                {proposal.unit || "mg"}
                              </span>
                            </div>
                          ) : (
                            <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#b91c1c" }}>
                              ⛔ Dose Withheld
                            </div>
                          )}
                        </div>

                        {/* Route & Frequency */}
                        <div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
                            Route / Schedule
                          </div>
                          <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "#0f2744" }}>
                            {proposal.route || "Oral (PO)"} • {proposal.frequency || "Once or twice daily"}
                          </div>
                        </div>

                        {/* Renal Clearance Adjustment */}
                        <div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
                            Renal Adjustment
                          </div>
                          <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#334155" }}>
                            {isAuth ? "Dose cleared for eGFR profile" : "Contraindicated by renal/lab limits"}
                          </div>
                        </div>

                        {/* Source of Dosing Information */}
                        <div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
                            Dosing Provenance
                          </div>
                          <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#475569" }}>
                            {proposal.provenance ? proposal.provenance.replace(/_/g, " ") : "MIMIC-IV Regressor & Guidelines"}
                          </div>
                        </div>
                      </div>

                      {/* Rationale and candidate explanation */}
                      <div style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "#334155", lineHeight: 1.4 }}>
                        <strong>Candidate Rationale:</strong> {proposal.why_candidate || proposal.rationale}
                      </div>

                      {/* Instructions if available */}
                      {proposal.instructions && (
                        <div style={{ marginTop: "0.4rem", fontSize: "0.8rem", color: "#0f766e" }}>
                          ⏱️ <strong>Administration Guidance:</strong> {proposal.instructions}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ padding: "2rem", textAlign: "center", color: "#64748b" }}>
                No candidate medicines eligible under current patient laboratory parameters.
              </div>
            )}
          </div>

          {/* Section D: Clinical Safety Engine Results (Prompt Section 5.D) */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #0d9488", paddingBottom: "0.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.2rem" }}>🛡️</span>
                <h3 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700, color: "#0f2744" }}>
                  Clinical Safety Engine Evaluations ({result.safety_checks.length} Rules Executed)
                </h3>
              </div>
              <span style={{ fontSize: "0.75rem", color: "#0d9488", fontWeight: 700 }}>
                Independent Clinical Overrides
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "0.6rem" }}>
              {result.safety_checks.map((chk, idx) => {
                const isPass = chk.status === "PASS";
                const isFail = chk.status === "FAIL";

                return (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "0.75rem 1rem",
                      borderRadius: "6px",
                      background: isPass ? "#f8fafc" : isFail ? "#fef2f2" : "#fffbeb",
                      border: `1px solid ${isPass ? "#e2e8f0" : isFail ? "#fca5a5" : "#fde68a"}`
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "#0f2744" }}>
                        {chk.check_name}
                      </div>
                      <div style={{ fontSize: "0.82rem", color: isPass ? "#475569" : "#991b1b", marginTop: "2px" }}>
                        {chk.findings}
                      </div>
                      {chk.source_reference && (
                        <div style={{ fontSize: "0.72rem", color: "#0d9488", marginTop: "2px", fontWeight: 600 }}>
                          Clinical Rule Source: {chk.source_reference}
                        </div>
                      )}
                    </div>

                    <span
                      style={{
                        padding: "0.25rem 0.6rem",
                        borderRadius: "4px",
                        fontSize: "0.75rem",
                        fontWeight: 800,
                        backgroundColor: isPass ? "#dcfce7" : isFail ? "#fee2e2" : "#fef3c7",
                        color: isPass ? "#166534" : isFail ? "#991b1b" : "#92400e"
                      }}
                    >
                      {chk.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section E: Collapsible Explanation (Prompt Section 5.E) */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
            <div
              onClick={() => setExplanationOpen((prev) => !prev)}
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer", borderBottom: explanationOpen ? "2px solid #0d9488" : "none", paddingBottom: explanationOpen ? "0.5rem" : 0 }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "1.2rem" }}>🔬</span>
                <h3 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700, color: "#0f2744" }}>
                  Why was this result produced?
                </h3>
              </div>
              <span style={{ fontSize: "0.9rem", color: "#64748b", fontWeight: 600 }}>
                {explanationOpen ? "Hide Explanation ▲" : "Show Explanation ▼"}
              </span>
            </div>

            {explanationOpen && (
              <div style={{ marginTop: "1rem" }}>
                {/* 1. Important Input Features Table */}
                <div style={{ marginBottom: "1.25rem" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", fontWeight: 700, color: "#334155" }}>
                    Clinical Input Parameters Evaluated:
                  </h4>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "0.5rem" }}>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Age</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{age} yrs</div>
                    </div>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Blood Glucose</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{glucose} mg/dL</div>
                    </div>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Creatinine</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{creatinine} mg/dL</div>
                    </div>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Potassium (K⁺)</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{potassium} mEq/L</div>
                    </div>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>Sodium (Na⁺)</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{sodium} mEq/L</div>
                    </div>
                    <div style={{ background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                      <div style={{ fontSize: "0.72rem", color: "#64748b" }}>BUN</div>
                      <div style={{ fontWeight: 700, color: "#0f2744", fontSize: "0.95rem" }}>{bun} mg/dL</div>
                    </div>
                  </div>
                </div>

                {/* 2. SHAP Feature Contributions */}
                {result.proposals && result.proposals[0]?.shap_contributions && (
                  <div style={{ marginBottom: "1.25rem" }}>
                    <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", fontWeight: 700, color: "#334155" }}>
                      TreeSHAP Statistical Feature Attributions (Impact on Dosage Output):
                    </h4>
                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                      {Object.entries(result.proposals[0].shap_contributions).map(([feature, value]) => {
                        const numVal = Number(value);
                        const isPos = numVal >= 0;
                        return (
                          <div
                            key={feature}
                            style={{
                              padding: "0.35rem 0.65rem",
                              borderRadius: "6px",
                              backgroundColor: isPos ? "#ecfdf5" : "#fef2f2",
                              border: `1px solid ${isPos ? "#a7f3d0" : "#fecaca"}`,
                              color: isPos ? "#065f46" : "#991b1b",
                              fontSize: "0.8rem",
                              fontWeight: 600
                            }}
                          >
                            <span>{feature.replace("pre_", "").toUpperCase()}: </span>
                            <span>{isPos ? `+${numVal.toFixed(2)}` : numVal.toFixed(2)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 3. Mandatory Model Limitations & Non-Causation Notice (Section 5.E) */}
                <div style={{ background: "#fffbeb", border: "1px solid #fde68a", borderRadius: "6px", padding: "0.85rem", fontSize: "0.82rem", color: "#92400e", lineHeight: 1.45 }}>
                  <strong>Model Limitations & Scientific Attribution Notice:</strong> TreeSHAP feature attributions describe how individual patient input features statistically influenced the machine learning model’s mathematical output relative to the training cohort baseline. <em>SHAP does not prove biological or clinical causation.</em> Prescribing decisions must be based on comprehensive clinical judgment by a qualified clinician.
                </div>
              </div>
            )}
          </div>

          {/* Section F: Final Actions Footer (Prompt Section 5.F) */}
          <div className="no-print" style={{ display: "flex", justifyContent: "center", gap: "12px", marginTop: "0.5rem", flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={handleEditPatient}
              style={{
                backgroundColor: "#ffffff",
                color: "#0f2744",
                border: "1px solid #cbd5e1",
                borderRadius: "8px",
                padding: "0.75rem 1.5rem",
                fontSize: "0.95rem",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              ✏️ Edit Patient Information
            </button>
            <button
              type="button"
              onClick={handleNewAssessment}
              style={{
                backgroundColor: "#0d9488",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "0.75rem 1.75rem",
                fontSize: "0.95rem",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              ➕ Start New Assessment
            </button>
            <button
              type="button"
              onClick={handlePrint}
              style={{
                backgroundColor: "#0f2744",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "0.75rem 1.5rem",
                fontSize: "0.95rem",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              🖨️ Print Assessment Summary
            </button>
          </div>
        </div>
      )}

      {/* Supporting Evidence Modal (Section 5.F) */}
      {showEvidenceModal && result && (
        <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(15, 23, 42, 0.6)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 100, padding: "1rem" }}>
          <div style={{ background: "#ffffff", borderRadius: "12px", maxWidth: "700px", width: "100%", maxHeight: "85vh", overflowY: "auto", padding: "1.75rem", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.75rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#0f2744" }}>
                📚 Verified Clinical Practice Guidelines & Sources
              </h3>
              <button
                type="button"
                onClick={() => setShowEvidenceModal(false)}
                style={{ background: "none", border: "none", fontSize: "1.3rem", cursor: "pointer", color: "#64748b" }}
              >
                ✕
              </button>
            </div>

            {result.sources && result.sources.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {result.sources.map((src, i) => (
                  <div key={i} style={{ padding: "1rem", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                    <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#0f2744" }}>{src.title}</div>
                    <div style={{ fontSize: "0.82rem", color: "#475569", marginTop: "4px" }}>{src.citation}</div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>
                      Organization: <strong>{src.organization}</strong> • Publication Year: <strong>{src.publication_year}</strong>
                    </div>
                    {src.url && (
                      <div style={{ marginTop: "8px" }}>
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: "#0d9488", fontSize: "0.8rem", fontWeight: 700, textDecoration: "none" }}
                        >
                          🔗 Open Guideline Document →
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: "#64748b", fontSize: "0.9rem" }}>
                No external guideline links returned for this specific case. Standard MIMIC-IV clinical references applied.
              </p>
            )}

            <div style={{ marginTop: "1.5rem", textAlign: "right" }}>
              <button
                type="button"
                onClick={() => setShowEvidenceModal(false)}
                style={{ padding: "0.55rem 1.25rem", borderRadius: "6px", background: "#0d9488", color: "#ffffff", border: "none", fontWeight: 700, cursor: "pointer" }}
              >
                Close Evidence Modal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Print-specific stylesheet */}
      <style>{`
        @media print {
          body {
            background: #ffffff !important;
            color: #000000 !important;
          }
          .no-print, header button, .vignettes-section {
            display: none !important;
          }
          #clinical-assessment-result {
            box-shadow: none !important;
            border: none !important;
          }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scaleX(0.95); }
          50% { opacity: 0.7; transform: scaleX(1); }
        }
      `}</style>
    </div>
  );
};

export default SimpleInputOutputPage;
