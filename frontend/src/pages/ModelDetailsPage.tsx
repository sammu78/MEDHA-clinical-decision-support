import React, { useState, useEffect } from "react";
import { fetchModelEvaluationInfo } from "../services/api";

export const ModelDetailsPage: React.FC = () => {
  const [modelMetrics, setModelMetrics] = useState<any>(null);

  useEffect(() => {
    fetchModelEvaluationInfo("type_2_diabetes")
      .then((data) => {
        setModelMetrics(data.metrics);
      })
      .catch((err) => {
        console.error("Failed to load model info:", err);
      });
  }, []);

  return (
    <div className="clinical-card">
      <div className="card-title">
        <span>🔬</span> Model Architecture, Training & Clinical Feasibility Benchmarks
      </div>
      <div className="card-subtitle">
        Transparent technical documentation of retrospective MIMIC-IV demo models, patient-level splits, baseline comparisons, and methodological boundaries.
      </div>

      {/* Cohort Overview Card */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ padding: "1rem", backgroundColor: "var(--bg-subtle)", borderRadius: 8, border: "1px solid var(--border-light)" }}>
          <div className="field-label">Training Data Source</div>
          <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--text-primary)" }}>MIMIC-IV Demo v2.2</div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Beth Israel Deaconess Medical Center</div>
        </div>

        <div style={{ padding: "1rem", backgroundColor: "var(--bg-subtle)", borderRadius: 8, border: "1px solid var(--border-light)" }}>
          <div className="field-label">Total Treatment Decisions</div>
          <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--teal-dark)" }}>2,010 Records</div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Across 76 unique patients</div>
        </div>

        <div style={{ padding: "1rem", backgroundColor: "var(--bg-subtle)", borderRadius: 8, border: "1px solid var(--border-light)" }}>
          <div className="field-label">Train / Test Split Strategy</div>
          <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--text-primary)" }}>GroupShuffleSplit</div>
          <div style={{ fontSize: "0.75rem", color: "#166534", fontWeight: 600 }}>Zero patient overlap (leak-free)</div>
        </div>

        <div style={{ padding: "1rem", backgroundColor: "var(--bg-subtle)", borderRadius: 8, border: "1px solid var(--border-light)" }}>
          <div className="field-label">Clinical Safety Gating</div>
          <div style={{ fontSize: "1.125rem", fontWeight: 700, color: "#15803d" }}>Active & Enforced</div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Overrides unvalidated ML outputs</div>
        </div>
      </div>

      {/* Task 1: Medicine Selection Classification */}
      <div style={{ marginBottom: "2rem" }}>
        <h3 style={{ fontSize: "1.0625rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.5rem" }}>
          Task 1: Medicine Candidate Classification (Historical Selection)
        </h3>
        <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
          Predicts candidate medicine historically chosen given patient demographic attributes and pre-decision labs. Evaluated against a <strong>Most Frequent Baseline</strong>.
        </p>

        <table className="clinical-table">
          <thead>
            <tr>
              <th>Clinical Cohort</th>
              <th>Records (Train / Test)</th>
              <th>Candidate Classes</th>
              <th>Baseline Accuracy</th>
              <th>Model Accuracy (RF)</th>
              <th>Model F1-Score</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Type 2 Diabetes</strong></td>
              <td>1,095 (787 / 308)</td>
              <td>Insulin, Metformin, Glipizide</td>
              <td>75.5%</td>
              <td><strong style={{ color: "var(--teal-dark)" }}>75.5%</strong></td>
              <td>0.650</td>
            </tr>
            <tr>
              <td><strong>Essential Hypertension</strong></td>
              <td>528 (387 / 141)</td>
              <td>Metoprolol, Hydralazine, Lisinopril, Amlodipine</td>
              <td>27.8%</td>
              <td><strong style={{ color: "var(--teal-dark)" }}>31.2%</strong></td>
              <td>0.197</td>
            </tr>
            <tr>
              <td><strong>Congestive Heart Failure</strong></td>
              <td>387 (320 / 67)</td>
              <td>Furosemide, Spironolactone</td>
              <td>97.0%</td>
              <td><strong style={{ color: "var(--teal-dark)" }}>94.0%</strong></td>
              <td>0.940</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Task 2: Dose Regression */}
      <div style={{ marginBottom: "2rem" }}>
        <h3 style={{ fontSize: "1.0625rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.5rem" }}>
          Task 2: Dose Numeric Regression (Historical Inpatient Titration)
        </h3>
        <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
          Models prescribed numeric dose conditional on route, pre-decision labs, and age. Evaluated against a <strong>Median Baseline Regressor</strong>.
        </p>

        <table className="clinical-table">
          <thead>
            <tr>
              <th>Target Medicine & Route</th>
              <th>Dose Unit</th>
              <th>Orders / Patients</th>
              <th>Baseline Median MAE</th>
              <th>Random Forest Regressor MAE</th>
              <th>Interpretability</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Insulin (Subcutaneous)</strong></td>
              <td>UNIT</td>
              <td>840 orders / 32 patients</td>
              <td>12.58 UNIT</td>
              <td><strong>14.12 UNIT</strong></td>
              <td>SHAP Tree Explainer</td>
            </tr>
            <tr>
              <td><strong>Metoprolol Tartrate (Oral / PO)</strong></td>
              <td>mg</td>
              <td>146 orders / 34 patients</td>
              <td>30.51 mg</td>
              <td><strong>33.17 mg</strong></td>
              <td>SHAP Tree Explainer</td>
            </tr>
            <tr>
              <td><strong>Furosemide (IV Injection)</strong></td>
              <td>mg</td>
              <td>239 orders / 28 patients</td>
              <td>80.48 mg</td>
              <td><strong style={{ color: "#15803d" }}>67.17 mg</strong> (-13.3 mg improvement)</td>
              <td>SHAP Tree Explainer</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Critical Scientific & Methodological Limitations */}
      <div style={{ backgroundColor: "#f8fafc", border: "1px solid var(--border-light)", borderRadius: 8, padding: "1.25rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#0f2744", marginBottom: "0.5rem" }}>
          ⚠️ Critical Methodological Limitations & Safety Boundaries
        </h3>
        <ul style={{ marginLeft: "1.25rem", color: "var(--text-secondary)", fontSize: "0.875rem", lineHeight: 1.6 }}>
          <li>
            <strong>Retrospective Demo Constraint:</strong> The MIMIC-IV demo contains only 100 subject profiles. While inpatient orders are plentiful (18,087 orders), the unique patient population is small (76 patients in target cohorts). ML models trained on this sample are research demonstrations, not clinical generalizers.
          </li>
          <li>
            <strong>Billing Diagnosis Timing:</strong> ICD codes in EHR data reflect discharge summary billing, not real-time clinician suspicion at 2 AM when medication orders are signed.
          </li>
          <li>
            <strong>Inpatient vs Outpatient Practice:</strong> Hospitalized diabetic patients frequently receive subcutaneous sliding-scale insulin rather than outpatient metformin due to fasting procedures and imaging contrast concerns.
          </li>
          <li>
            <strong>No Clinical Claim:</strong> This application is not a medical device. Dosing displays are strictly gated by peer-reviewed guidelines and require physician validation.
          </li>
        </ul>
      </div>

      {/* Live Backend Metrics Inspector */}
      {modelMetrics && (
        <details style={{ marginTop: "1.5rem", padding: "1rem", backgroundColor: "#ffffff", border: "1px solid var(--border-light)", borderRadius: 8 }}>
          <summary style={{ cursor: "pointer", fontWeight: 600, color: "var(--teal-dark)", fontSize: "0.875rem" }}>
            🔍 View Raw Live Model Metrics Payload (FastAPI: /model-info/type_2_diabetes)
          </summary>
          <pre style={{ marginTop: "0.75rem", padding: "0.75rem", backgroundColor: "var(--bg-subtle)", borderRadius: 6, fontSize: "0.75rem", overflowX: "auto", color: "var(--text-secondary)" }}>
            {JSON.stringify(modelMetrics, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
};
