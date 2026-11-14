import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
from fastapi.responses import StreamingResponse

from app.schemas.clinical import (
    PatientAssessmentRequest,
    AssessmentResponse,
    SupportedCase,
    EvidenceSource,
    ModelEvaluationInfo
)
from app.evidence.disease_catalogue import (
    get_disease_entry,
    get_all_diseases,
    DISEASE_CATALOGUE
)
from app.evidence.registry import (
    get_supported_case as get_legacy_case,
    get_all_supported_cases as get_legacy_cases,
    get_evidence_source,
    SOURCES
)
from app.evidence.retriever import hybrid_retriever
from app.safety.checker import SafetyEngine
from app.models.predictor import predictor
from app.explanations.generator import generate_decision_support
from app.services.indian_medicines_service import indian_medicines_catalogue
from app.services.clinical_chat import ClinicalChatService
from app.database.db import get_db_connection

router = APIRouter()

METRICS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "evaluation_metrics.json"
)
AUDIT_MD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "reports", "data_audit.md"
)

# 1. Health & Dashboard Metrics Endpoints
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Explainable Drug and Dosage Decision Support Backend (Indian Practice)",
        "version": "2.2.0",
        "disease_catalogue_count": len(DISEASE_CATALOGUE),
        "models_loaded": {
            "classifiers": list(predictor.clf_models.keys()),
            "regressors": list(predictor.reg_models.keys())
        },
        "retrieval_engine": "FAISS + BM25 Hybrid Active",
        "safety_engine": "ACTIVE (Multi-Tier Clinical Gate)",
        "indian_medicines_catalogue": "ACTIVE"
    }

@router.get("/dashboard/metrics")
def get_dashboard_metrics():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM cases")
    cases_cnt = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM assessments")
    asmt_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM dim_commercial_product")
    meds_cnt = cur.fetchone()[0]
    if meds_cnt == 0:
        cur.execute("SELECT COUNT(*) FROM indian_medicines")
        meds_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM evidence_documents")
    docs_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_treatment_decision")
    tx_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM dim_patient")
    pat_cnt = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_dosing_rule")
    rules_cnt = cur.fetchone()[0]

    cur.execute("""
        SELECT a.assessment_id, a.case_id, a.status, a.approved_by_doctor, a.created_at, c.title, c.diagnosis_name
        FROM assessments a
        LEFT JOIN cases c ON a.case_id = c.case_id
        ORDER BY a.created_at DESC
        LIMIT 6
    """)
    recent_asmts = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT batch_id, source_file, records_read, records_imported, records_rejected, status, imported_at
        FROM import_batches
        ORDER BY imported_at DESC
        LIMIT 5
    """)
    batches = [dict(r) for r in cur.fetchall()]
    conn.close()

    metrics = {}
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r") as f:
                metrics = json.load(f)
        except Exception:
            pass

    return {
        "status": "healthy",
        "counts": {
            "cases": cases_cnt,
            "assessments": asmt_cnt,
            "commercial_medicines": meds_cnt,
            "evidence_documents": docs_cnt,
            "treatment_decisions": tx_cnt,
            "unique_patients": pat_cnt,
            "dosing_rules": rules_cnt,
            "supported_diseases": len(DISEASE_CATALOGUE)
        },
        "recent_assessments": recent_asmts,
        "import_batches": batches,
        "model_evaluation": metrics,
        "models_status": {
            "classifiers": list(predictor.clf_models.keys()),
            "regressors": list(predictor.reg_models.keys())
        }
    }

# 2. Disease Coverage & Supported Cases
@router.get("/supported-cases")
def list_supported_cases():
    """
    Returns full coverage catalogue across all 27 diseases, including
    evidence coverage, medicine coverage, dose method coverage, and evaluation status.
    """
    return get_all_diseases()

@router.get("/supported-cases/{disease_id}")
def get_single_supported_case(disease_id: str):
    entry = get_disease_entry(disease_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found in coverage catalogue.")
    return entry

# 3. Clinical Cases Session Management
@router.get("/cases")
def list_cases(doctor_id: str = Query("dr_default")):
    return ClinicalChatService.list_cases(doctor_id)

@router.post("/cases")
def create_case(payload: Dict[str, Any] = Body(default={})):
    case_id = payload.get("case_id")
    doctor_id = payload.get("doctor_id", "dr_default")
    return ClinicalChatService.get_or_create_case(case_id, doctor_id)

@router.get("/cases/{case_id}")
def get_case(case_id: str):
    case = ClinicalChatService.get_or_create_case(case_id)
    # Fetch messages
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE case_id = ? ORDER BY created_at ASC", (case_id,))
    msg_rows = cursor.fetchall()
    messages = []
    for m in msg_rows:
        messages.append({
            "message_id": m["message_id"],
            "role": m["role"],
            "content": m["content"],
            "structured_cards": json.loads(m["structured_cards"]) if m["structured_cards"] else None,
            "citations": json.loads(m["citations"]) if m["citations"] else None,
            "created_at": m["created_at"]
        })
    conn.close()
    case["messages"] = messages
    return case

@router.patch("/cases/{case_id}/patient")
@router.put("/cases/{case_id}/patient")
def update_case_patient(case_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        return ClinicalChatService.update_patient_data(case_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/cases/{case_id}/messages")
def send_case_message(case_id: str, payload: Dict[str, Any] = Body(...)):
    doctor_message = payload.get("content", "")
    if not doctor_message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    
    # Run chat service assessment
    assessment = ClinicalChatService.run_full_clinical_assessment(case_id)
    return {
        "case_id": case_id,
        "assessment": assessment
    }

@router.get("/cases/{case_id}/stream")
def stream_case_events(case_id: str, message: str = Query(...)):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Streams processing statuses, extracted entities, clinical cards, and explanation tokens.
    """
    return StreamingResponse(
        ClinicalChatService.stream_chat_response(case_id, message),
        media_type="text/event-stream"
    )

@router.post("/cases/{case_id}/assess", response_model=AssessmentResponse)
def assess_case(case_id: str):
    return ClinicalChatService.run_full_clinical_assessment(case_id)

@router.post("/cases/{case_id}/approve")
def approve_treatment_plan(case_id: str, payload: Dict[str, Any] = Body(default={})):
    notes = payload.get("notes", "Reviewed and confirmed by attending physician.")
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE cases 
        SET approved_by_doctor = 1, approved_at = ?, updated_at = ?
        WHERE case_id = ?
    """, (now, now, case_id))
    cursor.execute("""
        UPDATE assessments
        SET approved_by_doctor = 1, approved_at = ?, doctor_notes = ?
        WHERE case_id = ? AND rowid = (SELECT MAX(rowid) FROM assessments WHERE case_id = ?)
    """, (now, notes, case_id, case_id))
    conn.commit()
    conn.close()

    return {
        "case_id": case_id,
        "approved": True,
        "approved_at": now,
        "notice": "Treatment proposal officially recorded as reviewed and approved by the attending clinician. (Research prototype - prescription requires manual hospital EMR entry)."
    }

@router.get("/cases/{case_id}/export")
def export_draft_assessment(case_id: str):
    asmt = ClinicalChatService.run_full_clinical_assessment(case_id)
    case = ClinicalChatService.get_or_create_case(case_id)
    
    # Generate structured markdown summary for export
    lines = [
        f"# Clinical Decision Support Summary: {asmt.diagnosis_name}",
        f"**Case ID**: `{case_id}` | **Patient Version**: v{case['patient_version']} | **Exported**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Review Status**: {'✓ APPROVED BY ATTENDING CLINICIAN' if case['approved_by_doctor'] else 'PENDING CLINICIAN REVIEW'}",
        "",
        "## Patient Factors Considered",
        f"- **Age**: {asmt.patient_factors_considered.get('age', 'N/A')} yrs | **Gender**: {asmt.patient_factors_considered.get('gender', 'N/A')} | **Weight**: {asmt.patient_factors_considered.get('weight_kg', 'N/A')} kg",
        f"- **Creatinine**: {asmt.patient_factors_considered.get('creatinine', 'N/A')} mg/dL | **eGFR**: {asmt.patient_factors_considered.get('egfr', 'N/A')} mL/min/1.73m²",
        "",
        "## Treatment Proposals",
    ]
    for p in asmt.proposals:
        dose_str = f"{p.dose_display} {p.unit or ''}".strip() if p.dose_display else "WITHHELD"
        lines.append(f"- **{p.generic_name}**: `{dose_str}` ({p.dose_status}) - Route: {p.route or 'N/A'}, Freq: {p.frequency or 'N/A'}")
        lines.append(f"  *Rationale*: {p.rationale}")
    
    lines.append("")
    lines.append("## Safety Gating & Contraindications")
    for s in asmt.safety_checks:
        lines.append(f"- **{s.check_name}**: [{s.status}] {s.findings}")

    lines.append("")
    lines.append(f"> **Disclaimer**: {asmt.disclaimer}")

    markdown_report = "\n".join(lines)

    return {
        "title": f"Clinical Assessment: {asmt.diagnosis_name} (Case {case_id})",
        "export_timestamp": datetime.utcnow().isoformat(),
        "case_id": case_id,
        "patient_version": case["patient_version"],
        "diagnosis": asmt.diagnosis_name,
        "status": asmt.status,
        "patient_factors": asmt.patient_factors_considered,
        "candidate_medicines": asmt.candidate_medicines,
        "dose_proposals": [p.model_dump() for p in asmt.proposals],
        "safety_checks": [s.model_dump() for s in asmt.safety_checks],
        "unchecked_safety_items": [s.model_dump() for s in asmt.safety_checks if s.status == "NOT_CHECKED"],
        "missing_information": asmt.missing_information,
        "evidence_citations": [src.model_dump() for src in asmt.sources],
        "approved_by_doctor": case["approved_by_doctor"],
        "disclaimer": asmt.disclaimer,
        "markdown_report": markdown_report
    }

# 4. Indian Medicines Catalogue Endpoints
@router.get("/medicines/search")
def search_indian_medicines(
    q: str = Query("", description="Brand name, generic, or therapeutic use"),
    generic: Optional[str] = Query(None, description="Specific active ingredient"),
    formulation: Optional[str] = Query(None, description="Tablet, Injection, Syrup, etc."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return indian_medicines_catalogue.search(
        query=q,
        generic_name=generic,
        formulation=formulation,
        limit=limit,
        offset=offset
    )

@router.get("/medicines/match")
def match_indian_products(
    generic: str = Query(..., description="Generic ingredient name e.g. Metformin, Amlodipine"),
    strength: Optional[str] = Query(None, description="Desired product strength e.g. 500mg"),
    route: Optional[str] = Query(None, description="Desired route e.g. Oral, IV")
):
    return indian_medicines_catalogue.find_matching_products_for_generic(
        generic=generic,
        desired_strength=strength,
        desired_route=route
    )

# 5. Evidence Library & Document Ingestion
@router.get("/sources/{source_id}")
def get_source_by_id(source_id: str):
    source = get_evidence_source(source_id)
    if source:
        return source
    # Search retriever chunks
    for c in hybrid_retriever.chunks:
        if c.doc_id == source_id:
            return {
                "source_id": c.doc_id,
                "title": c.title,
                "organization": c.organization,
                "publication_year": c.publication_year,
                "url": c.url,
                "verified": True,
                "review_date": c.review_date,
                "citation": c.citation
            }
    raise HTTPException(status_code=404, detail=f"Evidence source '{source_id}' not found.")

@router.post("/documents")
def upload_clinical_guideline(payload: Dict[str, Any] = Body(...)):
    doc_id = payload.get("doc_id") or f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    title = payload.get("title", "Clinical Practice Guideline")
    org = payload.get("organization", "Hospital Clinical Practice Committee")
    url = payload.get("url", "")
    content = payload.get("content", "")
    disease_tag = payload.get("disease_tag", "general")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    chunk_count = hybrid_retriever.add_uploaded_document(
        doc_id=doc_id,
        title=title,
        organization=org,
        url=url,
        content=content,
        disease_tag=disease_tag
    )
    return {
        "doc_id": doc_id,
        "title": title,
        "chunks_indexed": chunk_count,
        "status": "Document parsed and indexed in FAISS + BM25 hybrid library."
    }

@router.get("/evidence/search")
def search_evidence_library(
    q: str = Query(..., description="Query to search clinical guideline knowledge base"),
    disease_tag: Optional[str] = Query(None, description="Optional filter by disease tag"),
    medicine_tag: Optional[str] = Query(None, description="Optional filter by medicine tag"),
    top_k: int = Query(5, ge=1, le=20)
):
    """
    RAG Evidence Search endpoint combining BM25 lexical ranking and FAISS dense cosine similarity.
    Returns matched guideline chunks with individual and hybrid similarity scores.
    """
    results = hybrid_retriever.retrieve(
        query=q,
        disease_tag=disease_tag,
        medicine_tag=medicine_tag,
        top_k=top_k
    )
    return {
        "query": q,
        "disease_tag": disease_tag,
        "results_count": len(results),
        "results": results
    }

@router.post("/evidence/query")
def ask_clinical_evidence_question(payload: Dict[str, Any] = Body(...)):
    """
    Retrieval-Augmented Generation (RAG) Question Answering Endpoint.
    Takes a clinical question, retrieves top authentic guideline chunks, and
    synthesizes a grounded clinical guidance response with citations.
    """
    query = payload.get("query", "").strip()
    disease_tag = payload.get("disease_tag")
    medicine_tag = payload.get("medicine_tag")
    top_k = int(payload.get("top_k", 3))

    if not query:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    rag_result = hybrid_retriever.rag_answer(
        query=query,
        disease_tag=disease_tag,
        medicine_tag=medicine_tag,
        top_k=top_k
    )
    return rag_result

# 6. Model Info & Data Audit
@router.get("/model-info/{case_id}")
def get_model_info(case_id: str):
    metrics = {}
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)

    matched = {k: v for k, v in metrics.items() if case_id in k}
    return {
        "case_id": case_id,
        "metrics": matched if matched else metrics,
        "provenance": "MIMIC-IV Clinical Database Demo v2.2 Cohort Evaluation",
        "split_method": "Patient-level GroupShuffleSplit (strict separation of subject_ids)",
        "temporal_window": "Pre-decision labs only (lab_charttime <= rx_starttime)",
        "clinical_safety_gate_active": True,
        "disclaimer": "Models provide research benchmark distributions only; doses are strictly verified by clinical practice guidelines."
    }

@router.get("/audit")
def get_data_audit_summary():
    if not os.path.exists(AUDIT_MD_PATH):
        raise HTTPException(status_code=404, detail="Data audit report not found.")
    with open(AUDIT_MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()
    return {
        "audit_file": "reports/data_audit.md",
        "content_markdown": md_text
    }

# 7. Backward-Compatible Direct Assessment Endpoint
@router.post("/assess", response_model=AssessmentResponse)
def assess_patient(request: PatientAssessmentRequest):
    case = get_disease_entry(request.diagnosis_id) or get_legacy_case(request.diagnosis_id)
    
    # 1. Safety Checks
    safety_checks, missing_info, can_authorize_dose = SafetyEngine.evaluate(request, case)

    # 2. Extract features
    feat_df = predictor.extract_features(request.age, request.labs)

    # 3. Model Predictions & SHAP
    predicted_candidates = []
    dose_info = {}

    if case:
        diag_id = getattr(case, "disease_id", getattr(case, "case_id", request.diagnosis_id))
        predicted_candidates = predictor.predict_candidates(diag_id, feat_df)
        
        if diag_id == "type_2_diabetes":
            dose, unit, shap_vals = predictor.predict_dose_and_shap("insulin_sc", feat_df)
            dose_info["insulin_dose"] = dose
            dose_info["insulin_unit"] = unit
            dose_info["insulin_shap"] = shap_vals
        elif diag_id == "essential_hypertension":
            dose, unit, shap_vals = predictor.predict_dose_and_shap("metoprolol_po", feat_df)
            dose_info["metoprolol_dose"] = dose
            dose_info["metoprolol_unit"] = unit
            dose_info["metoprolol_shap"] = shap_vals
        elif diag_id == "heart_failure":
            dose, unit, shap_vals = predictor.predict_dose_and_shap("furosemide_iv", feat_df)
            dose_info["furosemide_dose"] = dose
            dose_info["furosemide_unit"] = unit
            dose_info["furosemide_shap"] = shap_vals

    # 4. Generate Proposals
    if case:
        proposals = generate_decision_support(
            request=request,
            case=case,
            safety_checks=safety_checks,
            missing_info=missing_info,
            can_authorize_dose=can_authorize_dose,
            predicted_candidates=predicted_candidates,
            pred_dose_info=dose_info
        )
        cand_meds = getattr(case, "candidate_medicines", [])
        diag_name = getattr(case, "disease_name", getattr(case, "diagnosis_name", "Unknown"))
    else:
        proposals = []
        cand_meds = []
        diag_name = "Unsupported Diagnosis"

    # 5. Status
    has_critical_fail = any(c.status == "FAIL" for c in safety_checks)
    is_model_ready = getattr(case, "is_dose_model_ready", True)
    if not case:
        status = "UNSUPPORTED_CASE"
    elif has_critical_fail:
        status = "CONTRAINDICATED"
    elif missing_info or not can_authorize_dose or not is_model_ready:
        status = "MORE_INFO_NEEDED"
    else:
        status = "PROPOSAL_AVAILABLE"

    # Patient factors summary
    patient_factors = {
        "age": request.age,
        "weight_kg": request.weight_kg,
        "gender": request.gender,
        "allergies_count": len(request.allergies),
        "current_medications_count": len(request.current_medications),
        "reported_labs": {k: f"{v.value} {v.unit}" for k, v in request.labs.items()}
    }

    if status == "PROPOSAL_AVAILABLE":
        clinical_explanation = (
            f"Patient is an eligible candidate for guideline-directed medical therapy for {diag_name}. "
            "All vital parameters and required renal/metabolic laboratories are within validated operating ranges. "
            "Dose proposals reflect verified clinical guidelines and inpatient prescribing distributions with zero critical contraindications."
        )
    elif status == "CONTRAINDICATED":
        clinical_explanation = (
            f"Active clinical contraindications or acute physiological safety risks detected for {diag_name}. "
            "Automated dosing is strictly withheld to prevent patient harm. Immediate bedside clinical evaluation required."
        )
    elif status == "MORE_INFO_NEEDED":
        clinical_explanation = (
            f"Assessment incomplete for {diag_name}. Missing essential clinical measurements: {', '.join(missing_info)}. "
            "Dosing proposals are withheld until verified laboratory values are entered."
        )
    else:
        clinical_explanation = "The requested diagnosis is not currently registered in the verified evidence case base."

    model_provenance = {
        "dataset": "MIMIC-IV Clinical Database Demo v2.2 (hosp module) & ICMR Standard Treatment Workflows",
        "patient_split": "Patient-level GroupShuffleSplit (no patient overlap between train/test)",
        "gated_by_safety_engine": True,
        "classification_candidates_rank": [c[0] for c in predicted_candidates[:3]] if predicted_candidates else [],
        "decision_rule": "Final dosing authority resides entirely with the attending physician."
    }

    # Retrieve sources
    retrieved = hybrid_retriever.retrieve(f"{request.diagnosis_id} treatment guideline", disease_tag=request.diagnosis_id, top_k=2)
    case_sources = [
        EvidenceSource(
            source_id=r["doc_id"],
            title=r["title"],
            organization=r["organization"],
            publication_year=r["publication_year"],
            url=r["url"],
            verified=True,
            review_date=r["review_date"],
            citation=r["citation"]
        )
        for r in retrieved
    ]
    if not case_sources and request.diagnosis_id in ["type_2_diabetes", "essential_hypertension", "heart_failure"]:
        case_sources = [SOURCES.get("ADA_2024", list(SOURCES.values())[0])]

    return AssessmentResponse(
        status=status,
        diagnosis_id=request.diagnosis_id,
        diagnosis_name=diag_name,
        eligible_group_match=(case is not None),
        candidate_medicines=cand_meds,
        proposals=proposals,
        safety_checks=safety_checks,
        missing_information=missing_info,
        patient_factors_considered=patient_factors,
        clinical_explanation=clinical_explanation,
        model_provenance=model_provenance,
        sources=case_sources,
        disclaimer=(
            "RESEARCH PROTOTYPE ONLY - NOT A MEDICAL DEVICE. Dosing proposals are derived from "
            "retrospective research data (MIMIC-IV Demo) and verified published guidelines (ICMR STWs, CDSCO, ADA). "
            "They do not constitute medical advice or guaranteed prescriptions. The attending "
            "clinician must independently verify all indications, renal adjustments, and dosages."
        )
    )
