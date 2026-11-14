import pytest
import math
import numpy as np
from app.schemas.clinical import PatientAssessmentRequest, LabMeasurement
from app.safety.checker import SafetyEngine
from app.evidence.disease_catalogue import get_disease_entry
from app.evidence.retriever import HybridRetriever
from app.models.predictor import predictor
from app.explanations.generator import generate_decision_support

def test_failure_case_missing_age():
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=0, # Invalid zero age
        weight_kg=70.0
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    assert any("age" in m.lower() for m in missing)

def test_failure_case_missing_creatinine():
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=55,
        weight_kg=75.0,
        labs={
            "glucose": LabMeasurement(name="glucose", value=140.0, unit="mg/dL")
            # Missing creatinine
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    assert any("creatinine" in m.lower() for m in missing)

def test_failure_case_non_finite_labs_nan_inf():
    case = get_disease_entry("type_2_diabetes")
    # Simulate nan and inf lab inputs
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=60,
        weight_kg=70.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=float("nan"), unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=float("inf"), unit="mg/dL")
        }
    )
    # Must evaluate safely without crashing
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False

def test_failure_case_conflicting_severe_hyperkalemia_with_raas():
    case = get_disease_entry("essential_hypertension")
    req = PatientAssessmentRequest(
        diagnosis_id="essential_hypertension",
        age=62,
        weight_kg=78.0,
        current_medications=["Lisinopril 10mg daily"],
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.2, unit="mg/dL"),
            "potassium": LabMeasurement(name="potassium", value=6.2, unit="mEq/L") # Severe hyperkalemia
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    assert any(c.status == "FAIL" and c.rule_id == "RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE" for c in checks)

def test_failure_case_unknown_medication_identifier():
    feat_df = predictor.extract_features(age=55, labs={})
    dose, unit, shap_vals = predictor.predict_dose_and_shap("nonexistent_drug_regressor_xyz", feat_df)
    assert dose is None
    assert unit is None
    assert shap_vals is None

def test_failure_case_empty_retrieval_query():
    retriever = HybridRetriever(dimension=256)
    results = retriever.retrieve(query="", top_k=3)
    assert isinstance(results, list)

def test_failure_case_dose_proposals_strictly_withheld_on_safety_block():
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=65,
        weight_kg=70.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=3.2, unit="mg/dL"), # Severe renal block
            "glucose": LabMeasurement(name="glucose", value=190.0, unit="mg/dL")
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False

    # Generate proposals
    proposals = generate_decision_support(
        request=req,
        case=case,
        safety_checks=checks,
        missing_info=missing,
        can_authorize_dose=can_auth,
        predicted_candidates=[("Metformin", 0.8), ("Insulin", 0.2)],
        pred_dose_info={}
    )

    # Assert that Metformin is NOT AUTHORIZED
    for p in proposals:
        if "metformin" in p.generic_name.lower():
            assert p.dose_status != "AUTHORIZED"
            assert "WITHHELD" in p.dose_status

def test_llm_cannot_override_deterministic_block():
    # Verify that even if an external mock text claims 'Dose is safe', deterministic safety checks prevail
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=50,
        weight_kg=70.0,
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.0, unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=45.0, unit="mg/dL") # Severe hypoglycemia
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    # No proposal can be authorized when acute hypoglycemia check fails
    proposals = generate_decision_support(
        request=req,
        case=case,
        safety_checks=checks,
        missing_info=missing,
        can_authorize_dose=can_auth,
        predicted_candidates=[],
        pred_dose_info={}
    )
    for p in proposals:
        assert p.dose_status != "AUTHORIZED"
