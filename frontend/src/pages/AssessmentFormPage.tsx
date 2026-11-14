import React, { useState, useEffect } from "react";
import type { PatientAssessmentRequest, SupportedCase } from "../types";

interface AssessmentFormPageProps {
  initialData: PatientAssessmentRequest;
  supportedCases: SupportedCase[];
  onSubmit: (formData: PatientAssessmentRequest) => void;
  isLoading: boolean;
  errorMessage: string | null;
}

export const AssessmentFormPage: React.FC<AssessmentFormPageProps> = ({
  initialData,
  supportedCases,
  onSubmit,
  isLoading,
  errorMessage
}) => {
  const [formData, setFormData] = useState<PatientAssessmentRequest>(initialData);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  useEffect(() => {
    setFormData(initialData);
  }, [initialData]);

  const activeCase = supportedCases.find((c) => c.case_id === formData.diagnosis_id);

  const handleDiagnosisChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setFormData((prev) => ({
      ...prev,
      diagnosis_id: val
    }));
  };

  const handleNumberChange = (field: "age" | "weight_kg", val: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: val === "" ? (field === "age" ? 0 : undefined) : parseFloat(val)
    }));
  };

  const handleLabChange = (labKey: string, field: "value" | "unit" | "measurement_date", val: string) => {
    setFormData((prev) => {
      const currentLab = prev.labs[labKey] || {
        name: labKey.toUpperCase(),
        value: 0,
        unit: labKey === "potassium" || labKey === "sodium" ? "mEq/L" : labKey === "egfr" ? "mL/min" : labKey === "hba1c" ? "%" : "mg/dL",
        measurement_date: new Date().toISOString().split("T")[0]
      };

      const updated = {
        ...currentLab,
        [field]: field === "value" ? parseFloat(val) || 0 : val
      };

      return {
        ...prev,
        labs: {
          ...prev.labs,
          [labKey]: updated
        }
      };
    });
  };

  const handleRemoveLab = (labKey: string) => {
    setFormData((prev) => {
      const copy = { ...prev.labs };
      delete copy[labKey];
      return { ...prev, labs: copy };
    });
  };

  const loadCaseStudy = (caseType: string) => {
    const today = new Date().toISOString().split("T")[0];
    if (caseType === "t2d_hyperglycemia") {
      setFormData({
        diagnosis_id: "type_2_diabetes",
        age: 58,
        weight_kg: 84.5,
        gender: "M",
        allergies: [],
        current_medications: ["Atorvastatin 20mg PO daily"],
        existing_conditions: ["Hyperlipidemia", "Chronic Hypertension"],
        labs: {
          glucose: { name: "Blood Glucose", value: 215, unit: "mg/dL", measurement_date: today },
          creatinine: { name: "Serum Creatinine", value: 1.0, unit: "mg/dL", measurement_date: today },
          potassium: { name: "Serum Potassium", value: 4.2, unit: "mEq/L", measurement_date: today },
          bun: { name: "Blood Urea Nitrogen", value: 18, unit: "mg/dL", measurement_date: today }
        }
      });
    } else if (caseType === "t2d_hypoglycemia_stop") {
      setFormData({
        diagnosis_id: "type_2_diabetes",
        age: 64,
        weight_kg: 76.0,
        gender: "F",
        allergies: [],
        current_medications: ["Glipizide 5mg PO"],
        existing_conditions: ["Type 2 Diabetes"],
        labs: {
          glucose: { name: "Blood Glucose", value: 52, unit: "mg/dL", measurement_date: today },
          creatinine: { name: "Serum Creatinine", value: 0.9, unit: "mg/dL", measurement_date: today }
        }
      });
    } else if (caseType === "t2d_severe_ckd") {
      setFormData({
        diagnosis_id: "type_2_diabetes",
        age: 72,
        weight_kg: 68.0,
        gender: "M",
        allergies: [],
        current_medications: ["Aspirin 81mg PO"],
        existing_conditions: ["Chronic Kidney Disease Stage 4"],
        labs: {
          glucose: { name: "Blood Glucose", value: 198, unit: "mg/dL", measurement_date: today },
          creatinine: { name: "Serum Creatinine", value: 2.8, unit: "mg/dL", measurement_date: today },
          egfr: { name: "Estimated GFR", value: 22.0, unit: "mL/min", measurement_date: today }
        }
      });
    } else if (caseType === "htn_first_line") {
      setFormData({
        diagnosis_id: "essential_hypertension",
        age: 62,
        weight_kg: 79.0,
        gender: "M",
        allergies: [],
        current_medications: [],
        existing_conditions: ["Essential Hypertension"],
        labs: {
          creatinine: { name: "Serum Creatinine", value: 1.1, unit: "mg/dL", measurement_date: today },
          potassium: { name: "Serum Potassium", value: 4.3, unit: "mEq/L", measurement_date: today }
        }
      });
    } else if (caseType === "htn_hyperkalemia_stop") {
      setFormData({
        diagnosis_id: "essential_hypertension",
        age: 67,
        weight_kg: 72.0,
        gender: "F",
        allergies: [],
        current_medications: ["Spironolactone 25mg PO"],
        existing_conditions: ["Hypertension", "Mild Renal Impairment"],
        labs: {
          creatinine: { name: "Serum Creatinine", value: 1.4, unit: "mg/dL", measurement_date: today },
          potassium: { name: "Serum Potassium", value: 5.7, unit: "mEq/L", measurement_date: today }
        }
      });
    } else if (caseType === "hf_loop_diuretic") {
      setFormData({
        diagnosis_id: "heart_failure",
        age: 69,
        weight_kg: 88.0,
        gender: "M",
        allergies: [],
        current_medications: ["Metoprolol Succinate 50mg PO"],
        existing_conditions: ["Congestive Heart Failure", "Volume Overload"],
        labs: {
          creatinine: { name: "Serum Creatinine", value: 1.2, unit: "mg/dL", measurement_date: today },
          potassium: { name: "Serum Potassium", value: 4.1, unit: "mEq/L", measurement_date: today },
          sodium: { name: "Serum Sodium", value: 138, unit: "mEq/L", measurement_date: today }
        }
      });
    } else if (caseType === "missing_labs_demo") {
      setFormData({
        diagnosis_id: "type_2_diabetes",
        age: 55,
        weight_kg: 80.0,
        gender: "M",
        allergies: [],
        current_medications: [],
        existing_conditions: [],
        labs: {} // Omit required labs
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const errors: string[] = [];

    if (!formData.diagnosis_id) {
      errors.push("Please select a clinical diagnosis.");
    }
    if (!formData.age || formData.age <= 0 || formData.age > 125) {
      errors.push("Valid patient age (1–125 years) is required.");
    }
    if (formData.weight_kg !== undefined && (formData.weight_kg <= 2 || formData.weight_kg > 400)) {
      errors.push("Body weight must be between 2 and 400 kg if specified.");
    }

    setValidationErrors(errors);
    if (errors.length === 0) {
      onSubmit(formData);
    }
  };

  const getLabStatusBadge = (key: string, val: number) => {
    if (key === "glucose") {
      if (val < 70) return <span className="lab-status-badge critical">Critical Low (&lt;70)</span>;
      if (val > 180) return <span className="lab-status-badge abnormal">Elevated (&gt;180)</span>;
      return <span className="lab-status-badge normal">Normal Target</span>;
    }
    if (key === "creatinine") {
      if (val > 1.5) return <span className="lab-status-badge abnormal">High (&gt;1.5)</span>;
      return <span className="lab-status-badge normal">Normal Range</span>;
    }
    if (key === "potassium") {
      if (val < 3.5) return <span className="lab-status-badge critical">Hypokalemia (&lt;3.5)</span>;
      if (val > 5.2) return <span className="lab-status-badge critical">Hyperkalemia (&gt;5.2)</span>;
      return <span className="lab-status-badge normal">Optimal (3.5–5.0)</span>;
    }
    if (key === "egfr") {
      if (val < 30) return <span className="lab-status-badge critical">Stage 4/5 CKD (&lt;30)</span>;
      if (val < 60) return <span className="lab-status-badge abnormal">Reduced GFR (&lt;60)</span>;
      return <span className="lab-status-badge normal">Preserved GFR</span>;
    }
    return null;
  };

  return (
    <div>
      {/* Interactive Case Vignettes Banner */}
      <div className="vignettes-section">
        <div className="vignettes-header">
          <h3><span>🏥</span> Hospital Pre-Loaded Clinical Case Studies (Evaluator Demonstrations)</h3>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Click any case to populate chart</span>
        </div>

        <div className="vignette-cards-grid">
          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("t2d_hyperglycemia")}>
            <div className="vignette-card-title">1. T2D Hyperglycemia</div>
            <div className="vignette-card-tag">Eligible (Dose Auth)</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("t2d_hypoglycemia_stop")}>
            <div className="vignette-card-title">2. T2D Hypoglycemia</div>
            <div className="vignette-card-tag" style={{ color: "#dc2626" }}>Safety Stop (&lt;70 mg/dL)</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("t2d_severe_ckd")}>
            <div className="vignette-card-title">3. T2D Severe CKD</div>
            <div className="vignette-card-tag" style={{ color: "#d97706" }}>Metformin Withheld</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("htn_first_line")}>
            <div className="vignette-card-title">4. Primary HTN</div>
            <div className="vignette-card-tag">Standard First-Line</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("htn_hyperkalemia_stop")}>
            <div className="vignette-card-title">5. HTN + High K+ (5.7)</div>
            <div className="vignette-card-tag" style={{ color: "#dc2626" }}>Lisinopril Withheld</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("hf_loop_diuretic")}>
            <div className="vignette-card-title">6. Heart Failure Overload</div>
            <div className="vignette-card-tag">IV Furosemide Regimen</div>
          </button>

          <button type="button" className="vignette-card-btn" onClick={() => loadCaseStudy("missing_labs_demo")}>
            <div className="vignette-card-title">7. Missing Required Labs</div>
            <div className="vignette-card-tag" style={{ color: "#b45309" }}>Dose Withheld</div>
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="result-hero CONTRAINDICATED">
          <div className="result-hero-icon">⛔</div>
          <div>
            <div className="result-hero-title">Evaluation Error</div>
            <div className="result-hero-desc">{errorMessage}</div>
          </div>
        </div>
      )}

      {validationErrors.length > 0 && (
        <div className="result-hero MORE_INFO_NEEDED">
          <div className="result-hero-icon">⚠️</div>
          <div>
            <div className="result-hero-title">Clinical Chart Incomplete</div>
            <ul style={{ marginLeft: "1.25rem", marginTop: "4px" }}>
              {validationErrors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Two-Column Clinical Chart Layout */}
        <div className="ehr-two-col">
          {/* Left Column: Indication, Demographics, Problem List */}
          <div>
            {/* Primary Indication Card */}
            <div className="ehr-card">
              <div className="ehr-card-header">
                <div className="ehr-card-title">
                  <span>🎯</span> Confirmed Clinical Indication
                </div>
                <span style={{ fontSize: "0.75rem", color: "var(--teal-dark)", fontWeight: 600 }}>Registry Gated</span>
              </div>

              <div className="field-group" style={{ marginBottom: "1rem" }}>
                <label className="field-label">
                  <span>Established Diagnosis</span>
                  <span style={{ color: "#dc2626", fontWeight: 700 }}>*</span>
                </label>
                <select
                  className="field-select"
                  style={{ fontSize: "0.95rem", fontWeight: 700 }}
                  value={formData.diagnosis_id}
                  onChange={handleDiagnosisChange}
                >
                  <option value="">-- Select Established Clinical Indication --</option>
                  {supportedCases.map((c) => (
                    <option key={c.case_id} value={c.case_id}>
                      {c.diagnosis_name} (ICD: {(c.icd_codes || c.icd_10_codes || []).join(", ")})
                    </option>
                  ))}
                  <option value="unsupported_asthma_acute">
                    Acute Bronchial Asthma Exacerbation [Negative Control - Unsupported]
                  </option>
                </select>
              </div>

              {activeCase && (
                <div style={{ backgroundColor: "var(--bg-subtle)", borderRadius: 6, padding: "0.75rem", fontSize: "0.8125rem", color: "var(--text-secondary)" }}>
                  <div><strong>Eligible Patient Group:</strong> {activeCase.eligible_patient_group}</div>
                  <div style={{ marginTop: "4px" }}>
                    <strong>Required Pre-Decision Labs:</strong>{" "}
                    <span style={{ color: "#b45309", fontWeight: 700 }}>
                      {activeCase.required_inputs.join(", ")}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Patient Demographics & Profile */}
            <div className="ehr-card">
              <div className="ehr-card-header">
                <div className="ehr-card-title">
                  <span>👤</span> Patient Demographics
                </div>
              </div>

              <div className="form-row">
                <div className="field-group">
                  <label className="field-label">
                    <span>Patient Age (Years) <span style={{ color: "#dc2626" }}>*</span></span>
                  </label>
                  <input
                    type="number"
                    className="field-input"
                    value={formData.age || ""}
                    onChange={(e) => handleNumberChange("age", e.target.value)}
                    placeholder="e.g. 58"
                    min="1"
                    max="125"
                    required
                  />
                </div>

                <div className="field-group">
                  <label className="field-label">
                    <span>Body Weight (kg)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="field-input"
                    value={formData.weight_kg || ""}
                    onChange={(e) => handleNumberChange("weight_kg", e.target.value)}
                    placeholder="e.g. 84.5"
                  />
                </div>

                <div className="field-group">
                  <label className="field-label">
                    <span>Biological Sex</span>
                  </label>
                  <select
                    className="field-select"
                    value={formData.gender || ""}
                    onChange={(e) => setFormData({ ...formData, gender: (e.target.value as any) || undefined })}
                  >
                    <option value="">Unspecified</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                  </select>
                </div>
              </div>

              <div className="field-group" style={{ marginBottom: "1rem" }}>
                <label className="field-label">
                  <span>Documented Drug Hypersensitivities / Allergies</span>
                </label>
                <input
                  type="text"
                  className="field-input"
                  value={formData.allergies.join(", ")}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      allergies: e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                    })
                  }
                  placeholder="e.g. ACE-inhibitors, Penicillin, Sulfa"
                />
              </div>

              <div className="field-group">
                <label className="field-label">
                  <span>Current Active Medications</span>
                </label>
                <input
                  type="text"
                  className="field-input"
                  value={formData.current_medications.join(", ")}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      current_medications: e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                    })
                  }
                  placeholder="e.g. Atorvastatin 20mg, Spironolactone 25mg"
                />
              </div>
            </div>
          </div>

          {/* Right Column: Pre-Decision Lab Flowsheet */}
          <div>
            <div className="ehr-card">
              <div className="ehr-card-header">
                <div>
                  <div className="ehr-card-title">
                    <span>🧪</span> Pre-Decision Laboratory Flowsheet
                  </div>
                  <div className="ehr-card-subtitle">
                    Recorded strictly prior to medication order timestamp (leakage-free).
                  </div>
                </div>
              </div>

              <table className="ehr-table">
                <thead>
                  <tr>
                    <th>Measurement</th>
                    <th>Result</th>
                    <th>Unit</th>
                    <th>Interpretation</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { key: "glucose", label: "Blood Glucose", defaultUnit: "mg/dL", normalRef: "70–140" },
                    { key: "creatinine", label: "Serum Creatinine", defaultUnit: "mg/dL", normalRef: "0.7–1.3" },
                    { key: "potassium", label: "Serum Potassium", defaultUnit: "mEq/L", normalRef: "3.5–5.0" },
                    { key: "sodium", label: "Serum Sodium", defaultUnit: "mEq/L", normalRef: "135–145" },
                    { key: "bun", label: "Blood Urea Nitrogen", defaultUnit: "mg/dL", normalRef: "7–20" },
                    { key: "egfr", label: "Estimated GFR", defaultUnit: "mL/min", normalRef: ">60" }
                  ].map((item) => {
                    const isPresent = Boolean(formData.labs[item.key]);
                    const lab = formData.labs[item.key];
                    const isRequired = activeCase?.required_inputs.includes(`labs.${item.key}`);

                    return (
                      <tr key={item.key} style={{ backgroundColor: isRequired && !isPresent ? "#fffbeb" : undefined }}>
                        <td>
                          <strong>{item.label}</strong>
                          {isRequired && (
                            <span style={{ color: "#dc2626", fontSize: "0.7rem", fontWeight: 700, marginLeft: "4px" }}>
                              *REQ
                            </span>
                          )}
                          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Ref: {item.normalRef}</div>
                        </td>
                        <td style={{ width: "110px" }}>
                          <input
                            type="number"
                            step="0.01"
                            className="field-input"
                            style={{ padding: "0.35rem 0.5rem", width: "100%", fontWeight: isPresent ? 700 : 400 }}
                            placeholder={isPresent ? String(lab.value) : "—"}
                            value={isPresent ? lab.value : ""}
                            onChange={(e) => handleLabChange(item.key, "value", e.target.value)}
                          />
                        </td>
                        <td style={{ width: "90px" }}>
                          <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                            {isPresent ? lab.unit : item.defaultUnit}
                          </span>
                        </td>
                        <td>
                          {isPresent && getLabStatusBadge(item.key, lab.value)}
                        </td>
                        <td>
                          {isPresent && (
                            <button
                              type="button"
                              onClick={() => handleRemoveLab(item.key)}
                              style={{ background: "none", border: "none", color: "#dc2626", cursor: "pointer", fontSize: "0.75rem", fontWeight: 700 }}
                            >
                              Clear
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Generate Action Button Card */}
            <div className="ehr-card" style={{ backgroundColor: "var(--bg-subtle)" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <button
                  type="submit"
                  className="clinical-btn-primary"
                  style={{ width: "100%", justifyContent: "center", padding: "0.875rem" }}
                  disabled={isLoading}
                >
                  {isLoading ? "Evaluating Clinical Safety Checks..." : "⚡ Execute Decision Support Assessment"}
                </button>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textAlign: "center" }}>
                  Clinical safety engine evaluates contraindications, eGFR bounds, and drug-drug interactions.
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
