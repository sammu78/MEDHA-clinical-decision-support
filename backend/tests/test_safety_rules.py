import pytest
from app.schemas.clinical import PatientAssessmentRequest, LabMeasurement
from app.safety.checker import SafetyEngine
from app.safety.rules_registry import safety_rules_registry, SafetyRuleDefinition
from app.evidence.disease_catalogue import get_disease_entry
from app.database.db import get_db_connection

def test_safety_registry_loaded():
    rules = safety_rules_registry.get_all_rules()
    assert len(rules) >= 14
    renal_rules = safety_rules_registry.get_rules_by_domain("renal")
    assert len(renal_rules) >= 3
    for r in rules:
        assert r.rule_id.startswith("RULE_")
        assert r.rule_version == "2.1.0"
        assert r.status in ["active", "draft", "deprecated", "disabled"]

def test_diagnosis_verification_unknown_blocks():
    req = PatientAssessmentRequest(
        diagnosis_id="unknown_mythical_disease",
        age=50,
        weight_kg=70.0
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=None)
    assert can_auth is False
    assert any(c.status == "FAIL" and c.rule_id == "RULE_DIAGNOSIS_VERIFICATION_GATE" for c in checks)

def test_missing_age_and_labs_withholds():
    case = get_disease_entry("type_2_diabetes")
    # Patient with zero/missing labs
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=60,
        weight_kg=75.0,
        gender="M",
        labs={}
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    assert len(missing) > 0
    assert any(c.status == "MORE_INFO_NEEDED" and c.rule_id == "RULE_INPUT_COMPLETENESS_GATE" for c in checks)

def test_renal_egfr_boundary_29_9_blocks():
    # eGFR < 30 should FAIL (RULE_RENAL_EGFR_SEVERE)
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=60,
        weight_kg=70.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=2.8, unit="mg/dL"), # yields eGFR ~25
            "glucose": LabMeasurement(name="glucose", value=140.0, unit="mg/dL")
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    severe_check = next((c for c in checks if c.rule_id == "RULE_RENAL_EGFR_SEVERE"), None)
    assert severe_check is not None
    assert severe_check.status == "FAIL"
    assert severe_check.severity == "critical"

def test_renal_egfr_boundary_35_warns_stage_3b():
    # eGFR between 30 and 45 should WARN (RULE_RENAL_EGFR_MODERATE_3B)
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=65,
        weight_kg=70.0,
        gender="M",
        labs={
            "egfr": LabMeasurement(name="egfr", value=38.0, unit="mL/min/1.73m2"),
            "creatinine": LabMeasurement(name="creatinine", value=1.8, unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=135.0, unit="mg/dL")
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    mod_check = next((c for c in checks if c.rule_id == "RULE_RENAL_EGFR_MODERATE_3B"), None)
    assert mod_check is not None
    assert mod_check.status == "WARNING"

def test_renal_egfr_boundary_45_passes():
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=45,
        weight_kg=75.0,
        gender="M",
        labs={
            "egfr": LabMeasurement(name="egfr", value=55.0, unit="mL/min/1.73m2"),
            "creatinine": LabMeasurement(name="creatinine", value=1.2, unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=130.0, unit="mg/dL")
        }
    )
    checks, missing, can_auth = SafetyEngine.evaluate(req, case=case)
    pass_check = next((c for c in checks if c.rule_id == "RULE_RENAL_EGFR_ADEQUATE"), None)
    assert pass_check is not None
    assert pass_check.status == "PASS"

def test_hyperkalemia_boundary_5_5_vs_5_6():
    case = get_disease_entry("essential_hypertension")
    
    # 5.4 mEq/L -> PASS
    req_pass = PatientAssessmentRequest(
        diagnosis_id="essential_hypertension",
        age=55,
        weight_kg=70.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.0, unit="mg/dL"),
            "potassium": LabMeasurement(name="potassium", value=5.4, unit="mEq/L")
        }
    )
    checks_pass, _, can_auth_pass = SafetyEngine.evaluate(req_pass, case=case)
    assert any(c.rule_id == "RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE" and c.status == "PASS" for c in checks_pass)
    
    # 5.6 mEq/L -> FAIL critical
    req_fail = PatientAssessmentRequest(
        diagnosis_id="essential_hypertension",
        age=55,
        weight_kg=70.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.0, unit="mg/dL"),
            "potassium": LabMeasurement(name="potassium", value=5.6, unit="mEq/L")
        }
    )
    checks_fail, _, can_auth_fail = SafetyEngine.evaluate(req_fail, case=case)
    assert can_auth_fail is False
    assert any(c.rule_id == "RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE" and c.status == "FAIL" for c in checks_fail)

def test_hypoglycemia_danger_blocks():
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=50,
        weight_kg=70.0,
        gender="F",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=0.9, unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=62.0, unit="mg/dL") # < 70
        }
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    hypo_check = next((c for c in checks if c.rule_id == "RULE_GLYCEMIC_HYPOGLYCEMIA_CRITICAL"), None)
    assert hypo_check is not None
    assert hypo_check.status == "FAIL"

def test_dengue_nsaid_contraindication_enforced():
    case = get_disease_entry("dengue")
    req = PatientAssessmentRequest(
        diagnosis_id="dengue",
        age=28,
        weight_kg=65.0,
        labs={
            "platelet": LabMeasurement(name="platelet", value=42000, unit="/mcL")
        }
    )
    checks, _, _ = SafetyEngine.evaluate(req, case=case)
    dengue_check = next((c for c in checks if c.rule_id == "RULE_DENGUE_NSAID_HEMORRHAGE"), None)
    assert dengue_check is not None
    assert "NSAIDs" in dengue_check.findings

def test_asthma_nonselective_betablocker_blocks():
    case = get_disease_entry("bronchial_asthma")
    req = PatientAssessmentRequest(
        diagnosis_id="bronchial_asthma",
        age=40,
        weight_kg=68.0,
        current_medications=["Propranolol 40mg daily", "Salbutamol Inhaler"]
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    bb_check = next((c for c in checks if c.rule_id == "RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM"), None)
    assert bb_check is not None
    assert bb_check.status == "FAIL"

def test_pediatric_viral_aspirin_reyes_blocks():
    case = get_disease_entry("common_cold_viral")
    req = PatientAssessmentRequest(
        diagnosis_id="common_cold_viral",
        age=14, # < 19
        weight_kg=45.0,
        current_medications=["Aspirin 300mg"]
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    reye_check = next((c for c in checks if c.rule_id == "RULE_PEDIATRIC_VIRAL_ASPIRIN_REYES"), None)
    assert reye_check is not None
    assert reye_check.status == "FAIL"

def test_dual_raas_blockade_blocks():
    case = get_disease_entry("essential_hypertension")
    req = PatientAssessmentRequest(
        diagnosis_id="essential_hypertension",
        age=60,
        weight_kg=72.0,
        current_medications=["Lisinopril 10mg", "Telmisartan 40mg"], # ACEi + ARB
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.1, unit="mg/dL"),
            "potassium": LabMeasurement(name="potassium", value=4.5, unit="mEq/L")
        }
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    raas_check = next((c for c in checks if c.rule_id == "RULE_INTERACTION_DUAL_RAAS_BLOCKADE"), None)
    assert raas_check is not None
    assert raas_check.status == "FAIL"

def test_pregnancy_teratogenicity_blocks():
    case = get_disease_entry("essential_hypertension")
    req = PatientAssessmentRequest(
        diagnosis_id="essential_hypertension",
        age=28,
        weight_kg=60.0,
        gender="F",
        existing_conditions=["Pregnancy 24 weeks"],
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=0.7, unit="mg/dL"),
            "potassium": LabMeasurement(name="potassium", value=4.1, unit="mEq/L")
        }
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    assert can_auth is False
    preg_check = next((c for c in checks if c.rule_id == "RULE_PREGNANCY_TERATOGEN_GATE"), None)
    assert preg_check is not None
    assert preg_check.status == "FAIL"

def test_safety_audit_database_logging():
    # Test that log_safety_decision_records writes records to SQLite table
    case = get_disease_entry("type_2_diabetes")
    req = PatientAssessmentRequest(
        diagnosis_id="type_2_diabetes",
        age=55,
        weight_kg=75.0,
        gender="M",
        labs={
            "creatinine": LabMeasurement(name="creatinine", value=1.0, unit="mg/dL"),
            "glucose": LabMeasurement(name="glucose", value=130.0, unit="mg/dL")
        }
    )
    checks, _, can_auth = SafetyEngine.evaluate(req, case=case)
    import uuid
    uid = uuid.uuid4().hex[:8]
    test_case_id = f"test_case_audit_{uid}"
    test_asmt_id = f"asmt_test_audit_{uid}"
    
    saved_count = SafetyEngine.log_safety_decision_records(test_case_id, test_asmt_id, checks, can_auth)
    assert saved_count > 0
    
    # Verify records present in DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM safety_decision_records WHERE case_id = ?", (test_case_id,))
    count_in_db = cur.fetchone()[0]
    conn.close()
    assert count_in_db == saved_count
