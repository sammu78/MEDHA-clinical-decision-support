import React, { useState } from "react";
import type { SupportedCase } from "../types";

interface SupportedCasesPageProps {
  cases: SupportedCase[];
  onSelectCase: (caseId: string) => void;
}

export const SupportedCasesPage: React.FC<SupportedCasesPageProps> = ({
  cases,
  onSelectCase
}) => {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCases = cases.filter((c) => {
    const q = searchQuery.toLowerCase();
    const codes = c.icd_codes || c.icd_10_codes || [];
    return (
      c.diagnosis_name.toLowerCase().includes(q) ||
      codes.some((icd) => icd.toLowerCase().includes(q)) ||
      (c.candidate_medicines || []).some((med) => med.toLowerCase().includes(q))
    );
  });

  return (
    <div className="clinical-card">
      <div className="card-title">
        <span>📖</span> Verified Supported Clinical Case Registry
      </div>
      <div className="card-subtitle">
        Curated list of indications with verified clinical practice guidelines, validated laboratory bounds, and MIMIC-IV benchmark cohorts.
      </div>

      <div style={{ padding: "0.875rem", backgroundColor: "#fffbeb", border: "1px solid #fde68a", borderRadius: 6, marginBottom: "1.25rem", fontSize: "0.8125rem", color: "#92400e" }}>
        ℹ️ <strong>Scope Restriction Notice:</strong> Decision support is strictly restricted to narrowly defined, verified clinical cohorts. General medical conditions or vague diagnoses outside this registry are intentionally withheld to prevent unvalidated recommendations.
      </div>

      <div style={{ marginBottom: "1.25rem" }}>
        <input
          type="text"
          className="form-input"
          style={{ width: "100%", maxWidth: "450px" }}
          placeholder="Search by condition, ICD code (e.g. E11, I10), or medication..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {filteredCases.map((c) => (
          <div
            key={c.case_id}
            style={{
              border: "1px solid var(--border-light)",
              borderRadius: 8,
              padding: "1.25rem",
              backgroundColor: "#ffffff",
              boxShadow: "var(--shadow-subtle)"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem" }}>
              <div>
                <h3 style={{ fontSize: "1.125rem", color: "var(--text-primary)" }}>
                  {c.diagnosis_name}
                </h3>
                <div style={{ fontSize: "0.8125rem", color: "var(--text-muted)", marginTop: "2px" }}>
                  ICD Codes: <strong>{(c.icd_codes || c.icd_10_codes || []).join(", ")}</strong> | Review Date: {c.review_date}
                </div>
              </div>
              <button
                type="button"
                className="btn-primary"
                style={{ padding: "0.4rem 0.875rem", fontSize: "0.8125rem" }}
                onClick={() => onSelectCase(c.case_id)}
              >
                Assess This Case →
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginTop: "1rem", fontSize: "0.875rem" }}>
              <div>
                <div className="field-label">Eligible Patient Group</div>
                <div>{c.eligible_patient_group}</div>
              </div>

              <div>
                <div className="field-label">Candidate Medicines</div>
                <div style={{ fontWeight: 600, color: "var(--teal-dark)" }}>
                  {c.candidate_medicines.join(", ")}
                </div>
              </div>

              <div>
                <div className="field-label">Required Pre-Decision Inputs</div>
                <div style={{ color: "#b45309", fontWeight: 600 }}>
                  {c.required_inputs.join(", ")}
                </div>
              </div>

              <div>
                <div className="field-label">Dosing & Titration Method</div>
                <div>{c.dosing_method}</div>
              </div>
            </div>

            <div style={{ marginTop: "0.875rem", borderTop: "1px solid var(--border-light)", paddingTop: "0.75rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                <strong>Exclusions:</strong> {c.exclusions.join("; ")}
              </div>
              <a
                href={c.evidence_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--teal-primary)", fontSize: "0.8125rem", fontWeight: 600, textDecoration: "none" }}
              >
                Verified Guideline Source ↗
              </a>
            </div>
          </div>
        ))}

        {filteredCases.length === 0 && (
          <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
            No registered clinical cases match "{searchQuery}".
          </div>
        )}
      </div>
    </div>
  );
};
