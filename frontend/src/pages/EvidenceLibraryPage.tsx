import React, { useState } from "react";
import { uploadEvidenceDocument, searchEvidenceLibrary, askEvidenceQuestion } from "../services/api";
import type { EvidenceChunkMatch, RAGQueryResponse } from "../types";

export const EvidenceLibraryPage: React.FC = () => {
  // Navigation tab state
  const [activeTab, setActiveTab] = useState<"search" | "qa" | "repositories" | "ingest">("search");

  // RAG Search state
  const [searchQuery, setSearchQuery] = useState<string>("Metformin eGFR renal cutoff");
  const [searchDiseaseTag, setSearchDiseaseTag] = useState<string>("");
  const [searchResults, setSearchResults] = useState<EvidenceChunkMatch[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  // RAG Q&A state
  const [qaQuery, setQaQuery] = useState<string>("What is the recommended fluid protocol and NSAID warning in Dengue fever?");
  const [qaDiseaseTag, setQaDiseaseTag] = useState<string>("dengue");
  const [qaResult, setQaResult] = useState<RAGQueryResponse | null>(null);
  const [isAsking, setIsAsking] = useState<boolean>(false);
  const [qaError, setQaError] = useState<string | null>(null);

  // Upload Form state
  const [title, setTitle] = useState<string>("");
  const [organization, setOrganization] = useState<string>("Hospital Clinical Committee");
  const [url, setUrl] = useState<string>("");
  const [diseaseTag, setDiseaseTag] = useState<string>("pneumonia");
  const [content, setContent] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const curatedSources = [
    {
      title: "ICMR Standard Treatment Workflows (STWs) in India",
      org: "Indian Council of Medical Research (ICMR)",
      url: "https://www.icmr.gov.in/standard-treatment-workflows-stws",
      scope: "National evidence-based workflows covering primary, secondary, and tertiary care across 120+ clinical conditions in India.",
      status: "Active & Indexed (13 Guidelines)"
    },
    {
      title: "CDSCO Notifications & Approved Prescribing Information",
      org: "Central Drugs Standard Control Organisation (CDSCO)",
      url: "https://cdsco.gov.in/opencms/opencms/en/Notifications/Prescribing-Information/",
      scope: "Official Government of India drug safety alerts, boxed warnings, renal/hepatic contraindications, and approved new drug listings.",
      status: "Active & Indexed"
    },
    {
      title: "National Tuberculosis Elimination Programme (NTEP) Technical Guidelines",
      org: "Central TB Division, MoHFW India",
      url: "https://tbcindia.gov.in",
      scope: "Weight-banded fixed-dose combinations (HRZE), baseline LFT monitoring, and drug-resistant PMDT expert algorithms.",
      status: "Active & Indexed"
    },
    {
      title: "National Drug Policy on Malaria (NVBDCP)",
      org: "Directorate of NVBDCP, MoHFW India",
      url: "https://nvbdcp.gov.in",
      scope: "Artemisinin-based combination therapies (ACT), species-specific treatment protocols (P. falciparum vs P. vivax), and G6PD deficiency safety gating.",
      status: "Active & Indexed"
    },
    {
      title: "Anemia Mukt Bharat (AMB) National Operational Guidelines",
      org: "Ministry of Health and Family Welfare, Government of India",
      url: "https://anemiamuktbharat.info",
      scope: "Nutritional anemia etiology stratification, prophylactic iron-folic acid, and Ganzoni formula parenteral iron deficit calculations.",
      status: "Active & Indexed"
    }
  ];

  const quickQueries = [
    { label: "Metformin eGFR renal cutoffs", q: "Metformin eGFR renal cutoff contraindication", disease: "type_2_diabetes" },
    { label: "Dengue fluid & NSAID warning", q: "Dengue fluid resuscitation hematocrit NSAID warning", disease: "dengue" },
    { label: "Malaria Vivax & G6PD screening", q: "Plasmodium vivax primaquine radical cure G6PD deficiency", disease: "malaria" },
    { label: "TB Daily FDC weight bands", q: "Tuberculosis daily FDC weight band HRZE isoniazid rifampicin", disease: "tuberculosis" },
    { label: "Hypertension ACEi & ARB contraindication", q: "Hypertension Lisinopril Telmisartan bilateral renal artery pregnancy", disease: "hypertension" }
  ];

  const handleSearch = async (queryText?: string, disease?: string) => {
    const q = queryText !== undefined ? queryText : searchQuery;
    const d = disease !== undefined ? disease : searchDiseaseTag;
    if (!q.trim()) return;

    setIsSearching(true);
    setSearchError(null);
    setHasSearched(true);

    try {
      const res = await searchEvidenceLibrary(q, d || undefined, undefined, 6);
      setSearchResults(res.results || []);
    } catch (err: any) {
      setSearchError(err.message || "Failed to search evidence library.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleQuickSearch = (item: { label: string; q: string; disease: string }) => {
    setSearchQuery(item.q);
    setSearchDiseaseTag(item.disease);
    handleSearch(item.q, item.disease);
  };

  const handleAskQA = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!qaQuery.trim()) return;

    setIsAsking(true);
    setQaError(null);

    try {
      const res = await askEvidenceQuestion(qaQuery, qaDiseaseTag || undefined, undefined, 4);
      setQaResult(res);
    } catch (err: any) {
      setQaError(err.message || "Failed to query clinical guidelines.");
    } finally {
      setIsAsking(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsUploading(true);
    setUploadSuccess(null);
    setUploadError(null);

    try {
      const res = await uploadEvidenceDocument({
        title,
        organization,
        url,
        disease_tag: diseaseTag,
        content
      });
      setUploadSuccess(`Document successfully parsed into ${res.chunks_indexed} clinical chunks and indexed in FAISS + BM25 hybrid library.`);
      setTitle("");
      setContent("");
      setUrl("");
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ flex: 1, padding: "2rem", overflowY: "auto", backgroundColor: "var(--bg-app)" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--hospital-navy)", margin: 0 }}>
              📚 Clinical Evidence Library & RAG Engine
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.25rem", maxWidth: "900px" }}>
              Hybrid Retrieval-Augmented Generation (BM25 lexical ranking + FAISS dense cosine embeddings) over authentic Indian clinical guidelines (ICMR STWs, CDSCO, NVBDCP, NTEP, AMB).
            </p>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <span className="case-badge" style={{ backgroundColor: "#e0f2fe", color: "#0369a1", fontWeight: 600 }}>
              FAISS Index: Active
            </span>
            <span className="case-badge" style={{ backgroundColor: "#dcfce7", color: "#15803d", fontWeight: 600 }}>
              BM25 Index: Active
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: "flex", gap: "0.5rem", marginTop: "1.25rem", borderBottom: "1px solid var(--border-light)", paddingBottom: "0.5rem" }}>
          <button
            onClick={() => setActiveTab("search")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "search" ? "var(--teal-primary)" : "transparent",
              color: activeTab === "search" ? "#fff" : "var(--text-secondary)"
            }}
          >
            🔍 RAG Guideline Search
          </button>
          <button
            onClick={() => setActiveTab("qa")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "qa" ? "var(--teal-primary)" : "transparent",
              color: activeTab === "qa" ? "#fff" : "var(--text-secondary)"
            }}
          >
            💡 Ask Guidelines (RAG QA)
          </button>
          <button
            onClick={() => setActiveTab("repositories")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "repositories" ? "var(--teal-primary)" : "transparent",
              color: activeTab === "repositories" ? "#fff" : "var(--text-secondary)"
            }}
          >
            🏛️ Verified Repositories
          </button>
          <button
            onClick={() => setActiveTab("ingest")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "var(--radius-sm)",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "0.875rem",
              background: activeTab === "ingest" ? "var(--teal-primary)" : "transparent",
              color: activeTab === "ingest" ? "#fff" : "var(--text-secondary)"
            }}
          >
            📤 Ingest New Guideline
          </button>
        </div>
      </div>

      {/* TAB 1: RAG GUIDELINE SEARCH */}
      {activeTab === "search" && (
        <div>
          {/* Search Box */}
          <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.25rem", marginBottom: "1.5rem", boxShadow: "var(--shadow-sm)" }}>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
              <input
                type="text"
                className="form-input"
                style={{ flex: 3, minWidth: "250px" }}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Search clinical guidance, drug dosing, contraindications, renal thresholds..."
              />
              <input
                type="text"
                className="form-input"
                style={{ flex: 1, minWidth: "150px" }}
                value={searchDiseaseTag}
                onChange={(e) => setSearchDiseaseTag(e.target.value)}
                placeholder="Disease tag (optional)"
              />
              <button
                className="clinical-btn-primary"
                onClick={() => handleSearch()}
                disabled={isSearching}
              >
                {isSearching ? "Searching..." : "Retrieve Evidence"}
              </button>
            </div>

            {/* Quick Queries */}
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginRight: "0.5rem" }}>Try clinical queries:</span>
              <div style={{ display: "inline-flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.25rem" }}>
                {quickQueries.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleQuickSearch(item)}
                    style={{
                      background: "var(--bg-subtle, #f1f5f9)",
                      border: "1px solid var(--border-light)",
                      borderRadius: "12px",
                      padding: "2px 8px",
                      fontSize: "0.72rem",
                      cursor: "pointer",
                      color: "var(--hospital-navy)"
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {searchError && (
            <div style={{ background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", marginBottom: "1rem", fontSize: "0.85rem" }}>
              ⚠️ {searchError}
            </div>
          )}

          {/* Results List */}
          {hasSearched && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>
                  Retrieved Guideline Chunks ({searchResults.length})
                </h3>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  Scoring: 0.5 × Dense FAISS + 0.5 × Lexical BM25 + Tag Boost
                </span>
              </div>

              {searchResults.length === 0 ? (
                <div style={{ background: "var(--bg-card)", border: "1px dashed var(--border-light)", padding: "2rem", borderRadius: "var(--radius-md)", textAlign: "center", color: "var(--text-secondary)" }}>
                  No guideline chunks matched this query. Try adjusting keywords or clearing the disease tag.
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                  {searchResults.map((item) => (
                    <div
                      key={item.chunk_id}
                      style={{
                        background: "var(--bg-card)",
                        border: "1px solid var(--border-light)",
                        borderRadius: "var(--radius-md)",
                        padding: "1.25rem",
                        boxShadow: "var(--shadow-sm)"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem" }}>
                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                            <span className="case-badge" style={{ backgroundColor: "#e0e7ff", color: "#3730a3", fontSize: "0.7rem", fontWeight: 600 }}>
                              {item.organization}
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                              {item.section_name} • Pub Year: {item.publication_year}
                            </span>
                          </div>
                          <h4 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--hospital-navy)", margin: "4px 0 2px 0" }}>
                            {item.title}
                          </h4>
                        </div>
                        <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                          <span style={{ background: "#f0fdf4", color: "#166534", border: "1px solid #bbf7d0", padding: "2px 6px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                            Hybrid: {item.hybrid_score}
                          </span>
                          <span style={{ background: "#f8fafc", color: "#475569", border: "1px solid #cbd5e1", padding: "2px 6px", borderRadius: "4px", fontSize: "0.72rem" }}>
                            BM25: {item.bm25_score}
                          </span>
                          <span style={{ background: "#f8fafc", color: "#475569", border: "1px solid #cbd5e1", padding: "2px 6px", borderRadius: "4px", fontSize: "0.72rem" }}>
                            FAISS: {item.dense_score}
                          </span>
                        </div>
                      </div>

                      {/* Snippet text */}
                      <p style={{ fontSize: "0.85rem", color: "var(--text-main)", lineHeight: 1.5, background: "var(--bg-subtle, #f8fafc)", padding: "0.75rem", borderRadius: "var(--radius-sm)", borderLeft: "3px solid var(--teal-primary)", margin: "0.5rem 0" }}>
                        {item.text}
                      </p>

                      {/* Footer tags and link */}
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
                        <div style={{ display: "flex", gap: "0.3rem", flexWrap: "wrap" }}>
                          {item.disease_tags.map((t, idx) => (
                            <span key={idx} style={{ fontSize: "0.68rem", background: "#f1f5f9", color: "#475569", padding: "1px 6px", borderRadius: "10px" }}>
                              🏷️ {t}
                            </span>
                          ))}
                          {item.medicine_tags.map((m, idx) => (
                            <span key={idx} style={{ fontSize: "0.68rem", background: "#fef3c7", color: "#92400e", padding: "1px 6px", borderRadius: "10px" }}>
                              💊 {m}
                            </span>
                          ))}
                        </div>
                        {item.url && (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ fontSize: "0.75rem", color: "var(--teal-primary)", fontWeight: 600, textDecoration: "none" }}
                          >
                            Verify in Official Source ↗
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: RAG Q&A ASSISTANT */}
      {activeTab === "qa" && (
        <div>
          <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.5rem", marginBottom: "1.5rem", boxShadow: "var(--shadow-sm)" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--hospital-navy)", margin: "0 0 0.5rem 0" }}>
              💡 Ask Clinical Guideline Assistant (RAG QA)
            </h3>
            <p style={{ fontSize: "0.825rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
              Submit clinical dosing questions, contraindications, or disease management inquiries. The system retrieves authentic guideline excerpts and synthesizes an evidence-grounded answer citing official passages.
            </p>

            <form onSubmit={handleAskQA} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <div>
                <label className="form-label">Clinical Question / Guideline Query</label>
                <textarea
                  className="form-input"
                  rows={3}
                  value={qaQuery}
                  onChange={(e) => setQaQuery(e.target.value)}
                  placeholder="e.g. What is the target dosage for Metformin in elderly diabetic patients with mild renal impairment?"
                  required
                />
              </div>

              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <input
                  type="text"
                  className="form-input"
                  style={{ maxWidth: "250px" }}
                  value={qaDiseaseTag}
                  onChange={(e) => setQaDiseaseTag(e.target.value)}
                  placeholder="Optional disease tag (e.g. dengue)"
                />
                <button type="submit" className="clinical-btn-primary" disabled={isAsking}>
                  {isAsking ? "Retrieving & Synthesizing..." : "Ask Guideline Engine"}
                </button>
              </div>
            </form>
          </div>

          {qaError && (
            <div style={{ background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", marginBottom: "1rem", fontSize: "0.85rem" }}>
              ⚠️ {qaError}
            </div>
          )}

          {qaResult && (
            <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.5rem", boxShadow: "var(--shadow-sm)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-light)", paddingBottom: "0.75rem", marginBottom: "1rem" }}>
                <h4 style={{ margin: 0, fontSize: "1.05rem", color: "var(--hospital-navy)" }}>
                  Synthesized Guideline Guidance
                </h4>
                <span className="case-badge" style={{ backgroundColor: "#dcfce7", color: "#166534" }}>
                  Evidence Match Confidence: {qaResult.confidence}
                </span>
              </div>

              {/* Formatted Answer */}
              <div style={{ whiteSpace: "pre-wrap", fontSize: "0.875rem", lineHeight: 1.6, color: "var(--text-main)" }}>
                {qaResult.answer}
              </div>

              {/* Grounding Sources */}
              {qaResult.sources && qaResult.sources.length > 0 && (
                <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--border-light)", paddingTop: "1rem" }}>
                  <h5 style={{ margin: "0 0 0.5rem 0", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    Retrieved Guideline Grounding Passages:
                  </h5>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.75rem" }}>
                    {qaResult.sources.map((s, idx) => (
                      <div key={idx} style={{ background: "var(--bg-subtle, #f8fafc)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", padding: "0.75rem", fontSize: "0.78rem" }}>
                        <div style={{ fontWeight: 700, color: "var(--hospital-navy)" }}>{s.title}</div>
                        <div style={{ color: "var(--teal-dark)", fontSize: "0.72rem" }}>{s.organization} ({s.publication_year})</div>
                        <p style={{ marginTop: "4px", color: "var(--text-secondary)", lineHeight: 1.3 }}>
                          "{s.text.slice(0, 150)}..."
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: CURATED REPOSITORIES */}
      {activeTab === "repositories" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
          {curatedSources.map((src, idx) => (
            <div
              key={idx}
              style={{
                background: "var(--bg-card)",
                border: "1px solid var(--border-light)",
                borderRadius: "var(--radius-md)",
                padding: "1.25rem",
                boxShadow: "var(--shadow-sm)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "0.5rem"
              }}
            >
              <div>
                <span className="case-badge" style={{ fontSize: "0.68rem" }}>{src.status}</span>
                <h4 style={{ fontSize: "0.95rem", color: "var(--text-main)", margin: "6px 0 2px 0" }}>{src.title}</h4>
                <div style={{ fontSize: "0.75rem", color: "var(--teal-dark)", fontWeight: 600 }}>{src.org}</div>
                <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "6px", lineHeight: 1.4 }}>
                  {src.scope}
                </p>
              </div>
              <a
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: "0.75rem", color: "var(--teal-primary)", fontWeight: 600, textDecoration: "none", marginTop: "6px" }}
              >
                Access Source Repository ↗
              </a>
            </div>
          ))}
        </div>
      )}

      {/* TAB 4: UPLOAD INSTITUTIONAL GUIDELINES FORM */}
      {activeTab === "ingest" && (
        <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "1.5rem", boxShadow: "var(--shadow-sm)", maxWidth: "800px" }}>
          <div style={{ marginBottom: "1rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--hospital-navy)", margin: 0 }}>
              📤 Ingest New Clinical Practice Guideline
            </h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>
              Add hospital-specific or newly released clinical guidelines. Content will be safely sanitized, chunked, and indexed in the hybrid FAISS + BM25 knowledgebase.
            </p>
          </div>

          {uploadSuccess && (
            <div style={{ background: "var(--badge-pass-bg)", color: "var(--badge-pass-text)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", marginBottom: "1rem", fontSize: "0.85rem" }}>
              ✓ {uploadSuccess}
            </div>
          )}
          {uploadError && (
            <div style={{ background: "var(--badge-fail-bg)", color: "var(--badge-fail-text)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", marginBottom: "1rem", fontSize: "0.85rem" }}>
              ⚠️ {uploadError}
            </div>
          )}

          <form onSubmit={handleUploadSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label className="form-label">Document Title</label>
              <input
                type="text"
                className="form-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. AIIMS Standard Operating Procedure for Adult CAP"
                required
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
              <div>
                <label className="form-label">Publishing Organization</label>
                <input
                  type="text"
                  className="form-input"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  placeholder="e.g. AIIMS New Delhi"
                  required
                />
              </div>
              <div>
                <label className="form-label">Disease Tag</label>
                <input
                  type="text"
                  className="form-input"
                  value={diseaseTag}
                  onChange={(e) => setDiseaseTag(e.target.value)}
                  placeholder="e.g. pneumonia, asthma, sepsis"
                  required
                />
              </div>
            </div>

            <div>
              <label className="form-label">Source URL / DOI Link</label>
              <input
                type="url"
                className="form-input"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://..."
              />
            </div>

            <div>
              <label className="form-label">Clinical Guideline Content (Markdown or Plain Text)</label>
              <textarea
                className="form-input"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={6}
                placeholder="Paste clinical guideline text, dosing recommendations, and renal/hepatic thresholds here..."
                required
              />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button type="submit" className="clinical-btn-primary" disabled={isUploading}>
                {isUploading ? "Chunking & Indexing in FAISS..." : "Parse & Ingest Guideline"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

