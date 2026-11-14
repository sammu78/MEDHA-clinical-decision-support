import React from "react";
import type { ClinicalCase } from "../types";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  cases: ClinicalCase[];
  activeCaseId: string;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  isDarkTheme: boolean;
  onToggleTheme: () => void;
  backendOnline: boolean | null;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  cases,
  activeCaseId,
  onSelectCase,
  onNewCase,
  isDarkTheme,
  onToggleTheme,
  backendOnline,
  collapsed,
  onToggleCollapse
}) => {
  return (
    <aside className={`app-sidebar ${collapsed ? "collapsed" : ""}`}>
      {/* Brand & Collapse */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">💊</div>
          {!collapsed && (
            <div>
              <div style={{ lineHeight: 1.2 }}>AushadhiDose</div>
              <div style={{ fontSize: "0.65rem", color: "#94a3b8", fontWeight: 400 }}>
                Indian Clinical Decision Support
              </div>
            </div>
          )}
        </div>
        <button
          className="sidebar-collapse-btn"
          onClick={onToggleCollapse}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? "▶" : "◀"}
        </button>
      </div>

      {/* New Case Button */}
      <button className="sidebar-new-case-btn" onClick={onNewCase} title="Start new clinical assessment">
        <span>+</span>
        {!collapsed && <span>New Patient Case</span>}
      </button>

      {/* Primary Navigation */}
      <div className="sidebar-nav-section">
        {/* 0. Simple Input & Output */}
        <div
          className={`sidebar-nav-item ${activeTab === "simple" ? "active" : ""}`}
          onClick={() => setActiveTab("simple")}
          title="Simple Input and Output Predictor"
        >
          <span>⚡</span>
          {!collapsed && <span>Simple Input & Output</span>}
        </div>

        {/* 1. Overview Dashboard */}
        <div
          className={`sidebar-nav-item ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
          title="Clinical Overview Dashboard"
        >
          <span>📈</span>
          {!collapsed && <span>Overview Dashboard</span>}
        </div>

        {/* 2. New Clinical Assessment */}
        <div
          className={`sidebar-nav-item ${activeTab === "new_assessment" ? "active" : ""}`}
          onClick={() => setActiveTab("new_assessment")}
          title="Guided multi-section clinical assessment"
        >
          <span>🩺</span>
          {!collapsed && <span>New Clinical Assessment</span>}
        </div>

        {/* 3. Patient Cases */}
        <div
          className={`sidebar-nav-item ${activeTab === "workspace" ? "active" : ""}`}
          onClick={() => setActiveTab("workspace")}
          title="Patient Cases & Conversational Assistant"
        >
          <span>💬</span>
          {!collapsed && <span>Patient Cases</span>}
        </div>

        {/* 4. Medicine Explorer */}
        <div
          className={`sidebar-nav-item ${activeTab === "medicines" ? "active" : ""}`}
          onClick={() => setActiveTab("medicines")}
          title="Search 11,827 Indian commercial medicines"
        >
          <span>💊</span>
          {!collapsed && <span>Medicine Explorer</span>}
        </div>

        {/* 5. Dosage and Renal Safety */}
        <div
          className={`sidebar-nav-item ${activeTab === "safety" || activeTab === "catalogue" ? "active" : ""}`}
          onClick={() => setActiveTab("safety")}
          title="Dosage protocols, eGFR & CrCl Renal Safety"
        >
          <span>🛡️</span>
          {!collapsed && <span>Dosage & Renal Safety</span>}
        </div>

        {/* 6. Evidence Library */}
        <div
          className={`sidebar-nav-item ${activeTab === "evidence" ? "active" : ""}`}
          onClick={() => setActiveTab("evidence")}
          title="ICMR STWs & CDSCO Guidelines Library"
        >
          <span>📚</span>
          {!collapsed && <span>Evidence Library</span>}
        </div>

        {/* 7. Model Explainability */}
        <div
          className={`sidebar-nav-item ${activeTab === "explainability" ? "active" : ""}`}
          onClick={() => setActiveTab("explainability")}
          title="TreeSHAP Feature Attributions & Visual Rationales"
        >
          <span>🔬</span>
          {!collapsed && <span>Model Explainability</span>}
        </div>

        {/* 8. Audit History & Benchmarks */}
        <div
          className={`sidebar-nav-item ${activeTab === "audit" ? "active" : ""}`}
          onClick={() => setActiveTab("audit")}
          title="MIMIC-IV Benchmark Evaluation & Data Audit"
        >
          <span>📊</span>
          {!collapsed && <span>Model Audit & Benchmarks</span>}
        </div>

        {/* 9. Dataset & Model Evaluation */}
        <div
          className={`sidebar-nav-item ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          title="27-Disease Evaluation Matrix & Model Readiness"
        >
          <span>📋</span>
          {!collapsed && <span>Dataset & Evaluation</span>}
        </div>

        {/* 10. Settings */}
        <div
          className={`sidebar-nav-item ${activeTab === "settings" ? "active" : ""}`}
          onClick={() => setActiveTab("settings")}
          title="System & Clinical Governance Settings"
        >
          <span>⚙️</span>
          {!collapsed && <span>Settings</span>}
        </div>
      </div>

      {/* Recent Cases History */}
      {!collapsed && (
        <div className="sidebar-case-history">
          <div className="sidebar-nav-title" style={{ paddingLeft: "0.25rem", marginBottom: "0.25rem" }}>
            Recent Cases ({cases.length})
          </div>
          {cases.map((c) => (
            <div
              key={c.case_id}
              className={`case-history-item ${c.case_id === activeCaseId ? "active" : ""}`}
              onClick={() => {
                onSelectCase(c.case_id);
                setActiveTab("workspace");
              }}
            >
              <div className="case-history-title">
                {c.diagnosis_name || c.title || c.case_id}
              </div>
              <div className="case-history-meta">
                <span>v{c.patient_version}</span>
                <span>{c.approved_by_doctor ? "✓ Approved" : "Pending"}</span>
              </div>
            </div>
          ))}
          {cases.length === 0 && (
            <div style={{ fontSize: "0.75rem", color: "#64748b", padding: "0.5rem" }}>
              No recent cases yet.
            </div>
          )}
        </div>
      )}

      {/* Footer / Status */}
      <div className="sidebar-footer">
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: backendOnline ? "#10b981" : backendOnline === false ? "#ef4444" : "#f59e0b"
            }}
          />
          {!collapsed && (
            <span style={{ fontSize: "0.7rem" }}>
              {backendOnline ? "API Online" : "Backend Offline"}
            </span>
          )}
        </div>
        <button
          onClick={onToggleTheme}
          style={{
            background: "transparent",
            border: "none",
            color: "#94a3b8",
            cursor: "pointer",
            fontSize: "0.85rem"
          }}
          title={isDarkTheme ? "Switch to light theme" : "Switch to dark theme"}
        >
          {isDarkTheme ? "☀️" : "🌙"}
        </button>
      </div>
    </aside>
  );
};
