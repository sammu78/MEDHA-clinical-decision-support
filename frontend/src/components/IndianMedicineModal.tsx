import React, { useState, useEffect } from "react";
import type { IndianMedicineProduct } from "../types";
import { matchIndianProducts } from "../services/api";

interface IndianMedicineModalProps {
  isOpen: boolean;
  onClose: () => void;
  genericName: string;
  desiredStrength?: string;
  desiredRoute?: string;
}

export const IndianMedicineModal: React.FC<IndianMedicineModalProps> = ({
  isOpen,
  onClose,
  genericName,
  desiredStrength,
  desiredRoute
}) => {
  const [products, setProducts] = useState<IndianMedicineProduct[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && genericName) {
      setLoading(true);
      setError(null);
      matchIndianProducts(genericName, desiredStrength, desiredRoute)
        .then((res) => setProducts(res))
        .catch((err) => setError(err.message || "Failed to load Indian brands."))
        .finally(() => setLoading(false));
    }
  }, [isOpen, genericName, desiredStrength, desiredRoute]);

  if (!isOpen) return null;

  return (
    <div className="citation-modal-overlay" style={{ position: "fixed", inset: 0, backgroundColor: "rgba(9, 30, 58, 0.6)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <div className="citation-modal-content" style={{ background: "var(--bg-card)", maxWidth: "700px", width: "100%", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-lg)", overflow: "hidden", display: "flex", flexDirection: "column", maxHeight: "85vh" }}>
        {/* Header */}
        <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border-light)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "linear-gradient(135deg, var(--hospital-navy), #064e3b)", color: "white" }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.1rem" }}>💊 Matching Indian Commercial Medicines</h3>
            <div style={{ fontSize: "0.75rem", color: "#6ee7b7", marginTop: "2px" }}>
              Active Generic: <strong>{genericName}</strong> {desiredStrength ? `• Strength: ${desiredStrength}` : ""}
            </div>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: "white", fontSize: "1.2rem", cursor: "pointer" }}>✕</button>
        </div>

        {/* Content */}
        <div style={{ padding: "1.25rem 1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.85rem" }}>
          <div style={{ background: "var(--teal-light)", border: "1px solid var(--teal-border)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", fontSize: "0.8rem", color: "var(--teal-dark)", lineHeight: 1.45 }}>
            🛡️ <strong>Prescribing Verification Notice</strong>: Generic ingredient, formulation, route, and strength must be verified before prescribing. Commercial brand availability, CDSCO licensing, and batch availability should be cross-checked at the dispensing pharmacy.
          </div>

          {loading && (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.9rem" }}>
              Searching 11,827 Indian commercial formulations...
            </div>
          )}

          {error && (
            <div style={{ padding: "1rem", background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)", borderRadius: "var(--radius-sm)", fontSize: "0.85rem" }}>
              {error}
            </div>
          )}

          {!loading && !error && products.length === 0 && (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
              No commercial brands with single-ingredient match found for "{genericName}". Please consult the institutional formulary.
            </div>
          )}

          {!loading && products.map((prod) => (
            <div
              key={prod.id}
              style={{
                border: "1px solid var(--border-light)",
                borderRadius: "var(--radius-md)",
                padding: "0.85rem 1rem",
                background: "var(--bg-app)",
                display: "flex",
                flexDirection: "column",
                gap: "0.35rem"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <strong style={{ fontSize: "0.95rem", color: "var(--text-main)" }}>{prod.name}</strong>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    Composition: {prod.composition_raw || prod.generic_ingredients}
                  </div>
                </div>
                <span className="case-badge" style={{ fontSize: "0.7rem" }}>
                  {prod.formulation} • {prod.route}
                </span>
              </div>

              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "4px", fontSize: "0.75rem" }}>
                <span style={{ background: "var(--bg-subtle)", padding: "2px 6px", borderRadius: "4px" }}>
                  Strength: <strong>{prod.strength || "Standard"}</strong>
                </span>
                <span style={{ background: "var(--bg-subtle)", padding: "2px 6px", borderRadius: "4px" }}>
                  Release: <strong>{prod.release_type}</strong>
                </span>
                <span style={{ background: "var(--bg-subtle)", padding: "2px 6px", borderRadius: "4px" }}>
                  Source: <strong>{prod.source}</strong>
                </span>
              </div>

              {prod.uses && (
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "2px" }}>
                  <strong>Indications:</strong> {prod.uses}
                </div>
              )}

              <div style={{ marginTop: "4px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <a
                  href={prod.cdsco_prescribing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: "0.72rem", color: "var(--teal-primary)", textDecoration: "none", fontWeight: 600 }}
                >
                  🔗 CDSCO Prescribing Information ↗
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div style={{ padding: "0.75rem 1.5rem", borderTop: "1px solid var(--border-light)", display: "flex", justifyContent: "flex-end", background: "var(--bg-card)" }}>
          <button onClick={onClose} className="clinical-btn-secondary" style={{ fontSize: "0.85rem" }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
