import React from "react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  backendOnline: boolean | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, backendOnline }) => {
  return (
    <header className="hospital-header">
      <div className="header-top">
        <div className="header-top-inner">
          <div className="brand-wrapper">
            <div className="brand-caduceus">Rx</div>
            <div className="brand-text">
              <h1>Explainable Drug & Dosage Decision Support</h1>
              <p>MIMIC-IV Retrospective Benchmarks • Multi-Tier Safety Engine • Verified Clinical Guidelines</p>
            </div>
          </div>

          <div className="header-actions">
            <div className="status-pill">
              <span className={`status-dot ${backendOnline === true ? "online" : "offline"}`} />
              <span>{backendOnline === true ? "CDS Engine Connected (FastAPI)" : "CDS Engine Offline"}</span>
            </div>
          </div>
        </div>
      </div>

      <nav className="header-nav">
        <div className="nav-inner">
          <button
            className={`nav-tab-btn ${activeTab === "assess" ? "active" : ""}`}
            onClick={() => setActiveTab("assess")}
          >
            <span>📝</span> Patient Encounter & Assessment
          </button>
          <button
            className={`nav-tab-btn ${activeTab === "cases" ? "active" : ""}`}
            onClick={() => setActiveTab("cases")}
          >
            <span>📚</span> Supported Cases Registry
          </button>
          <button
            className={`nav-tab-btn ${activeTab === "models" ? "active" : ""}`}
            onClick={() => setActiveTab("models")}
          >
            <span>🔬</span> MIMIC-IV Model Benchmarks
          </button>
        </div>
      </nav>
    </header>
  );
};
