import React, { useState, useEffect } from "react";
import type { SupportedCase } from "../types";
import { fetchSupportedCases } from "../services/api";

interface CoverageMatrixPageProps {
  onSelectDiseaseForPrescription?: (disease: SupportedCase) => void;
}

export const CoverageMatrixPage: React.FC<CoverageMatrixPageProps> = ({
  onSelectDiseaseForPrescription
}) => {
  const [diseases, setDiseases] = useState<SupportedCase[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedDisease, setSelectedDisease] = useState<SupportedCase | null>(null);

  useEffect(() => {
    fetchSupportedCases()
      .then((data) => {
        setDiseases(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load disease coverage catalogue.");
        setLoading(false);
      });
  }, []);

  const getDiseaseName = (d: SupportedCase) => d.diagnosis_name || d.disease_name || d.case_id || "";

  const categories = [
    "ALL",
    ...Array.from(new Set(diseases.map((d) => d.category || "General").filter(Boolean)))
  ];

  const filtered = diseases.filter((d) => {
    const name = getDiseaseName(d).toLowerCase();
    const id = (d.disease_id || d.case_id || "").toLowerCase();
    const cat = (d.category || "").toLowerCase();
    const meds = (d.candidate_medicines || []).join(" ").toLowerCase();
    const brands = (d.treatment_protocols || [])
      .map((p) => `${p.suggested_brand || ""} ${(p.brand_alternatives || []).join(" ")}`)
      .join(" ")
      .toLowerCase();
    const term = searchTerm.toLowerCase();

    const matchesSearch =
      !searchTerm ||
      name.includes(term) ||
      id.includes(term) ||
      cat.includes(term) ||
      meds.includes(term) ||
      brands.includes(term);

    const matchesCat = selectedCategory === "ALL" || (d.category || "General") === selectedCategory;
    return matchesSearch && matchesCat;
  });

  const handlePrescribe = (disease: SupportedCase, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (onSelectDiseaseForPrescription) {
      onSelectDiseaseForPrescription(disease);
    }
  };

  return (
    <div style={{ flex: 1, padding: "2rem", overflowY: "auto", backgroundColor: "var(--bg-app)" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--hospital-navy)", margin: 0 }}>
            📋 Clinical Disease & Prescription Coverage Matrix
          </h2>
          <span className="case-badge" style={{ fontSize: "0.8rem", padding: "4px 10px" }}>
            {diseases.length} Diseases Registered
          </span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.25rem", maxWidth: "900px" }}>
          Multi-tier clinical coverage matrix aligned with ICMR STWs, CDSCO, and Indian pharmacopeia.
          Click any disease card to view standard dosages, administration routes, and verified Indian commercial brands, or click <strong>Prescribe & Assess</strong> to launch patient evaluation.
        </p>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem", alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search diseases, brands (e.g., Glycomet, Pan 40), or generics..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="form-input"
          style={{ maxWidth: "380px" }}
        />
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={selectedCategory === cat ? "clinical-btn-primary" : "clinical-btn-secondary"}
              style={{ fontSize: "0.75rem", padding: "0.35rem 0.75rem" }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading && <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>Loading coverage catalogue...</div>}
      {error && <div style={{ padding: "1rem", background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)" }}>{error}</div>}

      {/* Grid of Disease Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "1.25rem" }}>
        {filtered.map((d) => {
          const diseaseName = getDiseaseName(d);
          const protocols = d.treatment_protocols || [];
          const topBrands = protocols.map((p) => p.suggested_brand).filter(Boolean).slice(0, 3);

          return (
            <div
              key={d.case_id || d.disease_id || diseaseName}
              onClick={() => setSelectedDisease(d)}
              style={{
                background: "var(--bg-card)",
                border: "1px solid var(--border-light)",
                borderRadius: "var(--radius-md)",
                padding: "1.25rem",
                boxShadow: "var(--shadow-sm)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "0.75rem",
                cursor: "pointer",
                transition: "transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "var(--shadow-md)";
                e.currentTarget.style.borderColor = "var(--teal-primary)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "none";
                e.currentTarget.style.boxShadow = "var(--shadow-sm)";
                e.currentTarget.style.borderColor = "var(--border-light)";
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                  <div>
                    <span style={{ fontSize: "0.68rem", fontWeight: 700, textTransform: "uppercase", color: "var(--teal-primary)" }}>
                      {d.category || "General Clinical"}
                    </span>
                    <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-main)", margin: "2px 0 0 0" }}>
                      {diseaseName}
                    </h3>
                  </div>
                  <span className={`status-badge ${d.is_dose_model_ready ? "proposal-available" : "more-info-needed"}`} style={{ fontSize: "0.68rem", whiteSpace: "nowrap" }}>
                    {d.is_dose_model_ready ? "Dose Ready" : "Subtype Needed"}
                  </span>
                </div>

                {/* ICD & Target Group */}
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "6px" }}>
                  ICD-10: {(d.icd_10_codes || d.icd_codes || []).join(", ") || "Clinical"} • Age: {d.supported_age_group || "All ages"}
                </div>

                {/* Top Suggested Indian Commercial Brands */}
                {topBrands.length > 0 && (
                  <div style={{ marginTop: "0.75rem", background: "rgba(13, 148, 136, 0.08)", padding: "6px 8px", borderRadius: "6px", border: "1px solid rgba(13, 148, 136, 0.2)" }}>
                    <div style={{ fontSize: "0.68rem", fontWeight: 700, color: "var(--teal-primary)", textTransform: "uppercase", display: "flex", alignItems: "center", gap: "4px" }}>
                      🏷️ Prescribed Indian Brands:
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "3px" }}>
                      {topBrands.map((b, idx) => (
                        <span key={idx} style={{ fontSize: "0.72rem", fontWeight: 600, background: "white", color: "var(--hospital-navy)", padding: "1px 6px", borderRadius: "4px", border: "1px solid var(--border-light)" }}>
                          {b}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Candidate Medicines */}
                <div style={{ marginTop: "0.75rem" }}>
                  <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                    Candidate Generic Ingredients:
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "4px" }}>
                    {(d.candidate_medicines || []).slice(0, 4).map((med, idx) => (
                      <span key={idx} style={{ fontSize: "0.72rem", background: "var(--bg-subtle)", padding: "2px 6px", borderRadius: "4px", border: "1px solid var(--border-subtle)" }}>
                        {med}
                      </span>
                    ))}
                    {(d.candidate_medicines?.length || 0) > 4 && (
                      <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", padding: "2px 4px" }}>
                        +{(d.candidate_medicines?.length || 0) - 4} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Dose Method Coverage */}
                <div style={{ marginTop: "0.65rem", fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                  <strong>Dose Method:</strong> {d.dose_method_coverage || d.dosing_method || "Guideline-directed dosing algorithm"}
                </div>

                {/* Subtype Notice if broad */}
                {d.subtype_prompt_guidance && (
                  <div style={{ marginTop: "0.5rem", background: "var(--badge-warn-bg)", border: "1px solid var(--badge-warn-border)", padding: "0.5rem", borderRadius: "var(--radius-sm)", fontSize: "0.72rem", color: "var(--badge-warn-text)", lineHeight: 1.35 }}>
                    ⚠️ <strong>Subtype Requirement:</strong> {d.subtype_prompt_guidance}
                  </div>
                )}
              </div>

              {/* Action Buttons Footer */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.75rem", marginTop: "0.5rem", gap: "0.5rem" }}>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedDisease(d);
                  }}
                  className="clinical-btn-secondary"
                  style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem" }}
                >
                  🔍 Protocols & Brands ↗
                </button>
                <button
                  type="button"
                  onClick={(e) => handlePrescribe(d, e)}
                  className="clinical-btn-primary"
                  style={{ fontSize: "0.75rem", padding: "0.35rem 0.8rem", display: "flex", alignItems: "center", gap: "4px" }}
                >
                  💊 Prescribe & Assess
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disease Detail Modal */}
      {selectedDisease && (
        <div
          className="citation-modal-overlay"
          onClick={() => setSelectedDisease(null)}
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(9, 30, 58, 0.65)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1rem"
          }}
        >
          <div
            className="citation-modal-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "var(--bg-card)",
              maxWidth: "820px",
              width: "100%",
              borderRadius: "var(--radius-lg)",
              boxShadow: "var(--shadow-lg)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              maxHeight: "90vh"
            }}
          >
            {/* Modal Header */}
            <div
              style={{
                padding: "1.25rem 1.5rem",
                borderBottom: "1px solid var(--border-light)",
                background: "var(--hospital-navy)",
                color: "white",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>
                  {getDiseaseName(selectedDisease)}
                </h3>
                <div style={{ fontSize: "0.75rem", color: "#99f6e4", marginTop: "2px" }}>
                  Category: {selectedDisease.category} • ICD-10: {(selectedDisease.icd_10_codes || selectedDisease.icd_codes || []).join(", ") || "Clinical"} • Care Setting: {(selectedDisease.supported_care_setting || ["Primary Care / Outpatient"]).join(", ")}
                </div>
              </div>
              <button
                onClick={() => setSelectedDisease(null)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "white",
                  fontSize: "1.4rem",
                  cursor: "pointer",
                  lineHeight: 1
                }}
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: "1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.25rem", fontSize: "0.85rem" }}>
              
              {/* Treatment Protocols & Commercial Brands Section */}
              {selectedDisease.treatment_protocols && selectedDisease.treatment_protocols.length > 0 ? (
                <div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <h4 style={{ margin: 0, fontSize: "0.95rem", color: "var(--hospital-navy)", fontWeight: 700 }}>
                      💊 Standard Treatment Protocols & Indian Commercial Brands
                    </h4>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                      CDSCO / Jan Aushadhi / ICMR Aligned
                    </span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    {selectedDisease.treatment_protocols.map((proto, idx) => (
                      <div
                        key={idx}
                        style={{
                          border: "1px solid var(--border-light)",
                          borderRadius: "var(--radius-md)",
                          padding: "0.85rem",
                          background: "var(--bg-subtle)"
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem" }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--text-main)" }}>
                              {proto.generic_name}
                            </div>
                            <div style={{ fontSize: "0.8rem", color: "var(--teal-primary)", fontWeight: 600, marginTop: "2px" }}>
                              Suggested Brand: <span style={{ background: "white", padding: "2px 8px", borderRadius: "4px", border: "1px solid var(--teal-primary)" }}>🏷️ {proto.suggested_brand}</span>
                            </div>
                          </div>
                          <span style={{ fontSize: "0.75rem", background: "var(--bg-card)", padding: "3px 8px", borderRadius: "4px", border: "1px solid var(--border-light)", color: "var(--text-secondary)" }}>
                            {proto.route} • {proto.frequency}
                          </span>
                        </div>

                        {proto.brand_alternatives && proto.brand_alternatives.length > 0 && (
                          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "6px" }}>
                            <strong>Alternative Brands:</strong> {proto.brand_alternatives.join(", ")}
                          </div>
                        )}

                        <div style={{ marginTop: "6px", fontSize: "0.8rem", color: "var(--text-main)" }}>
                          <strong>Dosage:</strong> {proto.adult_dosage}
                        </div>

                        {proto.timing_instructions && (
                          <div style={{ marginTop: "4px", fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                            <strong>Instructions:</strong> {proto.timing_instructions}
                          </div>
                        )}

                        {proto.renal_adjustment && (
                          <div style={{ marginTop: "4px", fontSize: "0.75rem", color: "#b45309", background: "#fef3c7", padding: "4px 8px", borderRadius: "4px" }}>
                            <strong>Renal Note:</strong> {proto.renal_adjustment}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", color: "var(--hospital-navy)", fontWeight: 700 }}>
                    Candidate Medicines
                  </h4>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {(selectedDisease.candidate_medicines || []).map((med, idx) => (
                      <span key={idx} style={{ padding: "4px 10px", background: "var(--bg-subtle)", borderRadius: "4px", border: "1px solid var(--border-light)", fontSize: "0.8rem" }}>
                        {med}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence & Guidelines */}
              <div style={{ borderTop: "1px solid var(--border-light)", paddingTop: "0.75rem" }}>
                <strong>Evidence Coverage:</strong>
                <p style={{ marginTop: "2px", color: "var(--text-secondary)" }}>{selectedDisease.evidence_coverage}</p>
              </div>

              <div>
                <strong>Dose Method Coverage:</strong>
                <p style={{ marginTop: "2px", color: "var(--text-secondary)" }}>{selectedDisease.dose_method_coverage || selectedDisease.dosing_method}</p>
              </div>

              {/* Required Inputs */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                <div className="patient-metric-card">
                  <div className="patient-metric-label">Supported Care Setting</div>
                  <div className="patient-metric-val" style={{ fontSize: "0.8rem" }}>
                    {(selectedDisease.supported_care_setting || ["Primary Care / Inpatient"]).join(", ")}
                  </div>
                </div>
                <div className="patient-metric-card">
                  <div className="patient-metric-label">Required Parameters</div>
                  <div className="patient-metric-val" style={{ fontSize: "0.8rem" }}>
                    {(selectedDisease.required_inputs || ["Vitals", "Renal function"]).join(", ")}
                  </div>
                </div>
              </div>

              {/* Contraindications / Exclusions */}
              {selectedDisease.exclusions && selectedDisease.exclusions.length > 0 && (
                <div style={{ background: "var(--badge-fail-bg)", border: "1px solid var(--badge-fail-border)", padding: "0.75rem", borderRadius: "var(--radius-sm)" }}>
                  <strong style={{ color: "var(--badge-fail-text)" }}>Strict Clinical Contraindications / Exclusions:</strong>
                  <ul style={{ paddingLeft: "1.2rem", marginTop: "4px", color: "var(--badge-fail-text)", marginBottom: 0 }}>
                    {selectedDisease.exclusions.map((ex, idx) => (
                      <li key={idx}>{ex}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Modal Footer with Primary Prescribe CTA */}
            <div
              style={{
                padding: "1rem 1.5rem",
                borderTop: "1px solid var(--border-light)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                background: "var(--bg-subtle)"
              }}
            >
              <button onClick={() => setSelectedDisease(null)} className="clinical-btn-secondary">
                Close
              </button>
              <button
                type="button"
                onClick={() => {
                  const diseaseToStart = selectedDisease;
                  setSelectedDisease(null);
                  handlePrescribe(diseaseToStart);
                }}
                className="clinical-btn-primary"
                style={{ display: "flex", alignItems: "center", gap: "6px", padding: "0.5rem 1.25rem", fontSize: "0.88rem", fontWeight: 700 }}
              >
                🚀 Prescribe This Therapy / Start Case
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
