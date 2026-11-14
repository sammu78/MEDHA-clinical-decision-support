import os
import re
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Generator, Tuple
from datetime import datetime

from app.database.db import get_db_connection
from app.schemas.clinical import (
    PatientAssessmentRequest,
    LabMeasurement,
    AssessmentResponse,
    SafetyCheckResult,
    DoseProposal,
    EvidenceSource
)
from app.evidence.disease_catalogue import get_disease_entry, get_all_diseases, DISEASE_CATALOGUE
from app.evidence.retriever import hybrid_retriever
from app.safety.checker import SafetyEngine
from app.explanations.generator import generate_decision_support
from app.services.indian_medicines_service import indian_medicines_catalogue
from app.models.predictor import predictor

def extract_patient_facts_from_text(text: str, current_patient: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Extracts clinical patient parameters from free-text doctor messages.
    Returns:
        - updated_patient: Dict containing merged patient facts
        - extracted_summaries: List of human-readable confirmations
    """
    updated = dict(current_patient)
    if "labs" not in updated:
        updated["labs"] = {}
    if "allergies" not in updated:
        updated["allergies"] = []
    if "current_medications" not in updated:
        updated["current_medications"] = []
    if "existing_conditions" not in updated:
        updated["existing_conditions"] = []

    confirmations = []
    text_lower = text.lower()

    # 1. Age extraction
    age_match = re.search(r"\b(\d{1,3})\s*(?:yo|y/o|year[s]?\s*old|yrs?\s*old|age[d]?\s*(\d{1,3}))\b", text_lower)
    if age_match:
        age_val = int(age_match.group(1) or age_match.group(2))
        if 0 < age_val <= 125:
            updated["age"] = age_val
            confirmations.append(f"Age: {age_val} years")

    # 2. Gender extraction
    if re.search(r"\b(male|gentleman|man|boy)\b", text_lower):
        updated["gender"] = "M"
        confirmations.append("Gender: Male")
    elif re.search(r"\b(female|woman|lady|girl)\b", text_lower):
        updated["gender"] = "F"
        confirmations.append("Gender: Female")

    # 3. Weight extraction
    wt_match = re.search(r"\b(?:weight|wt|weighs|w\.)\s*[:=]?\s*(\d{1,3}(?:\.\d+)?)\s*(?:kg|kilos)?\b|\b(\d{2,3}(?:\.\d+)?)\s*kg\b", text_lower)
    if wt_match:
        wt_val = float(wt_match.group(1) or wt_match.group(2))
        if 2.0 <= wt_val <= 300.0:
            updated["weight_kg"] = wt_val
            confirmations.append(f"Weight: {wt_val} kg")

    # 4. Disease / Diagnosis mapping
    for dis_id, entry in DISEASE_CATALOGUE.items():
        name_clean = entry.disease_name.lower()
        key_words = [dis_id.replace("_", " ")]
        if "diabetes" in dis_id:
            key_words.extend(["diabetes", "t2d", "type 2 diabetes", "t2dm"])
        elif "hypertension" in dis_id:
            key_words.extend(["hypertension", "htn", "high blood pressure", "high bp"])
        elif "pneumonia" in dis_id:
            key_words.extend(["pneumonia", "cap", "hap"])
        elif "dengue" in dis_id:
            key_words.extend(["dengue", "dengue fever", "dhf"])
        elif "malaria" in dis_id:
            key_words.extend(["malaria", "falciparum", "vivax"])
        elif "tuberculosis" in dis_id:
            key_words.extend(["tuberculosis", "tb", "pulmonary tb"])
        elif "typhoid" in dis_id:
            key_words.extend(["typhoid", "enteric fever"])
        elif "cholera" in dis_id:
            key_words.extend(["cholera", "rice water"])
        elif "scurvy" in dis_id:
            key_words.extend(["scurvy", "vitamin c deficiency"])
        elif "rickets" in dis_id:
            key_words.extend(["rickets", "vitamin d deficiency"])
        elif "beriberi" in dis_id:
            key_words.extend(["beriberi", "thiamine deficiency", "wet beriberi", "dry beriberi"])
        elif "night_blindness" in dis_id:
            key_words.extend(["night blindness", "nyctalopia", "vitamin a deficiency", "xerophthalmia"])
        elif "anaemia" in dis_id:
            key_words.extend(["anaemia", "anemia", "iron deficiency anemia", "low hemoglobin"])

        if any(re.search(r"\b" + re.escape(kw) + r"\b", text_lower) for kw in key_words):
            updated["diagnosis_id"] = dis_id
            updated["diagnosis_name"] = entry.disease_name
            confirmations.append(f"Diagnosis: {entry.disease_name}")
            break

    # 5. Laboratory measurements
    # Creatinine
    cr_match = re.search(r"\b(?:creatinine|cr|scr)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?\b", text_lower)
    if cr_match:
        val = float(cr_match.group(1))
        updated["labs"]["creatinine"] = {"name": "Serum Creatinine", "value": val, "unit": "mg/dL"}
        confirmations.append(f"Serum Creatinine: {val} mg/dL")

    # eGFR
    egfr_match = re.search(r"\b(?:egfr|gfr)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:ml/min)?\b", text_lower)
    if egfr_match:
        val = float(egfr_match.group(1))
        updated["labs"]["egfr"] = {"name": "eGFR", "value": val, "unit": "mL/min/1.73m2"}
        confirmations.append(f"eGFR: {val} mL/min/1.73m2")

    # Glucose
    glu_match = re.search(r"\b(?:glucose|blood sugar|rbs|fbs|ppbs)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?\b", text_lower)
    if glu_match:
        val = float(glu_match.group(1))
        updated["labs"]["glucose"] = {"name": "Blood Glucose", "value": val, "unit": "mg/dL"}
        confirmations.append(f"Blood Glucose: {val} mg/dL")

    # Potassium
    k_match = re.search(r"\b(?:potassium|k\+?)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:meq/l|mmol/l)?\b", text_lower)
    if k_match:
        val = float(k_match.group(1))
        updated["labs"]["potassium"] = {"name": "Serum Potassium", "value": val, "unit": "mEq/L"}
        confirmations.append(f"Serum Potassium: {val} mEq/L")

    # Hemoglobin
    hb_match = re.search(r"\b(?:hemoglobin|hb)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:g/dl)?\b", text_lower)
    if hb_match:
        val = float(hb_match.group(1))
        updated["labs"]["hemoglobin"] = {"name": "Hemoglobin", "value": val, "unit": "g/dL"}
        confirmations.append(f"Hemoglobin: {val} g/dL")

    # Platelets
    plt_match = re.search(r"\b(?:platelet[s]?|plt)\s*[:=]?\s*(\d+(?:,\d+)?|\d+k?)\s*(?:/mc[l]|/cumm)?\b", text_lower)
    if plt_match:
        raw_val = plt_match.group(1).replace(",", "")
        val = float(raw_val.replace("k", "000")) if "k" in raw_val else float(raw_val)
        updated["labs"]["platelet"] = {"name": "Platelet Count", "value": val, "unit": "/mcL"}
        confirmations.append(f"Platelet Count: {val} /mcL")

    # Blood Pressure
    bp_match = re.search(r"\b(?:bp|blood pressure)\s*[:=]?\s*(\d{2,3})\s*/\s*(\d{2,3})\b", text_lower)
    if bp_match:
        sbp = float(bp_match.group(1))
        dbp = float(bp_match.group(2))
        updated["labs"]["systolic_bp"] = {"name": "Systolic BP", "value": sbp, "unit": "mmHg"}
        updated["labs"]["diastolic_bp"] = {"name": "Diastolic BP", "value": dbp, "unit": "mmHg"}
        confirmations.append(f"Blood Pressure: {int(sbp)}/{int(dbp)} mmHg")

    # Allergies
    if "no allergies" in text_lower or "nkda" in text_lower or "nil allergies" in text_lower or "allergies: none" in text_lower:
        updated["allergies"] = []
        confirmations.append("Allergies: None confirmed (NKDA)")
    else:
        al_match = re.search(r"\ballerg(?:ic to|ies?[:=]?)\s*([a-zA-Z0-9,\s]+?)(?:\.|\n|$)", text_lower)
        if al_match:
            al_items = [a.strip() for a in al_match.group(1).split(",") if a.strip() and a.strip() not in ["none", "nil", "no"]]
            if al_items:
                updated["allergies"] = list(set(updated["allergies"] + al_items))
                confirmations.append(f"Allergies updated: {', '.join(al_items)}")

    # Medications
    med_match = re.search(r"\b(?:on|taking|medications?[:=]?|meds[:=]?)\s*([a-zA-Z0-9,\s]+?)(?:\.|\n|$)", text_lower)
    if med_match:
        m_items = [m.strip() for m in med_match.group(1).split(",") if len(m.strip()) > 3]
        if m_items:
            updated["current_medications"] = list(set(updated["current_medications"] + m_items))
            confirmations.append(f"Current Medications: {', '.join(m_items)}")

    return updated, confirmations

class ClinicalChatService:
    @staticmethod
    def get_or_create_case(case_id: Optional[str] = None, doctor_id: str = "dr_session_default") -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        if case_id:
            cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
            row = cursor.fetchone()
            if row:
                conn.close()
                return {
                    "case_id": row["case_id"],
                    "doctor_id": row["doctor_id"],
                    "title": row["title"],
                    "diagnosis_id": row["diagnosis_id"],
                    "diagnosis_name": row["diagnosis_name"],
                    "patient_data": json.loads(row["patient_data"]),
                    "patient_version": row["patient_version"],
                    "status": row["status"],
                    "approved_by_doctor": bool(row["approved_by_doctor"]),
                    "approved_at": row["approved_at"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }

        # Create new case
        new_id = case_id or f"case_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow().isoformat()
        initial_patient = {
            "age": 55,
            "weight_kg": 72.0,
            "gender": "M",
            "diagnosis_id": "type_2_diabetes",
            "diagnosis_name": "Type 2 Diabetes Mellitus",
            "allergies": [],
            "current_medications": [],
            "existing_conditions": [],
            "labs": {
                "glucose": {"name": "Blood Glucose", "value": 178, "unit": "mg/dL"},
                "creatinine": {"name": "Serum Creatinine", "value": 1.1, "unit": "mg/dL"},
                "potassium": {"name": "Serum Potassium", "value": 4.3, "unit": "mEq/L"}
            }
        }
        cursor.execute("""
            INSERT INTO cases (case_id, doctor_id, title, diagnosis_id, diagnosis_name, patient_data, patient_version, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, doctor_id, "New Patient Assessment", "type_2_diabetes", "Type 2 Diabetes Mellitus", json.dumps(initial_patient), 1, "ACTIVE", now, now))
        conn.commit()
        conn.close()

        return {
            "case_id": new_id,
            "doctor_id": doctor_id,
            "title": "New Patient Assessment",
            "diagnosis_id": "type_2_diabetes",
            "diagnosis_name": "Type 2 Diabetes Mellitus",
            "patient_data": initial_patient,
            "patient_version": 1,
            "status": "ACTIVE",
            "approved_by_doctor": False,
            "approved_at": None,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def list_cases(doctor_id: str = "dr_session_default") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases ORDER BY updated_at DESC LIMIT 30")
        rows = cursor.fetchall()
        cases = []
        for r in rows:
            cases.append({
                "case_id": r["case_id"],
                "doctor_id": r["doctor_id"],
                "title": r["title"],
                "diagnosis_id": r["diagnosis_id"],
                "diagnosis_name": r["diagnosis_name"],
                "patient_version": r["patient_version"],
                "status": r["status"],
                "approved_by_doctor": bool(r["approved_by_doctor"]),
                "updated_at": r["updated_at"]
            })
        conn.close()
        return cases

    @staticmethod
    def update_patient_data(case_id: str, new_patient_data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Case {case_id} not found.")

        current_ver = row["patient_version"]
        new_ver = current_ver + 1
        now = datetime.utcnow().isoformat()

        diag_id = new_patient_data.get("diagnosis_id", row["diagnosis_id"])
        cov = get_disease_entry(diag_id)
        diag_name = cov.disease_name if cov else new_patient_data.get("diagnosis_name", row["diagnosis_name"])

        cursor.execute("""
            UPDATE cases 
            SET patient_data = ?, patient_version = ?, diagnosis_id = ?, diagnosis_name = ?, updated_at = ?
            WHERE case_id = ?
        """, (json.dumps(new_patient_data), new_ver, diag_id, diag_name, now, case_id))
        conn.commit()
        conn.close()

        return {
            "case_id": case_id,
            "patient_data": new_patient_data,
            "patient_version": new_ver,
            "diagnosis_id": diag_id,
            "diagnosis_name": diag_name,
            "notice": "Patient facts updated. Previous assessments marked outdated; recalculation initiated."
        }

    @staticmethod
    def run_full_clinical_assessment(case_id: str) -> AssessmentResponse:
        case = ClinicalChatService.get_or_create_case(case_id)
        patient_data = case["patient_data"]
        diag_id = patient_data.get("diagnosis_id", case["diagnosis_id"])

        # Format as PatientAssessmentRequest
        labs_objs = {}
        for k, v in patient_data.get("labs", {}).items():
            if isinstance(v, dict):
                labs_objs[k] = LabMeasurement(
                    name=v.get("name", k),
                    value=float(v.get("value", 0.0)),
                    unit=v.get("unit", "")
                )

        req = PatientAssessmentRequest(
            diagnosis_id=diag_id,
            age=patient_data.get("age", 50),
            weight_kg=patient_data.get("weight_kg"),
            gender=patient_data.get("gender"),
            allergies=patient_data.get("allergies", []),
            current_medications=patient_data.get("current_medications", []),
            existing_conditions=patient_data.get("existing_conditions", []),
            labs=labs_objs
        )

        cov_entry = get_disease_entry(diag_id)

        # 1. Multi-tier Safety Evaluation
        safety_checks, missing_info, can_authorize_dose = SafetyEngine.evaluate(req, cov_entry)

        # 2. ML Feature Extraction & Inference
        feat_df = predictor.extract_features(req.age, req.labs)
        predicted_candidates = []
        dose_info = {}

        if cov_entry:
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

        # 3. Decision Support Proposals
        proposals = generate_decision_support(
            request=req,
            case=cov_entry,
            safety_checks=safety_checks,
            missing_info=missing_info,
            can_authorize_dose=can_authorize_dose,
            predicted_candidates=predicted_candidates,
            pred_dose_info=dose_info
        )

        # 4. Status determination
        has_critical_fail = any(c.status == "FAIL" for c in safety_checks)
        is_model_ready = getattr(cov_entry, "is_dose_model_ready", True)
        if not cov_entry:
            status = "UNSUPPORTED_CASE"
        elif has_critical_fail:
            status = "CONTRAINDICATED"
        elif missing_info or not can_authorize_dose or not is_model_ready:
            status = "MORE_INFO_NEEDED"
        else:
            status = "PROPOSAL_AVAILABLE"

        # 5. Hybrid Evidence Retrieval
        retrieved_passages = hybrid_retriever.retrieve(
            query=f"{diag_id} clinical treatment dosage guideline",
            disease_tag=diag_id,
            top_k=3
        )
        sources = [
            EvidenceSource(
                source_id=p["doc_id"],
                title=p["title"],
                organization=p["organization"],
                publication_year=p["publication_year"],
                url=p["url"],
                verified=True,
                review_date=p["review_date"],
                citation=p["citation"]
            )
            for p in retrieved_passages
        ]

        # Clinical Explanation
        diag_name = cov_entry.disease_name if cov_entry else diag_id
        if status == "PROPOSAL_AVAILABLE":
            clinical_exp = (
                f"Candidate regimens for {diag_name} evaluated against verified clinical practice guidelines (ICMR/CDSCO). "
                "Baseline renal clearance and electrolyte stability verified. No critical contraindications identified. "
                "Final clinical selection and prescription remain under direct attending physician authority."
            )
        elif status == "CONTRAINDICATED":
            clinical_exp = (
                f"Active clinical contraindication detected for {diag_name}. "
                "Automated dosing is strictly withheld to prevent patient harm. Immediate bedside evaluation required."
            )
        elif status == "MORE_INFO_NEEDED":
            clinical_exp = (
                f"Assessment incomplete for {diag_name}. Missing essential parameters: {', '.join(missing_info)}. "
                "Exact dose proposals are withheld until verified laboratory values or subtype confirmations are entered."
            )
        else:
            clinical_exp = f"The diagnosis '{diag_id}' requires specific subtype clarification before decision support can be synthesized."

        # Model provenance
        model_prov = {
            "evaluation_engine": "AushadhiDose Decision Support v2.1",
            "safety_rules_version": SafetyEngine.ENGINE_VERSION,
            "patient_context_version": case["patient_version"],
            "dataset_provenance": "MIMIC-IV Demo Cohort (Retrospective) & ICMR Standard Treatment Workflows",
            "candidate_ranking": [c[0] for c in predicted_candidates[:3]] if predicted_candidates else []
        }

        resp = AssessmentResponse(
            status=status,
            diagnosis_id=diag_id,
            diagnosis_name=diag_name,
            eligible_group_match=(cov_entry is not None),
            candidate_medicines=cov_entry.candidate_medicines if cov_entry else [],
            proposals=proposals,
            safety_checks=safety_checks,
            missing_information=missing_info,
            patient_factors_considered={
                "age": req.age,
                "weight_kg": req.weight_kg,
                "gender": req.gender,
                "reported_labs": {k: f"{v.value} {v.unit}" for k, v in req.labs.items()}
            },
            clinical_explanation=clinical_exp,
            model_provenance=model_prov,
            sources=sources,
            disclaimer=(
                "RESEARCH PROTOTYPE ONLY - NOT A MEDICAL DEVICE. Decision support reflects retrospective "
                "benchmark distributions and published clinical practice guidelines (ICMR STWs, CDSCO, WHO). "
                "The attending doctor retains exclusive medical authority over all prescriptions."
            )
        )

        # Store assessment in database
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        asmt_id = f"asmt_{uuid.uuid4().hex[:10]}"
        cursor.execute("""
            INSERT INTO assessments (assessment_id, case_id, patient_version, status, payload_json, approved_by_doctor, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asmt_id, case_id, case["patient_version"], status, resp.model_dump_json(), 0, now))
        conn.commit()
        conn.close()

        # Persist traceable safety decision audit records
        SafetyEngine.log_safety_decision_records(
            case_id=case_id,
            assessment_id=asmt_id,
            checks=safety_checks,
            can_authorize_dose=can_authorize_dose
        )

        return resp

    @staticmethod
    def stream_chat_response(case_id: str, doctor_message: str) -> Generator[str, None, None]:
        """
        Server-Sent Events (SSE) streaming generator yielding real-time processing statuses,
        extracted patient facts, evidence retrieval citations, structured proposal cards,
        and conversational response text.
        """
        # Save user message to database
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        user_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        cursor.execute("""
            INSERT INTO messages (message_id, case_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_msg_id, case_id, "user", doctor_message, now))
        conn.commit()
        conn.close()

        # Step 1: Processing Status Event
        yield f"event: status\ndata: {json.dumps({'status': 'Checking patient information and extracting parameters...'})}\n\n"
        time.sleep(0.15)

        case = ClinicalChatService.get_or_create_case(case_id)
        current_patient = case["patient_data"]
        updated_patient, confirmations = extract_patient_facts_from_text(doctor_message, current_patient)
        
        # If new facts extracted, persist update
        if confirmations:
            ClinicalChatService.update_patient_data(case_id, updated_patient)
            yield f"event: patient_update\ndata: {json.dumps({'confirmations': confirmations, 'patient_data': updated_patient})}\n\n"

        # Step 2: Evidence Retrieval Status Event
        diag_id = updated_patient.get("diagnosis_id", "type_2_diabetes")
        yield f"event: status\ndata: {json.dumps({'status': 'Retrieving clinical evidence from ICMR Standard Treatment Workflows & CDSCO...'})}\n\n"
        time.sleep(0.15)

        # Step 3: Safety Checks Status Event
        yield f"event: status\ndata: {json.dumps({'status': 'Running multi-tier safety rules (renal, hepatic, interactions, allergies)...'})}\n\n"
        time.sleep(0.15)

        # Step 4: Run full clinical assessment
        assessment = ClinicalChatService.run_full_clinical_assessment(case_id)

        # Step 5: Send structured assessment card
        asmt_dict = assessment.model_dump()
        yield f"event: assessment\ndata: {json.dumps(asmt_dict)}\n\n"

        # Step 6: Stream Conversational Explanation
        yield f"event: status\ndata: {json.dumps({'status': 'Synthesizing explainable clinical guidance with citations...'})}\n\n"

        lead_text = f"### Clinical Assessment for {assessment.diagnosis_name}\n\n"
        if assessment.status == "PROPOSAL_AVAILABLE":
            lead_text += (
                f"Based on verified guidance (**ICMR Standard Treatment Workflows** and CDSCO prescribing standards), "
                f"the patient is an eligible candidate for guideline-directed medical therapy. "
                f"Renal function and electrolytes have been evaluated. Below are the verified generic treatment proposals:\n\n"
            )
            for prop in assessment.proposals:
                if prop.dose_display:
                    lead_text += f"- **{prop.candidate_medicine}**: `{prop.dose_display} {prop.unit or ''}` {prop.route or ''} — *{prop.frequency or ''}* ({prop.rationale})\n"
                else:
                    lead_text += f"- **{prop.candidate_medicine}**: *Dose Withheld* — {prop.rationale}\n"
        elif assessment.status == "CONTRAINDICATED":
            lead_text += (
                f"⚠️ **CRITICAL CLINICAL ALERT**: Automated dosing is strictly withheld due to active contraindications. "
                f"Please review safety gate findings immediately before prescribing.\n\n"
            )
        elif assessment.status == "MORE_INFO_NEEDED":
            lead_text += (
                f"📋 **Additional Patient Information Required**: Dosing proposal is withheld pending essential data: "
                f"**{', '.join(assessment.missing_information)}**. Please confirm these laboratory values or subtypes.\n\n"
            )
        # Ground with RAG guideline passage if doctor message has clinical inquiry
        is_question = any(q_word in doctor_message.lower() for q_word in ["what", "how", "can", "is ", "why", "dose", "guideline", "contraindicat", "threshold", "cutoff", "safe", "protocol"])
        if is_question:
            rag_info = hybrid_retriever.rag_answer(doctor_message, disease_tag=diag_id, top_k=2)
            if rag_info.get("sources"):
                lead_text += "\n\n**Relevant Practice Guideline Guidance (RAG):**\n"
                top_p = rag_info["sources"][0]
                excerpt = top_p["text"][:280].strip() + ("..." if len(top_p["text"]) > 280 else "")
                lead_text += f"> *\"{excerpt}\"*\n> — **{top_p['title']}** ({top_p['organization']}, {top_p['publication_year']})\n\n"

        lead_text += "\n*Citations:* " + ", ".join([f"[{s.title}]({s.url})" for s in assessment.sources[:2]])

        # Stream tokens
        chunks = re.split(r"(\s+)", lead_text)
        for chunk in chunks:
            if chunk:
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                time.sleep(0.015)

        # Save assistant message to database
        conn = get_db_connection()
        cursor = conn.cursor()
        asst_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        cursor.execute("""
            INSERT INTO messages (message_id, case_id, role, content, structured_cards, citations, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asst_msg_id, case_id, "assistant", lead_text, json.dumps(asmt_dict), json.dumps([s.model_dump() for s in assessment.sources]), datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

        yield f"event: done\ndata: {json.dumps({'message_id': asst_msg_id, 'status': 'complete'})}\n\n"
