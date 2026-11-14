"""
Reproducible Ablation Experiment Runner for MEDHA / AushadhiDose CDSS.
Systematically evaluates 8 controlled component configurations:
  Config A: Full System (ML Proposals + Hybrid RAG + Safety Gating + SHAP)
  Config B: Ablation: No RAG Evidence Context
  Config C: Ablation: No ML Proposals (Guideline Rule Engine Only)
  Config D: Ablation: No SHAP Feature Attributions
  Config E: Ablation: BM25-Only Retrieval
  Config F: Ablation: Vector-Only Retrieval
  Config G: Ablation: Hybrid Retrieval
  Config H: Safety Gate Fault-Injection (Isolated Test Harness)

Saves machine-readable experimental registry to reports/ablation_experiment_results.json.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.clinical import PatientAssessmentRequest, LabMeasurement
from app.evidence.disease_catalogue import get_disease_entry
from app.evidence.retriever import HybridRetriever
from app.safety.checker import SafetyEngine
from app.models.predictor import predictor
from app.explanations.generator import generate_decision_support

OUTPUT_PATH = REPO_ROOT / "reports" / "ablation_experiment_results.json"

# Standard test cases covering diverse clinical presentations
STANDARDIZED_CASES = [
    {
        "id": "CASE_T2D_NORMAL",
        "description": "Controlled Type 2 Diabetes with preserved renal function",
        "request": PatientAssessmentRequest(
            diagnosis_id="type_2_diabetes", age=56, weight_kg=78.0, gender="M",
            labs={
                "creatinine": LabMeasurement(name="creatinine", value=1.0, unit="mg/dL"),
                "glucose": LabMeasurement(name="glucose", value=155.0, unit="mg/dL"),
                "potassium": LabMeasurement(name="potassium", value=4.2, unit="mEq/L")
            }
        ),
        "disease_id": "type_2_diabetes",
        "expected_safe": True
    },
    {
        "id": "CASE_T2D_SEVERE_CKD",
        "description": "Type 2 Diabetes with severe CKD Stage 4 (eGFR < 30)",
        "request": PatientAssessmentRequest(
            diagnosis_id="type_2_diabetes", age=68, weight_kg=72.0, gender="F",
            labs={
                "creatinine": LabMeasurement(name="creatinine", value=2.9, unit="mg/dL"),
                "glucose": LabMeasurement(name="glucose", value=180.0, unit="mg/dL"),
                "potassium": LabMeasurement(name="potassium", value=4.8, unit="mEq/L")
            }
        ),
        "disease_id": "type_2_diabetes",
        "expected_safe": False
    },
    {
        "id": "CASE_T2D_HYPOGLYCEMIA",
        "description": "Type 2 Diabetes with acute severe hypoglycemia (< 70 mg/dL)",
        "request": PatientAssessmentRequest(
            diagnosis_id="type_2_diabetes", age=52, weight_kg=80.0, gender="M",
            labs={
                "creatinine": LabMeasurement(name="creatinine", value=0.9, unit="mg/dL"),
                "glucose": LabMeasurement(name="glucose", value=54.0, unit="mg/dL")
            }
        ),
        "disease_id": "type_2_diabetes",
        "expected_safe": False
    },
    {
        "id": "CASE_HTN_HYPERKALEMIA",
        "description": "Essential Hypertension with severe hyperkalemia (> 5.5 mEq/L)",
        "request": PatientAssessmentRequest(
            diagnosis_id="essential_hypertension", age=61, weight_kg=75.0, gender="M",
            labs={
                "creatinine": LabMeasurement(name="creatinine", value=1.3, unit="mg/dL"),
                "potassium": LabMeasurement(name="potassium", value=5.9, unit="mEq/L")
            }
        ),
        "disease_id": "essential_hypertension",
        "expected_safe": False
    },
    {
        "id": "CASE_DENGUE_FEVER",
        "description": "Acute Dengue infection testing NSAID contraindication",
        "request": PatientAssessmentRequest(
            diagnosis_id="dengue", age=29, weight_kg=64.0,
            labs={
                "platelet": LabMeasurement(name="platelet", value=45000, unit="/mcL")
            }
        ),
        "disease_id": "dengue",
        "expected_safe": True # Safe for Paracetamol, NSAIDs blocked
    },
    {
        "id": "CASE_ASTHMA_PROPRANOLOL",
        "description": "Bronchial Asthma with active non-selective beta blocker in regimen",
        "request": PatientAssessmentRequest(
            diagnosis_id="bronchial_asthma", age=42, weight_kg=68.0,
            current_medications=["Propranolol 40mg BID"]
        ),
        "disease_id": "bronchial_asthma",
        "expected_safe": False
    },
    {
        "id": "CASE_PEDIATRIC_VIRAL_ASPIRIN",
        "description": "Pediatric viral cold with concurrent Aspirin (Reye's syndrome risk)",
        "request": PatientAssessmentRequest(
            diagnosis_id="common_cold_viral", age=13, weight_kg=40.0,
            current_medications=["Aspirin 300mg"]
        ),
        "disease_id": "common_cold_viral",
        "expected_safe": False
    },
    {
        "id": "CASE_MISSING_CREATININE",
        "description": "Hypertension with missing serum creatinine (incomplete input)",
        "request": PatientAssessmentRequest(
            diagnosis_id="essential_hypertension", age=58, weight_kg=82.0,
            labs={}
        ),
        "disease_id": "essential_hypertension",
        "expected_safe": False
    }
]

def run_single_ablation(
    config_id: str,
    config_name: str,
    enable_rag: bool,
    enable_ml: bool,
    enable_shap: bool,
    retrieval_alpha: float,
    safety_fault_injection: bool = False
) -> Dict[str, Any]:
    retriever = HybridRetriever(dimension=256)
    
    total_cases = len(STANDARDIZED_CASES)
    authorized_doses = 0
    withheld_doses = 0
    proposals_generated = 0
    citations_attached = 0
    shap_explanations_present = 0
    safety_blocks_triggered = 0
    unexpected_authorizations = 0

    case_logs = []

    for c in STANDARDIZED_CASES:
        req = c["request"]
        disease_id = c["disease_id"]
        cov_entry = get_disease_entry(disease_id)
        expected_safe = c["expected_safe"]

        # 1. Deterministic Safety Gate
        if safety_fault_injection:
            # Simulate critical safety engine exception/failure
            checks = []
            missing_info = ["SAFETY_ENGINE_FAULT_INJECTED"]
            can_auth = False
        else:
            checks, missing_info, can_auth = SafetyEngine.evaluate(req, cov_entry)

        if not can_auth:
            safety_blocks_triggered += 1

        # 2. ML Predictions (if enabled)
        pred_candidates = []
        pred_dose_info = {}
        if enable_ml and cov_entry:
            cohort_id = disease_id
            if "diabetes" in disease_id:
                cohort_id = "type_2_diabetes"
            elif "hypertension" in disease_id:
                cohort_id = "essential_hypertension"
            elif "heart_failure" in disease_id:
                cohort_id = "heart_failure"

            feat_df = predictor.extract_features(req.age, req.labs)
            pred_candidates = predictor.predict_candidates(cohort_id, feat_df)
            
            # Predict dose for compatible target
            reg_id = None
            if "diabetes" in disease_id:
                reg_id = "insulin_sc"
            elif "hypertension" in disease_id:
                reg_id = "metoprolol_po"
            elif "heart_failure" in disease_id:
                reg_id = "furosemide_iv"

            if reg_id:
                dose, unit, shap_vals = predictor.predict_dose_and_shap(reg_id, feat_df)
                if not enable_shap:
                    shap_vals = None
                pred_dose_info = {
                    "dose": dose,
                    "unit": unit,
                    "shap": shap_vals,
                    "insulin_dose": dose if "insulin" in reg_id else None,
                    "insulin_shap": shap_vals if enable_shap and "insulin" in reg_id else None
                }
                if shap_vals:
                    shap_explanations_present += 1

        # 3. Decision Support Proposals
        proposals = generate_decision_support(
            request=req,
            case=cov_entry,
            safety_checks=checks,
            missing_info=missing_info,
            can_authorize_dose=can_auth,
            predicted_candidates=pred_candidates,
            pred_dose_info=pred_dose_info
        )

        for p in proposals:
            proposals_generated += 1
            if p.dose_status == "AUTHORIZED":
                authorized_doses += 1
                if not expected_safe:
                    unexpected_authorizations += 1
            else:
                withheld_doses += 1

        # 4. RAG Retrieval (if enabled)
        evidence_chunks = []
        if enable_rag:
            evidence_chunks = retriever.retrieve(
                query=f"{disease_id} clinical treatment dosage guideline",
                disease_tag=disease_id,
                top_k=2,
                alpha=retrieval_alpha
            )
            if evidence_chunks:
                citations_attached += len(evidence_chunks)

        case_logs.append({
            "case_id": c["id"],
            "safety_authorized": can_auth,
            "proposals_count": len(proposals),
            "citations_count": len(evidence_chunks),
            "shap_available": bool(pred_dose_info.get("shap"))
        })

    return {
        "config_id": config_id,
        "config_name": config_name,
        "parameters": {
            "enable_rag": enable_rag,
            "enable_ml": enable_ml,
            "enable_shap": enable_shap,
            "retrieval_alpha": retrieval_alpha,
            "safety_fault_injection": safety_fault_injection
        },
        "cases_evaluated": total_cases,
        "metrics": {
            "proposals_generated": proposals_generated,
            "authorized_doses": authorized_doses,
            "withheld_doses": withheld_doses,
            "safety_blocks_triggered": safety_blocks_triggered,
            "unexpected_authorizations": unexpected_authorizations,
            "citations_attached": citations_attached,
            "shap_explanations_present": shap_explanations_present,
            "safe_withholding_rate": round(withheld_doses / max(1, (authorized_doses + withheld_doses)), 3)
        },
        "case_logs": case_logs
    }

def run_all_ablation_experiments() -> Dict[str, Any]:
    print("Executing Reproducible Ablation Suite across 8 Configurations...")

    configs = [
        # A: Full System
        ("CONFIG_A_FULL", "Full System (ML + Hybrid RAG + Safety Gating + SHAP)", True, True, True, 0.5, False),
        # B: No RAG Context
        ("CONFIG_B_NO_RAG", "Ablation: No RAG Evidence Retrieval", False, True, True, 0.5, False),
        # C: No ML Proposals
        ("CONFIG_C_NO_ML", "Ablation: Rule-Only Baseline (No ML Models)", True, False, True, 0.5, False),
        # D: No SHAP Explanations
        ("CONFIG_D_NO_SHAP", "Ablation: No SHAP Feature Explanations", True, True, False, 0.5, False),
        # E: BM25-Only Retrieval
        ("CONFIG_E_BM25_ONLY", "Ablation: BM25-Only Retrieval (alpha=0.0)", True, True, True, 0.0, False),
        # F: Vector-Only Retrieval
        ("CONFIG_F_VECTOR_ONLY", "Ablation: Vector-Only Retrieval (alpha=1.0)", True, True, True, 1.0, False),
        # G: Hybrid Retrieval
        ("CONFIG_G_HYBRID", "Ablation: Hybrid Retrieval (alpha=0.5)", True, True, True, 0.5, False),
        # H: Safety Fault Injection (Isolated Test Harness)
        ("CONFIG_H_SAFETY_FAULT", "Safety Fault-Injection: Simulated Engine Failure", True, True, True, 0.5, True)
    ]

    results = {}
    for cid, cname, erag, eml, eshap, alpha, sfault in configs:
        res = run_single_ablation(cid, cname, erag, eml, eshap, alpha, sfault)
        results[cid] = res
        print(f"[{cid}] {cname}: Auth={res['metrics']['authorized_doses']}, Withheld={res['metrics']['withheld_doses']}, Citations={res['metrics']['citations_attached']}, SHAP={res['metrics']['shap_explanations_present']}")

    full_payload = {
        "experiment_meta": {
            "runner": "scripts/run_ablation_experiments.py",
            "date": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "dataset": "Standardized Clinical Test Benchmark (8 Representative Scenarios)",
            "safety_gate_version": SafetyEngine.ENGINE_VERSION
        },
        "results": results
    }

    os.makedirs(REPO_ROOT / "reports", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, indent=2)

    print(f"\nAblation experimental registry saved to: {OUTPUT_PATH}")
    return full_payload

if __name__ == "__main__":
    run_all_ablation_experiments()
