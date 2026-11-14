import React from "react";

interface SettingsPageProps {
  isDarkTheme: boolean;
  onToggleTheme: () => void;
  backendOnline: boolean | null;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  isDarkTheme,
  onToggleTheme,
  backendOnline
}) => {
  return (
    <div className="workspace-main" style={{ padding: "1.5rem", overflowY: "auto", maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.6rem", fontWeight: 700, color: "var(--navy-900, #0f2744)" }}>
          System & Clinical Governance Settings
        </h1>
        <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.875rem" }}>
          Configure clinician session parameters, safety gate defaults, and interface settings.
        </p>
      </div>

      {/* Safety Gate Governance Card */}
      <div style={{ backgroundColor: "#fff", padding: "1.5rem", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "1.5rem" }}>
        <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.1rem", fontWeight: 600, color: "#0f2744" }}>
          🛡️ Clinical Safety Gate Policy
        </h3>
        <p style={{ fontSize: "0.85rem", color: "#475569", lineHeight: 1.5, margin: "0 0 1rem 0" }}>
          In accordance with CDSS governance standards, every dosage proposal is strictly gated by clinical guidelines (ICMR STWs, KDIGO 2023, ADA 2024). Doses are automatically withheld whenever required laboratory markers are missing or critical physiological contraindications are triggered.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.85rem" }}>
          <div style={{ backgroundColor: "#f8fafc", padding: "0.75rem", borderRadius: "6px" }}>
            <span style={{ color: "#64748b", display: "block", fontSize: "0.75rem" }}>Renal Function Standard</span>
            <span style={{ fontWeight: 600, color: "#0f2744" }}>CKD-EPI (2021) Race-Neutral & Cockcroft-Gault</span>
          </div>
          <div style={{ backgroundColor: "#f8fafc", padding: "0.75rem", borderRadius: "6px" }}>
            <span style={{ color: "#64748b", display: "block", fontSize: "0.75rem" }}>Temporal Lookback Window</span>
            <span style={{ fontWeight: 600, color: "#0f2744" }}>Strict 7-Day Pre-Decision Cutoff (Zero Leakage)</span>
          </div>
          <div style={{ backgroundColor: "#f8fafc", padding: "0.75rem", borderRadius: "6px" }}>
            <span style={{ color: "#64748b", display: "block", fontSize: "0.75rem" }}>Safety Engine Version</span>
            <span style={{ fontWeight: 600, color: "#0f2744" }}>v2.2.0-IndianClinicalPractice</span>
          </div>
          <div style={{ backgroundColor: "#f8fafc", padding: "0.75rem", borderRadius: "6px" }}>
            <span style={{ color: "#64748b", display: "block", fontSize: "0.75rem" }}>Prescription Override</span>
            <span style={{ fontWeight: 600, color: "#b91c1c" }}>Requires Attending Physician Sign-Off</span>
          </div>
        </div>
      </div>

      {/* Backend & Database Connection */}
      <div style={{ backgroundColor: "#fff", padding: "1.5rem", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "1.5rem" }}>
        <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.1rem", fontWeight: 600, color: "#0f2744" }}>
          🔌 Infrastructure & Service Connectivity
        </h3>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 0", borderBottom: "1px solid #f1f5f9" }}>
          <div>
            <div style={{ fontWeight: 500, color: "#0f2744" }}>FastAPI Clinical Backend</div>
            <div style={{ fontSize: "0.75rem", color: "#64748b" }}>REST endpoints & SSE Streaming at http://127.0.0.1:8000</div>
          </div>
          <span style={{
            padding: "0.2rem 0.6rem",
            borderRadius: "4px",
            fontSize: "0.75rem",
            fontWeight: 600,
            backgroundColor: backendOnline ? "#dcfce7" : "#fee2e2",
            color: backendOnline ? "#166534" : "#b91c1c"
          }}>
            {backendOnline ? "● CONNECTED (Healthy)" : "○ DISCONNECTED"}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 0" }}>
          <div>
            <div style={{ fontWeight: 500, color: "#0f2744" }}>SQLite Fact–Dimension Warehouse</div>
            <div style={{ fontSize: "0.75rem", color: "#64748b" }}>clinical_decision_support.db (Normalized Star Schema v2.2)</div>
          </div>
          <span style={{ padding: "0.2rem 0.6rem", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 600, backgroundColor: "#dcfce7", color: "#166534" }}>
            ● ACTIVE (11,825 Products, 2,010 Decisions)
          </span>
        </div>
      </div>

      {/* User Preferences */}
      <div style={{ backgroundColor: "#fff", padding: "1.5rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1.1rem", fontWeight: 600, color: "#0f2744" }}>
          🎨 Interface Preferences
        </h3>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 0" }}>
          <div>
            <div style={{ fontWeight: 500, color: "#0f2744" }}>Clinical High-Contrast Theme</div>
            <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Toggle between Soft Clinical Day and Night Theme</div>
          </div>
          <button
            onClick={onToggleTheme}
            style={{
              padding: "0.4rem 0.8rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              backgroundColor: "#f8fafc",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.8rem"
            }}
          >
            {isDarkTheme ? "Switch to Light Theme" : "Switch to Dark Theme"}
          </button>
        </div>
      </div>
    </div>
  );
};
