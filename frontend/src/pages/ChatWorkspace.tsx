import React, { useState, useRef, useEffect } from "react";
import type {
  ClinicalCase,
  ChatMessage,
  AssessmentResponse,
  EvidenceSource
} from "../types";
import { streamCaseEvents, approveTreatmentPlan, updatePatientData, assessCase } from "../services/api";
import { IndianMedicineModal } from "../components/IndianMedicineModal";
import { CitationModal } from "../components/CitationModal";
import { ExportDraftModal } from "../components/ExportDraftModal";
import { ClinicalIntakeCard } from "../components/ClinicalIntakeCard";
import { ClinicalVisualAnalytics } from "../components/ClinicalVisualAnalytics";
import { PrescriptionRecommendationCard } from "../components/PrescriptionRecommendationCard";

interface ChatWorkspaceProps {
  currentCase: ClinicalCase | null;
  onRefreshCase: () => void;
  onOpenEditModal: () => void;
  onTogglePatientPanel: () => void;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  currentCase,
  onRefreshCase,
  onOpenEditModal,
  onTogglePatientPanel
}) => {
  const [workspaceView, setWorkspaceView] = useState<"prescription" | "chat" | "all">("prescription");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [isAssessing, setIsAssessing] = useState<boolean>(false);
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const [streamedText, setStreamedText] = useState<string>("");
  const [streamedAssessment, setStreamedAssessment] = useState<AssessmentResponse | null>(null);
  const [currentAssessment, setCurrentAssessment] = useState<AssessmentResponse | null>(null);

  // Modals state
  const [selectedGenericForBrands, setSelectedGenericForBrands] = useState<{ generic: string; strength?: string; route?: string } | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<EvidenceSource | null>(null);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);
  const [approvalNotice, setApprovalNotice] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load existing messages and auto-load assessment when currentCase changes
  useEffect(() => {
    if (currentCase?.messages) {
      setMessages(currentCase.messages);
      // If there's an existing structured card in the latest assistant message, use it
      const lastAsstMsg = [...currentCase.messages].reverse().find(m => m.role === "assistant" && m.structured_cards);
      if (lastAsstMsg?.structured_cards) {
        setCurrentAssessment(lastAsstMsg.structured_cards);
      }
    } else {
      setMessages([]);
    }
    setStreamedText("");
    setStreamedAssessment(null);
    setCurrentStatus(null);

    // Fetch fresh assessment for current patient state
    if (currentCase?.case_id) {
      assessCase(currentCase.case_id)
        .then((asmt) => setCurrentAssessment(asmt))
        .catch((err) => console.log("Assessment fetch:", err));
    }
  }, [currentCase?.case_id, currentCase?.patient_version]);

  useEffect(() => {
    if (workspaceView !== "prescription") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, streamedText, currentStatus, workspaceView]);

  // Handle Save and Assess from ClinicalIntakeCard
  const handleSaveAndAssess = async (updatedPatient: Record<string, any>) => {
    if (!currentCase) return;
    setIsAssessing(true);
    try {
      await updatePatientData(currentCase.case_id, updatedPatient);
      const asmt = await assessCase(currentCase.case_id);
      setCurrentAssessment(asmt);
      onRefreshCase();
    } catch (err) {
      console.error("Failed to run assessment:", err);
    } finally {
      setIsAssessing(false);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || !currentCase || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setIsStreaming(true);
    setCurrentStatus("Initializing clinical assessment pipeline...");
    setStreamedText("");
    setStreamedAssessment(null);

    let incomingText = "";
    let incomingAssessment: AssessmentResponse | null = null;

    await streamCaseEvents(currentCase.case_id, text, {
      onStatus: (status) => {
        setCurrentStatus(status);
      },
      onPatientUpdate: (confirmations) => {
        console.log("Extracted patient updates:", confirmations);
        onRefreshCase();
      },
      onAssessment: (asmt) => {
        incomingAssessment = asmt;
        setStreamedAssessment(asmt);
        setCurrentAssessment(asmt);
      },
      onToken: (token) => {
        incomingText += token;
        setStreamedText(incomingText);
      },
      onDone: (msgId) => {
        setIsStreaming(false);
        setCurrentStatus(null);
        const asstMsg: ChatMessage = {
          id: msgId,
          role: "assistant",
          content: incomingText,
          structured_cards: incomingAssessment,
          citations: incomingAssessment?.sources || [],
          created_at: new Date().toISOString()
        };
        setMessages((prev) => [...prev, asstMsg]);
        setStreamedText("");
        setStreamedAssessment(null);
        if (incomingAssessment) {
          setCurrentAssessment(incomingAssessment);
        }
        onRefreshCase();
      },
      onError: (err) => {
        setIsStreaming(false);
        setCurrentStatus(null);
        console.error("Stream failed:", err);
      }
    });
  };

  const handleApprovePlan = async () => {
    if (!currentCase) return;
    try {
      const res = await approveTreatmentPlan(currentCase.case_id);
      setApprovalNotice(res.notice);
      onRefreshCase();
      setTimeout(() => setApprovalNotice(null), 8000);
    } catch (err: any) {
      alert(`Approval failed: ${err.message}`);
    }
  };

  const starterVignettes = [
    {
      tag: "Type 2 Diabetes",
      text: "58yo male with Type 2 Diabetes, eGFR 42 mL/min/1.73m2, blood glucose 188 mg/dL. Prescribe guideline glycemic therapy."
    },
    {
      tag: "Hypertension",
      text: "64yo female with Essential Hypertension, BP 155/95 mmHg, Potassium 5.8 mEq/L. Evaluate antihypertensive safety."
    },
    {
      tag: "Dengue Fever",
      text: "28yo female with acute Dengue fever, platelet count 45,000 /mcL. Need fever control and fluid resuscitation protocol."
    },
    {
      tag: "Malaria (Falciparum)",
      text: "34yo male with confirmed Plasmodium falciparum malaria in primary care. Weight 62 kg, G6PD normal."
    },
    {
      tag: "Tuberculosis",
      text: "42yo male with newly diagnosed drug-sensitive pulmonary tuberculosis, weight 54 kg, baseline LFTs normal."
    },
    {
      tag: "GERD / Acid Reflux",
      text: "45yo male with severe retrosternal burning, acid regurgitation for 3 weeks, no dysphagia or weight loss. Prescribe standard PPI therapy."
    },
    {
      tag: "Urinary Tract Infection",
      text: "32yo female with acute uncomplicated cystitis, dysuria, frequency, no fever or flank pain, not pregnant. Prescribe antimicrobial therapy."
    },
    {
      tag: "Dyslipidemia",
      text: "52yo male with primary hypercholesterolemia, LDL-C 168 mg/dL, normal LFTs. Initiate statin therapy."
    },
    {
      tag: "Hypothyroidism",
      text: "38yo female with primary overt hypothyroidism, TSH 14.2 mIU/L, weight 60 kg, no cardiac history. Calculate levothyroxine dose."
    },
    {
      tag: "Acute Gastroenteritis",
      text: "26yo male with watery diarrhea for 24 hours, mild dehydration, no fever or hematochezia. Prescribe rehydration and symptomatic therapy."
    },
    {
      tag: "Migraine",
      text: "30yo female with acute unilateral pulsating headache, nausea, photophobia, not pregnant. Prescribe acute abortive therapy."
    },
    {
      tag: "Nutritional Deficiency",
      text: "8yo child with manifest Scurvy, petechiae, and swollen bleeding gums. Propose therapeutic ascorbic acid replacement."
    }
  ];

  if (!currentCase) {
    return (
      <div className="central-workspace" style={{ alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "var(--text-muted)" }}>Select or create a patient case to begin.</p>
      </div>
    );
  }

  return (
    <div className="central-workspace">
      {/* Top Bar with Mode Switcher */}
      <div className="workspace-top-bar">
        <div className="workspace-case-info">
          <span className="case-title-text">{currentCase.diagnosis_name || currentCase.title}</span>
          <span className="case-badge">Patient v{currentCase.patient_version}</span>
          {currentCase.approved_by_doctor && (
            <span className="status-badge proposal-available" style={{ fontSize: "0.75rem" }}>
              ✓ Plan Approved
            </span>
          )}
        </div>

        {/* View Mode Switcher */}
        <div className="workspace-mode-switch">
          <button
            type="button"
            className={`mode-tab-btn ${workspaceView === "prescription" ? "active" : ""}`}
            onClick={() => setWorkspaceView("prescription")}
            title="Clinician Intake, Visual Analytics & Dosage Recommendation"
          >
            📋 Prescription Pad
          </button>
          <button
            type="button"
            className={`mode-tab-btn ${workspaceView === "chat" ? "active" : ""}`}
            onClick={() => setWorkspaceView("chat")}
            title="Interactive Clinical Consultation Chat"
          >
            💬 Consultation Chat
          </button>
          <button
            type="button"
            className={`mode-tab-btn ${workspaceView === "all" ? "active" : ""}`}
            onClick={() => setWorkspaceView("all")}
            title="Full Unified View"
          >
            🔄 Unified
          </button>
        </div>

        <div className="workspace-actions">
          <button
            onClick={() => setIsExportOpen(true)}
            className="clinical-btn-secondary"
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem" }}
            title="Export printable draft assessment report"
          >
            📄 Export Draft
          </button>
          <button
            onClick={handleApprovePlan}
            className="clinical-btn-primary"
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem" }}
            title="Officially record clinician review without auto-prescribing"
          >
            ✓ Approve
          </button>
          <button
            onClick={onTogglePatientPanel}
            className="clinical-btn-secondary"
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem" }}
            title="Toggle patient context panel"
          >
            👤 Patient Panel
          </button>
        </div>
      </div>

      {/* Approval Banner */}
      {approvalNotice && (
        <div style={{ background: "var(--badge-pass-bg)", borderBottom: "1px solid var(--badge-pass-border)", padding: "0.5rem 1.5rem", color: "var(--badge-pass-text)", fontSize: "0.825rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>🛡️ {approvalNotice}</span>
          <button onClick={() => setApprovalNotice(null)} style={{ background: "transparent", border: "none", color: "inherit", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {/* ==================== PRESCRIPTION PAD WORKFLOW ==================== */}
      {(workspaceView === "prescription" || workspaceView === "all") && (
        <div className="prescription-mode-container" style={{ overflowY: "auto", flex: 1 }}>
          {/* STEP 1: Clinical Intake Card */}
          <ClinicalIntakeCard
            currentCase={currentCase}
            onSaveAndAssess={handleSaveAndAssess}
            isLoading={isAssessing}
          />

          {/* VISUAL ANALYTICS: Graphs & Safety Gauges */}
          <ClinicalVisualAnalytics
            currentCase={currentCase}
            assessment={currentAssessment}
          />

          {/* STEP 2: Prescription Recommendation Card */}
          <PrescriptionRecommendationCard
            currentCase={currentCase}
            assessment={currentAssessment}
            onApprovePlan={handleApprovePlan}
            onExportPrescription={() => setIsExportOpen(true)}
            onOpenBrandModal={setSelectedGenericForBrands}
            onOpenCitationModal={setSelectedCitation}
            onOpenChat={() => setWorkspaceView("chat")}
          />
        </div>
      )}

      {/* ==================== CONSULTATION CHAT WORKFLOW ==================== */}
      {(workspaceView === "chat" || workspaceView === "all") && (
        <div className="chat-container-wrapper" style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
          {/* Messages Scroll Area */}
          <div className="chat-messages-viewport">
            {messages.length === 0 && !isStreaming && (
              <div className="chat-welcome-box">
                <div className="chat-welcome-title">Clinical Consultation & Guidance</div>
                <div className="chat-welcome-subtitle">
                  Ask clinical questions, review verified guideline evidence, or choose a clinical vignette below.
                </div>
                <div className="starter-prompts-grid">
                  {starterVignettes.map((v, idx) => (
                    <div key={idx} className="starter-prompt-card" onClick={() => handleSend(v.text)}>
                      <div className="starter-prompt-tag">{v.tag}</div>
                      <div className="starter-prompt-text">{v.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message-row ${msg.role}`}>
                <div className={`chat-avatar ${msg.role}`}>
                  {msg.role === "user" ? "👨‍⚕️" : "💊"}
                </div>
                <div className={`chat-bubble ${msg.role}`}>
                  <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5, fontSize: "0.925rem" }}>
                    {msg.content}
                  </div>

                  {/* Render Structured Assessment Cards */}
                  {msg.structured_cards && (
                    <div className="assessment-card-box" style={{ marginTop: "1rem" }}>
                      <div className="assessment-card-header">
                        <div>
                          <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--teal-primary)", fontWeight: 700 }}>
                            Clinical Protocol Evaluation
                          </div>
                          <h3 style={{ margin: "2px 0 0 0", fontSize: "1.1rem", color: "var(--hospital-navy)" }}>
                            {msg.structured_cards.diagnosis_name}
                          </h3>
                        </div>
                        <span className={`status-badge ${msg.structured_cards.status.toLowerCase()}`}>
                          {msg.structured_cards.status.replace(/_/g, " ")}
                        </span>
                      </div>

                      {/* Proposals */}
                      <div style={{ marginBottom: "1rem" }}>
                        <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--hospital-navy)", margin: "0 0 0.5rem 0", fontWeight: 700 }}>
                          Proposed Treatments & Doses ({msg.structured_cards.proposals.length})
                        </h4>
                        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                          {msg.structured_cards.proposals.map((prop, idx) => (
                            <div key={idx} style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", padding: "0.85rem", position: "relative" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                                <div>
                                  <span style={{ fontSize: "1rem", fontWeight: 700, color: "var(--hospital-navy)" }}>
                                    {prop.generic_name}
                                  </span>
                                  {prop.suggested_brand && (
                                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginLeft: "8px" }}>
                                      ({prop.suggested_brand})
                                    </span>
                                  )}
                                </div>
                                <span className={`dose-badge ${prop.dose_status.toLowerCase()}`}>
                                  {prop.dose_status.replace(/_/g, " ")}
                                </span>
                              </div>

                              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text-main)", marginBottom: "0.5rem" }}>
                                <span style={{ background: "var(--bg-subtle)", padding: "2px 8px", borderRadius: "4px" }}>
                                  <strong>Dose:</strong> {prop.dose_display ? `${prop.dose_display} ${prop.unit || ""}` : "Withheld"}
                                </span>
                                {prop.route && (
                                  <span style={{ background: "var(--bg-subtle)", padding: "2px 8px", borderRadius: "4px" }}>
                                    <strong>Route:</strong> {prop.route}
                                  </span>
                                )}
                                {prop.frequency && (
                                  <span style={{ background: "var(--bg-subtle)", padding: "2px 8px", borderRadius: "4px" }}>
                                    <strong>Freq:</strong> {prop.frequency}
                                  </span>
                                )}
                              </div>

                              {prop.instructions && (
                                <div style={{ fontSize: "0.8rem", color: "var(--hospital-navy)", background: "rgba(13, 148, 136, 0.08)", border: "1px solid rgba(13, 148, 136, 0.2)", padding: "6px 10px", borderRadius: "4px", marginTop: "0.5rem" }}>
                                  ⏱️ <strong>Administration Instructions:</strong> {prop.instructions}
                                </div>
                              )}

                              <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.45, marginTop: "0.5rem" }}>
                                <strong>Clinical Rationale:</strong> {prop.rationale}
                              </div>

                              {/* Matching Indian Medicines Button */}
                              <div style={{ marginTop: "0.6rem", display: "flex", justifyContent: "flex-end" }}>
                                <button
                                  onClick={() => setSelectedGenericForBrands({ generic: prop.generic_name, strength: prop.dose_display || undefined, route: prop.route || undefined })}
                                  className="clinical-btn-secondary"
                                  style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem" }}
                                >
                                  💊 Find Matching Indian Brands ↗
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Safety Checks */}
                      <div>
                        <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--hospital-navy)", margin: "0 0 0.5rem 0", fontWeight: 700 }}>
                          Multi-Tier Safety Gating ({msg.structured_cards.safety_checks.length} Checks)
                        </h4>
                        <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                          {msg.structured_cards.safety_checks.map((chk, idx) => (
                            <div key={idx} style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", padding: "0.5rem 0.75rem", background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", fontSize: "0.825rem" }}>
                              <div>
                                <strong>{chk.check_name}:</strong> {chk.findings}
                              </div>
                              <span className={`safety-badge ${chk.status.toLowerCase()}`}>
                                {chk.status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Live Streaming Response Bubble */}
            {isStreaming && (
              <div className="chat-message-row assistant">
                <div className="chat-avatar assistant">💊</div>
                <div className="chat-bubble assistant">
                  {currentStatus && (
                    <div className="processing-status-pill">
                      <span>⏳</span>
                      <span>{currentStatus}</span>
                    </div>
                  )}
                  {streamedAssessment && (
                    <div style={{ fontSize: "0.825rem", color: "var(--teal-primary)", marginBottom: "0.5rem", fontWeight: 600 }}>
                      Evaluating indication: {streamedAssessment.diagnosis_name} (Status: {streamedAssessment.status})
                    </div>
                  )}
                  {streamedText && (
                    <div style={{ whiteSpace: "pre-wrap", fontSize: "0.925rem" }}>
                      {streamedText}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Sticky Multiline Composer */}
          <div className="workspace-composer-area">
            <div className="composer-box">
              <textarea
                ref={textareaRef}
                className="composer-textarea"
                placeholder="Type clinical consultation or guideline queries... (e.g. 'What is the KDIGO renal threshold for SGLT2i?')"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={2}
                disabled={isStreaming}
              />
              <div className="composer-toolbar">
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    type="button"
                    onClick={onOpenEditModal}
                    className="clinical-btn-secondary"
                    style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}
                    title="Open structured patient parameters modal"
                  >
                    📋 Patient Modal
                  </button>
                </div>
                <button
                  onClick={() => handleSend()}
                  className="composer-btn-send"
                  disabled={!inputText.trim() || isStreaming}
                  title="Send to clinical decision engine"
                >
                  {isStreaming ? "⏳" : "➤"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      {selectedGenericForBrands && (
        <IndianMedicineModal
          isOpen={true}
          onClose={() => setSelectedGenericForBrands(null)}
          genericName={selectedGenericForBrands.generic}
          desiredStrength={selectedGenericForBrands.strength}
          desiredRoute={selectedGenericForBrands.route}
        />
      )}

      {selectedCitation && (
        <CitationModal
          isOpen={true}
          onClose={() => setSelectedCitation(null)}
          source={selectedCitation}
        />
      )}

      {isExportOpen && currentCase && (
        <ExportDraftModal
          isOpen={true}
          onClose={() => setIsExportOpen(false)}
          caseId={currentCase.case_id}
        />
      )}
    </div>
  );
};

export default ChatWorkspace;
