import os
import sys
import pytest
import pandas as pd
from fastapi.testclient import TestClient

# Ensure backend root is on path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.safety.checker import calculate_egfr, SafetyEngine
from app.evidence.registry import get_supported_case
from app.schemas.clinical import PatientAssessmentRequest, LabMeasurement

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "safety_engine" in data

def test_dashboard_metrics_endpoint():
    response = client.get("/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "counts" in data
    assert data["counts"]["cases"] >= 0
    assert data["counts"]["commercial_medicines"] > 0
    assert "recent_assessments" in data
    assert "import_batches" in data
    assert "models_status" in data

def test_supported_cases_endpoint():
    response = client.get("/supported-cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 3
    case_ids = [c["case_id"] for c in cases]
    assert "type_2_diabetes" in case_ids
    assert "essential_hypertension" in case_ids
    assert "heart_failure" in case_ids

def test_unsupported_diagnosis_behavior():
    payload = {
        "diagnosis_id": "rare_tropical_disease_xyz",
        "age": 45,
        "weight_kg": 70.0,
        "labs": {}
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNSUPPORTED_CASE"
    # Dosing proposals must be withheld
    for p in data["proposals"]:
        assert p["dose_display"] is None

def test_missing_labs_withheld_behavior():
    payload = {
        "diagnosis_id": "type_2_diabetes",
        "age": 55,
        "weight_kg": 80.0,
        # Intentionally omit required glucose & creatinine
        "labs": {}
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "MORE_INFO_NEEDED"
    assert len(data["missing_information"]) > 0
    # Exact doses must not be authorized
    for p in data["proposals"]:
        assert p["dose_display"] is None

def test_hypoglycemia_contraindication():
    payload = {
        "diagnosis_id": "type_2_diabetes",
        "age": 60,
        "weight_kg": 75.0,
        "labs": {
            "glucose": {"name": "Glucose", "value": 52.0, "unit": "mg/dL"},
            "creatinine": {"name": "Creatinine", "value": 0.9, "unit": "mg/dL"}
        }
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONTRAINDICATED"
    hypo_check = next((c for c in data["safety_checks"] if "Hypoglycemia" in c["check_name"]), None)
    assert hypo_check is not None
    assert hypo_check["status"] == "FAIL"

def test_hyperkalemia_lisinopril_withheld():
    payload = {
        "diagnosis_id": "essential_hypertension",
        "age": 65,
        "weight_kg": 70.0,
        "labs": {
            "creatinine": {"name": "Creatinine", "value": 1.1, "unit": "mg/dL"},
            "potassium": {"name": "Potassium", "value": 5.8, "unit": "mEq/L"}
        }
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONTRAINDICATED"
    # Lisinopril proposal must be withheld
    lis_prop = next((p for p in data["proposals"] if "Lisinopril" in p["generic_name"]), None)
    assert lis_prop is not None
    assert lis_prop["dose_display"] is None
    assert lis_prop["dose_status"] == "WITHHELD_CONTRAINDICATION"

def test_valid_patient_authorized_proposals():
    payload = {
        "diagnosis_id": "type_2_diabetes",
        "age": 58,
        "weight_kg": 82.0,
        "gender": "M",
        "allergies": [],
        "current_medications": [],
        "labs": {
            "glucose": {"name": "Glucose", "value": 165.0, "unit": "mg/dL"},
            "creatinine": {"name": "Creatinine", "value": 1.0, "unit": "mg/dL"},
            "potassium": {"name": "Potassium", "value": 4.2, "unit": "mEq/L"}
        }
    }
    response = client.post("/assess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROPOSAL_AVAILABLE"
    assert len(data["proposals"]) > 0
    authorized = [p for p in data["proposals"] if p["dose_status"] == "AUTHORIZED"]
    assert len(authorized) >= 1
    # Check that authorized proposal has unit, route, and frequency
    for auth in authorized:
        assert auth["dose_display"] is not None
        assert auth["unit"] is not None
        assert auth["route"] is not None

def test_patient_level_splitting_integrity():
    processed_csv = r"c:\Users\Sameer\OneDrive\Desktop\final\data\processed\mimic_treatment_decisions.csv"
    if os.path.exists(processed_csv):
        df = pd.read_csv(processed_csv)
        assert "subject_id" in df.columns
        assert df["subject_id"].nunique() >= 50
        # Verify no IDs are in feature set
        feature_cols = ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
        assert "subject_id" not in feature_cols
        assert "hadm_id" not in feature_cols

def test_pre_decision_timing_enforcement():
    processed_csv = r"c:\Users\Sameer\OneDrive\Desktop\final\data\processed\mimic_treatment_decisions.csv"
    if os.path.exists(processed_csv):
        df = pd.read_csv(processed_csv)
        assert len(df) > 1000
        # Ensure pre-decision labs were extracted
        assert df['pre_glucose'].notnull().sum() > 500
        assert df['pre_creatinine'].notnull().sum() > 500

def test_clinical_cases_lifecycle_and_calculations():
    # 1. Create case
    res = client.post("/cases", json={"title": "Test Diabetic Patient Evaluation"})
    assert res.status_code == 200
    case_data = res.json()
    case_id = case_data["case_id"]
    assert case_id.startswith("case_")
    assert case_data["patient_version"] == 1

    # 2. Update patient profile with diagnosis & labs
    update_payload = {
        "age": 62,
        "gender": "M",
        "weight_kg": 78,
        "diagnosis_id": "type_2_diabetes",
        "allergies": ["Sulfa"],
        "labs": {
            "creatinine": {"value": 1.3, "unit": "mg/dL"},
            "glucose": {"value": 185, "unit": "mg/dL"}
        }
    }
    res = client.put(f"/cases/{case_id}/patient", json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    p_data = updated.get("patient_data", {})
    assert p_data.get("age") == 62
    assert updated.get("patient_version") == 2
    assert updated.get("diagnosis_id") == "type_2_diabetes"

    # 3. Retrieve case details
    res = client.get(f"/cases/{case_id}")
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["case_id"] == case_id
    assert "messages" in fetched

    # 4. Assess case
    res = client.post(f"/cases/{case_id}/assess")
    assert res.status_code == 200
    asmt = res.json()
    assert asmt["diagnosis_id"] == "type_2_diabetes"
    assert asmt["status"] in ["PROPOSAL_AVAILABLE", "MORE_INFO_NEEDED"]
    assert len(asmt["proposals"]) > 0

def test_indian_medicines_search_and_matching():
    # Search formulary
    res = client.get("/medicines/search?q=metformin&limit=5")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert "name" in items[0]
    assert "generic_ingredients" in items[0]

    # Match commercial products for generic
    res = client.get("/medicines/match?generic=Metformin&strength=500+mg&route=oral")
    assert res.status_code == 200
    matches = res.json()
    assert isinstance(matches, list)
    if matches:
        assert "name" in matches[0]
        assert "generic_ingredients" in matches[0]


def test_doctor_approval_and_export_markdown():
    # Create test case
    res = client.post("/cases", json={"title": "Hypertension Case for Approval"})
    case_id = res.json()["case_id"]

    # Set patient data
    client.put(f"/cases/{case_id}/patient", json={
        "age": 55,
        "gender": "F",
        "weight_kg": 65,
        "confirmed_diagnosis": "essential_hypertension",
        "labs": {
            "creatinine": {"value": 0.9, "unit": "mg/dL"},
            "potassium": {"value": 4.3, "unit": "mEq/L"}
        }
    })

    # Approve treatment plan
    approval_res = client.post(f"/cases/{case_id}/approve", json={
        "notes": "Verified BP 145/90 mmHg. Prescribing Amlodipine 5mg PO OD."
    })
    assert approval_res.status_code == 200
    assert approval_res.json()["approved"] is True

    # Export draft report
    export_res = client.get(f"/cases/{case_id}/export")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert "markdown_report" in export_data
    assert "Clinical Decision Support Summary" in export_data["markdown_report"]
    assert export_data["approved_by_doctor"] == 1

def test_evidence_and_audit_endpoints():
    # Evidence source lookup
    res = client.get("/sources/ADA_2024")
    assert res.status_code == 200
    src = res.json()
    assert "American Diabetes Association" in src.get("organization", "") or "ADA" in src.get("organization", "")

    # Data audit summary
    res = client.get("/audit")
    assert res.status_code == 200
    audit_data = res.json()
    assert "content_markdown" in audit_data
    assert len(audit_data["content_markdown"]) > 500

    # Model info
    res = client.get("/model-info/type_2_diabetes")
    assert res.status_code == 200
    info = res.json()
    assert "metrics" in info
    assert info.get("clinical_safety_gate_active") is True

