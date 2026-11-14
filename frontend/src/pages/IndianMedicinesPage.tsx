import React, { useState, useEffect } from "react";
import type { IndianMedicineProduct } from "../types";
import { searchIndianMedicines } from "../services/api";

export const IndianMedicinesPage: React.FC = () => {
  const [query, setQuery] = useState<string>("");
  const [formulation, setFormulation] = useState<string>("");
  const [products, setProducts] = useState<IndianMedicineProduct[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(0);
  const limit = 20;

  const loadMedicines = (searchQ: string, formFilter: string, pageNum: number) => {
    setLoading(true);
    setError(null);
    searchIndianMedicines(searchQ, undefined, formFilter || undefined, limit, pageNum * limit)
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to search Indian medicines.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadMedicines(query, formulation, page);
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    loadMedicines(query, formulation, 0);
  };

  return (
    <div style={{ flex: 1, padding: "2rem", overflowY: "auto", backgroundColor: "var(--bg-app)" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--hospital-navy)", margin: 0 }}>
            💊 Indian Commercial Medicines Formulary
          </h2>
          <span className="case-badge" style={{ fontSize: "0.8rem", padding: "4px 10px" }}>
            11,827 Products
          </span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.25rem", maxWidth: "900px" }}>
          Search commercial Indian brand formulations by brand name, generic active ingredient, formulation, or clinical indications. CDSCO prescribing information and approved new drug lists are cross-referenced.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearchSubmit} style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1.5rem", alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search brand (e.g. Augmentin, Amlong, Glycomet, Azithral) or generic..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="form-input"
          style={{ maxWidth: "420px", flex: 1 }}
        />
        <select
          value={formulation}
          onChange={(e) => setFormulation(e.target.value)}
          className="form-input"
          style={{ maxWidth: "200px" }}
        >
          <option value="">All Formulations</option>
          <option value="Tablet">Tablets</option>
          <option value="Capsule">Capsules</option>
          <option value="Injection">Injections / Infusions</option>
          <option value="Oral Liquid / Syrup">Syrups / Suspensions</option>
          <option value="Topical">Creams / Ointments</option>
          <option value="Inhaler / Respules">Inhalers</option>
        </select>
        <button type="submit" className="clinical-btn-primary" style={{ padding: "0.6rem 1.25rem" }}>
          Search
        </button>
      </form>

      {loading && <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>Searching commercial catalogue...</div>}
      {error && <div style={{ padding: "1rem", background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)" }}>{error}</div>}

      {/* Results Table */}
      {!loading && (
        <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", overflow: "hidden", boxShadow: "var(--shadow-sm)" }}>
          <div style={{ overflowX: "auto" }}>
            <table className="clinical-data-table" style={{ width: "100%", margin: 0 }}>
              <thead>
                <tr>
                  <th>Brand Name</th>
                  <th>Active Generic Ingredients</th>
                  <th>Strength</th>
                  <th>Formulation & Route</th>
                  <th>Release Type</th>
                  <th>Indications</th>
                  <th>Regulatory Source</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <strong style={{ color: "var(--text-main)" }}>{p.name}</strong>
                      {p.is_combination && (
                        <span style={{ fontSize: "0.65rem", background: "#fef3c7", color: "#92400e", padding: "1px 5px", borderRadius: "3px", marginLeft: "6px" }}>
                          FDC Combination
                        </span>
                      )}
                    </td>
                    <td>
                      <span style={{ color: "var(--teal-dark)", fontWeight: 600 }}>{p.generic_ingredients}</span>
                    </td>
                    <td>{p.strength || "—"}</td>
                    <td>{p.formulation} ({p.route})</td>
                    <td>{p.release_type}</td>
                    <td style={{ maxWidth: "240px", fontSize: "0.75rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} title={p.uses}>
                      {p.uses || "Standard indication"}
                    </td>
                    <td>
                      <a
                        href={p.cdsco_prescribing_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ fontSize: "0.72rem", color: "var(--teal-primary)", textDecoration: "none", fontWeight: 600 }}
                      >
                        CDSCO Notification ↗
                      </a>
                    </td>
                  </tr>
                ))}
                {products.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                      No medicines matched the specified criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div style={{ padding: "0.75rem 1.5rem", borderTop: "1px solid var(--border-light)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--bg-subtle)" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Page {page + 1} (showing {products.length} items)
            </span>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                onClick={() => setPage((prev) => Math.max(0, prev - 1))}
                disabled={page === 0}
                className="clinical-btn-secondary"
                style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
              >
                ◀ Previous
              </button>
              <button
                onClick={() => setPage((prev) => prev + 1)}
                disabled={products.length < limit}
                className="clinical-btn-secondary"
                style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
              >
                Next ▶
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
