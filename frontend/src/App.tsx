import React, { useState, useEffect } from "react";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { Sidebar } from "./components/Sidebar";
import { PatientPanel } from "./components/PatientPanel";
import { EditPatientModal } from "./components/EditPatientModal";

import { OverviewDashboardPage } from "./pages/OverviewDashboardPage";
import { SimpleInputOutputPage } from "./pages/SimpleInputOutputPage";
import { ChatWorkspace } from "./pages/ChatWorkspace";
import { AssessmentFormPage } from "./pages/AssessmentFormPage";
import { AssessmentResultPage } from "./pages/AssessmentResultPage";
import { CoverageMatrixPage } from "./pages/CoverageMatrixPage";
import { IndianMedicinesPage } from "./pages/IndianMedicinesPage";
import { EvidenceLibraryPage } from "./pages/EvidenceLibraryPage";
import { ModelDetailsPage } from "./pages/ModelDetailsPage";
import { ModelAuditPage } from "./pages/ModelAuditPage";
import { SupportedCasesPage } from "./pages/SupportedCasesPage";
import { SettingsPage } from "./pages/SettingsPage";

import type { ClinicalCase, SupportedCase, PatientAssessmentRequest, AssessmentResponse } from "./types";
import {
  checkBackendHealth,
  listClinicalCases,
  createClinicalCase,
  fetchClinicalCase,
  updatePatientData,
  fetchSupportedCases,
  assessPatient
} from "./services/api";

import "./styles/clinical.css";

const DEFAULT_FORM_DATA: PatientAssessmentRequest = {
  diagnosis_id: "type_2_diabetes",
  age: 58,
  weight_kg: 78.5,
  gender: "M",
  allergies: [],
  current_medications: [],
  existing_conditions: [],
  labs: {
    glucose: { name: "GLUCOSE", value: 185, unit: "mg/dL" },
    creatinine: { name: "CREATININE", value: 1.1, unit: "mg/dL" },
    potassium: { name: "POTASSIUM", value: 4.3, unit: "mEq/L" },
    sodium: { name: "SODIUM", value: 139, unit: "mEq/L" },
    bun: { name: "BUN", value: 18, unit: "mg/dL" }
  }
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("simple");
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [cases, setCases] = useState<ClinicalCase[]>([]);
  const [currentCase, setCurrentCase] = useState<ClinicalCase | null>(null);
  const [supportedCases, setSupportedCases] = useState<SupportedCase[]>([]);
  const [isDarkTheme, setIsDarkTheme] = useState<boolean>(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [patientPanelOpen, setPatientPanelOpen] = useState<boolean>(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);

  // Direct Assessment Form & Result State
  const [assessmentFormData, setAssessmentFormData] = useState<PatientAssessmentRequest>(DEFAULT_FORM_DATA);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResponse | null>(null);
  const [isAssessing, setIsAssessing] = useState<boolean>(false);
  const [assessmentError, setAssessmentError] = useState<string | null>(null);

  // Initialize: Check backend health, load cases, and fetch supported cases
  useEffect(() => {
    checkBackendHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));

    fetchSupportedCases()
      .then((data) => setSupportedCases(data))
      .catch((err) => console.error("Error loading supported cases:", err));

    listClinicalCases()
      .then((loadedCases) => {
        setCases(loadedCases);
        if (loadedCases.length > 0) {
          fetchClinicalCase(loadedCases[0].case_id).then((c) => setCurrentCase(c));
        } else {
          createClinicalCase().then((newC) => {
            setCases([newC]);
            setCurrentCase(newC);
          });
        }
      })
      .catch((err) => console.error("Error loading clinical cases:", err));
  }, []);

  const handleToggleTheme = () => {
    setIsDarkTheme((prev) => {
      const next = !prev;
      if (next) {
        document.body.classList.add("dark-theme");
      } else {
        document.body.classList.remove("dark-theme");
      }
      return next;
    });
  };

  const handleNewCase = async () => {
    try {
      const newCase = await createClinicalCase();
      setCases((prev) => [newCase, ...prev]);
      setCurrentCase(newCase);
      setActiveTab("workspace");
    } catch (err) {
      console.error("Failed to create new case:", err);
    }
  };

  const handleSelectDiseaseForPrescription = async (disease: SupportedCase) => {
    const diseaseName = disease.diagnosis_name || disease.disease_name || disease.case_id || "";
    try {
      const newCase = await createClinicalCase();
      await updatePatientData(newCase.case_id, {
        diagnosis: diseaseName,
        chief_complaint: `Evaluation and therapy initiation for ${diseaseName}`
      });
      const refreshed = await fetchClinicalCase(newCase.case_id);
      setCases((prev) => [refreshed, ...prev]);
      setCurrentCase(refreshed);
      setActiveTab("workspace");
    } catch (err) {
      console.error("Failed to initialize prescription case:", err);
      setActiveTab("workspace");
    }
  };

  const handleSelectCase = async (caseId: string) => {
    try {
      const fullCase = await fetchClinicalCase(caseId);
      setCurrentCase(fullCase);
    } catch (err) {
      console.error("Failed to select case:", err);
    }
  };

  const handleRefreshCase = async () => {
    if (!currentCase) return;
    try {
      const fullCase = await fetchClinicalCase(currentCase.case_id);
      setCurrentCase(fullCase);
      setCases((prev) =>
        prev.map((c) => (c.case_id === fullCase.case_id ? fullCase : c))
      );
    } catch (err) {
      console.error("Failed to refresh case:", err);
    }
  };

  const handleSavePatientData = async (updatedData: Record<string, any>) => {
    if (!currentCase) return;
    await updatePatientData(currentCase.case_id, updatedData);
    await handleRefreshCase();
  };

  // Direct assessment submit handler
  const handleAssessmentSubmit = async (formData: PatientAssessmentRequest) => {
    setIsAssessing(true);
    setAssessmentError(null);
    try {
      setAssessmentFormData(formData);
      const res = await assessPatient(formData);
      setAssessmentResult(res);
    } catch (err: any) {
      console.error("Assessment submit error:", err);
      setAssessmentError(err?.message || "Failed to complete clinical assessment.");
    } finally {
      setIsAssessing(false);
    }
  };

  const getActiveTabTitle = () => {
    switch (activeTab) {
      case "simple": return "Simple Predictor (Direct Input & Output)";
      case "dashboard": return "Overview Dashboard";
      case "new_assessment": return "New Clinical Assessment";
      case "workspace": return "Patient Cases & Conversational Assistant";
      case "medicines": return "Indian Commercial Medicines (CDSCO)";
      case "safety":
      case "catalogue": return "Dosage Protocols & Renal Safety";
      case "evidence": return "Clinical Practice Guidelines & RAG Library";
      case "explainability": return "Model Explainability (TreeSHAP Attributions)";
      case "audit": return "Audit History & MIMIC-IV Benchmarks";
      case "evaluation": return "27-Disease Evaluation & Model Readiness";
      case "settings": return "System & Clinical Governance Settings";
      default: return "Clinical Decision Support";
    }
  };

  return (
    <div className="app-container">
      {/* Prominent Clinical Research Disclaimer */}
      <DisclaimerBanner />

      {/* Header bar */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "0.6rem 1.5rem",
          backgroundColor: "#ffffff",
          borderBottom: "1px solid #e2e8f0",
          fontSize: "0.85rem",
          zIndex: 10
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "1.3rem" }}>💊</span>
          <div>
            <strong style={{ color: "#0f2744", fontSize: "1rem", letterSpacing: "-0.01em" }}>MEDHA</strong>
            <span style={{ margin: "0 8px", color: "#cbd5e1" }}>|</span>
            <span style={{ color: "#0d9488", fontWeight: 600 }}>
              {activeTab === "simple" ? "Clinical Decision Support System" : getActiveTabTitle()}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          {/* Engineering / Audit toggle */}
          {activeTab === "simple" ? (
            <button
              type="button"
              onClick={() => setActiveTab("dashboard")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "0.35rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #cbd5e1",
                background: "#f8fafc",
                color: "#64748b",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer"
              }}
              title="Access underlying database warehouse, import logs, and model benchmarks"
            >
              <span>⚙️</span>
              <span>Developer / Admin Area</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setActiveTab("simple")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "0.35rem 0.85rem",
                borderRadius: "6px",
                border: "none",
                background: "#0d9488",
                color: "#ffffff",
                fontSize: "0.8rem",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              <span>←</span>
              <span>Back to Clinical Assessment</span>
            </button>
          )}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "0.25rem 0.65rem",
              borderRadius: "20px",
              fontSize: "0.75rem",
              fontWeight: 600,
              backgroundColor: backendOnline ? "#dcfce7" : "#fee2e2",
              color: backendOnline ? "#166534" : "#b91c1c"
            }}
          >
            <span>{backendOnline ? "●" : "○"}</span>
            <span>{backendOnline ? "Engine Connected" : "Engine Offline"}</span>
          </div>

          <div style={{ color: "#475569", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "5px" }}>
            <span>👨‍⚕️</span>
            <span>Authorized Evaluator</span>
          </div>
        </div>
      </header>

      {/* When in Simple Mode, show distraction-free full-width Input & Output view */}
      {activeTab === "simple" ? (
        <div style={{ flex: 1, overflowY: "auto", width: "100%", background: "#f8fafc" }}>
          <SimpleInputOutputPage />
        </div>
      ) : (
        /* Application Workspace Layout for Full System */
        <div className="app-workspace-layout">
          {/* Left Sidebar */}
          <Sidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            cases={cases}
            activeCaseId={currentCase?.case_id || ""}
            onSelectCase={handleSelectCase}
            onNewCase={handleNewCase}
            isDarkTheme={isDarkTheme}
            onToggleTheme={handleToggleTheme}
            backendOnline={backendOnline}
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
          />

          {/* Central Viewport */}
          {activeTab === "dashboard" && (
            <OverviewDashboardPage
              onNavigateTab={setActiveTab}
              onSelectCase={(cid) => {
                handleSelectCase(cid);
                setActiveTab("workspace");
              }}
            />
          )}

          {activeTab === "new_assessment" && (
            <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem" }}>
              {assessmentResult ? (
                <AssessmentResultPage
                  result={assessmentResult}
                  onBackToForm={() => setAssessmentResult(null)}
                />
              ) : (
                <AssessmentFormPage
                  initialData={assessmentFormData}
                  supportedCases={supportedCases}
                  onSubmit={handleAssessmentSubmit}
                  isLoading={isAssessing}
                  errorMessage={assessmentError}
                />
              )}
            </div>
          )}

        {activeTab === "workspace" && (
          <ChatWorkspace
            currentCase={currentCase}
            onRefreshCase={handleRefreshCase}
            onOpenEditModal={() => setIsEditModalOpen(true)}
            onTogglePatientPanel={() => setPatientPanelOpen((prev) => !prev)}
          />
        )}

        {(activeTab === "safety" || activeTab === "catalogue") && (
          <CoverageMatrixPage
            onSelectDiseaseForPrescription={handleSelectDiseaseForPrescription}
          />
        )}

        {activeTab === "medicines" && <IndianMedicinesPage />}

        {activeTab === "evidence" && <EvidenceLibraryPage />}

        {activeTab === "explainability" && (
          <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem" }}>
            <ModelDetailsPage />
          </div>
        )}

        {activeTab === "audit" && <ModelAuditPage />}

        {activeTab === "evaluation" && (
          <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem" }}>
            <SupportedCasesPage
              cases={supportedCases}
              onSelectCase={(cid) => {
                const found = supportedCases.find((c) => c.case_id === cid);
                if (found) handleSelectDiseaseForPrescription(found);
              }}
            />
          </div>
        )}

        {activeTab === "settings" && (
          <SettingsPage
            isDarkTheme={isDarkTheme}
            onToggleTheme={handleToggleTheme}
            backendOnline={backendOnline}
          />
        )}

        {/* Right Patient Panel (active in workspace view) */}
        {activeTab === "workspace" && (
          <PatientPanel
            currentCase={currentCase}
            onEditPatient={() => setIsEditModalOpen(true)}
            isOpen={patientPanelOpen}
            onClose={() => setPatientPanelOpen(false)}
          />
        )}
      </div>
      )}

      {/* Edit Patient Facts Modal */}
      {isEditModalOpen && currentCase && (
        <EditPatientModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          currentCase={currentCase}
          onSave={handleSavePatientData}
        />
      )}
    </div>
  );
};

export default App;
