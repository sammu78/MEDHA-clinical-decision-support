import os
import sys
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.evidence.disease_catalogue import DISEASE_CATALOGUE, get_all_diseases, get_disease_entry
from app.services.indian_medicines_service import indian_medicines_catalogue
from app.evidence.retriever import hybrid_retriever
from app.safety.checker import calculate_egfr_ckd_epi_2021, calculate_crcl_cockcroft_gault, SafetyEngine
from app.schemas.clinical import PatientAssessmentRequest, LabMeasurement

client = TestClient(app)

REQUIRED_27_DISEASES = [
    "common_cold", "influenza", "measles", "chickenpox", "dengue",
    "tuberculosis", "typhoid", "cholera", "pneumonia", "diphtheria",
    "malaria", "amoebiasis", "kala_azar", "sleeping_sickness", "ringworm",
    "athletes_foot", "candidiasis", "type_2_diabetes", "essential_hypertension",
    "asthma", "arthritis", "cancer", "scurvy", "rickets", "beriberi",
    "night_blindness", "anaemia"
]

def test_all_27_diseases_present_in_catalogue():
    all_diseases = get_all_diseases()
    disease_ids = [d.disease_id for d in all_diseases]
    
    assert len(all_diseases) >= 27
    for req_d in REQUIRED_27_DISEASES:
        assert req_d in disease_ids, f"Required disease '{req_d}' missing from catalogue!"

def test_broad_diseases_withhold_and_prompt_subtypes():
    broad_diseases = ["cancer", "arthritis", "anaemia", "pneumonia"]
    for d in broad_diseases:
        entry = get_disease_entry(d)
        assert entry is not None
        assert entry.is_dose_model_ready is False
        assert entry.subtype_prompt_guidance is not None
        assert len(entry.subtype_prompt_guidance) > 10

def test_cancer_dose_strictly_withheld():
    payload = {
        "diagnosis_id": "cancer",
        "age": 52,
        "weight_kg": 65.0,
        "labs": {}
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["MORE_INFO_NEEDED", "UNSUPPORTED_CASE"]
    for p in data["proposals"]:
        assert p["dose_display"] is None
        assert "WITHHELD" in p["dose_status"]

def test_dengue_nsaid_safety_and_paracetamol():
    payload = {
        "diagnosis_id": "dengue",
        "age": 30,
        "weight_kg": 70.0,
        "labs": {
            "platelet": {"name": "Platelets", "value": 75000, "unit": "/mcL"}
        }
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check that paracetamol is authorized and has dose
    pcm_prop = next((p for p in data["proposals"] if "Paracetamol" in p["candidate_medicine"]), None)
    assert pcm_prop is not None
    assert pcm_prop["dose_display"] is not None
    
    # Check that NSAIDs are blocked in safety checks
    nsaid_gate = next((c for c in data["safety_checks"] if "Dengue" in c["check_name"]), None)
    assert nsaid_gate is not None
    assert nsaid_gate["status"] == "PASS"

def test_indian_medicines_search():
    results = indian_medicines_catalogue.search(query="Metformin", limit=5)
    assert len(results) > 0
    first = results[0]
    assert "name" in first
    assert "generic_ingredients" in first
    assert "formulation" in first
    assert "route" in first
    assert "source" in first

def test_indian_medicines_matching_no_silent_combinations():
    matches = indian_medicines_catalogue.find_matching_products_for_generic("Metformin", limit=10)
    for m in matches:
        assert m["is_combination"] is False, "Single ingredient match should not return combination product!"

def test_hybrid_evidence_retrieval():
    results = hybrid_retriever.retrieve(query="tuberculosis treatment FDC weight band", disease_tag="tuberculosis", top_k=2)
    assert len(results) >= 1
    assert "NTEP" in results[0]["title"] or "Tuberculosis" in results[0]["title"] or "tuberculosis" in results[0]["disease_tags"]
    assert results[0]["url"] is not None
    assert len(results[0]["citation"]) > 5

def test_clinical_case_lifecycle():
    # 1. Create case
    create_res = client.post("/cases", json={"doctor_id": "dr_test"})
    assert create_res.status_code == 200
    case_data = create_res.json()
    case_id = case_data["case_id"]
    assert case_id.startswith("case_")

    # 2. Update patient facts
    patch_res = client.patch(f"/cases/{case_id}/patient", json={
        "age": 60,
        "weight_kg": 78.0,
        "diagnosis_id": "type_2_diabetes",
        "labs": {
            "glucose": {"name": "Glucose", "value": 160, "unit": "mg/dL"},
            "creatinine": {"name": "Creatinine", "value": 1.0, "unit": "mg/dL"}
        }
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["patient_version"] == 2

    # 3. Assess case
    asmt_res = client.post(f"/cases/{case_id}/assess")
    assert asmt_res.status_code == 200
    asmt = asmt_res.json()
    assert asmt["status"] == "PROPOSAL_AVAILABLE"

    # 4. Approve treatment plan
    appr_res = client.post(f"/cases/{case_id}/approve", json={"notes": "Doctor confirmed clinical plan."})
    assert appr_res.status_code == 200
    assert appr_res.json()["approved"] is True

    # 5. Export draft
    export_res = client.get(f"/cases/{case_id}/export")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["approved_by_doctor"] is True
    assert "dose_proposals" in export_data
    assert "evidence_citations" in export_data

def test_dual_raas_blockade_contraindication():
    payload = {
        "diagnosis_id": "essential_hypertension",
        "age": 62,
        "weight_kg": 75.0,
        "current_medications": ["Lisinopril 10mg PO", "Telmisartan 40mg PO"],
        "labs": {
            "creatinine": {"name": "Creatinine", "value": 1.2, "unit": "mg/dL"},
            "potassium": {"name": "Potassium", "value": 4.5, "unit": "mEq/L"}
        }
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONTRAINDICATED"
    dual_check = next((c for c in data["safety_checks"] if "Dual RAAS" in c["check_name"]), None)
    assert dual_check is not None
    assert dual_check["status"] == "FAIL"

def test_document_upload_and_indexing():
    payload = {
        "doc_id": "test_protocol_01",
        "title": "Hospital Emergency Protocol for Acute Asthma",
        "organization": "Tertiary Care Hospital",
        "url": "https://example-hospital.in/protocols/asthma",
        "disease_tag": "asthma",
        "content": "In acute severe asthma, high flow oxygen to maintain SpO2 93-95% is vital. Nebulized Salbutamol 5mg with Ipratropium 0.5mg should be administered immediately along with oral prednisolone 40mg."
    }
    response = client.post("/documents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["chunks_indexed"] >= 1
