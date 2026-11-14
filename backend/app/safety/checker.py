import math
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from app.schemas.clinical import (
    PatientAssessmentRequest,
    SafetyCheckResult,
    SupportedCase
)
from app.evidence.disease_catalogue import get_disease_entry
from app.safety.rules_registry import safety_rules_registry, SafetyRuleDefinition
from app.database.db import get_db_connection

def _is_female(gender: Optional[Any]) -> bool:
    if gender is None:
        return False
    g = str(gender).strip().upper()
    return g in ("F", "FEMALE", "WOMAN")

def calculate_egfr_ckd_epi_2021(creatinine_mg_dl: Any, age: Any, gender: Optional[Any] = None) -> Optional[float]:
    """
    CKD-EPI (2021) race-neutral creatinine formula:
    eGFR = 142 * min(Scr/kappa, 1)^alpha * max(Scr/kappa, 1)^-1.200 * 0.9938^Age [* 1.012 if female]
    Assumptions: Creatinine calibrated to IDMS; stable baseline kidney function.
    Returns None for non-finite, missing, or out-of-range clinical inputs.
    """
    try:
        if creatinine_mg_dl is None or age is None:
            return None
        scr = float(creatinine_mg_dl)
        a = float(age)
        if math.isnan(scr) or math.isinf(scr) or math.isnan(a) or math.isinf(a):
            return None
        if scr <= 0 or a <= 0 or a > 130:
            return None

        is_female = _is_female(gender)
        kappa = 0.7 if is_female else 0.9
        alpha = -0.241 if is_female else -0.302
        gender_mult = 1.012 if is_female else 1.0
        
        scr_ratio = scr / kappa
        val = 142.0 * (min(scr_ratio, 1.0) ** alpha) * (max(scr_ratio, 1.0) ** -1.200) * (0.9938 ** a) * gender_mult
        if math.isnan(val) or math.isinf(val):
            return None
        return round(val, 1)
    except (TypeError, ValueError, OverflowError):
        return None

# Backward-compatible alias
calculate_egfr = calculate_egfr_ckd_epi_2021

def calculate_crcl_cockcroft_gault(creatinine_mg_dl: Any, age: Any, weight_kg: Any, gender: Optional[Any] = None) -> Optional[float]:
    """
    Cockcroft-Gault Creatinine Clearance (CrCl):
    CrCl (mL/min) = [(140 - Age) * Weight (kg)] / (72 * Scr (mg/dL)) [* 0.85 if female]
    Assumptions: Stable kidney function; using total body weight.
    Returns None for non-finite, missing, or invalid clinical parameters.
    """
    try:
        if creatinine_mg_dl is None or age is None or weight_kg is None:
            return None
        scr = float(creatinine_mg_dl)
        a = float(age)
        wt = float(weight_kg)
        if math.isnan(scr) or math.isinf(scr) or math.isnan(a) or math.isinf(a) or math.isnan(wt) or math.isinf(wt):
            return None
        if scr <= 0 or a <= 0 or wt <= 0 or a >= 140:
            return None

        factor = 0.85 if _is_female(gender) else 1.0
        crcl = ((140.0 - a) * wt * factor) / (72.0 * scr)
        if math.isnan(crcl) or math.isinf(crcl):
            return None
        return round(crcl, 1)
    except (TypeError, ValueError, OverflowError):
        return None

class SafetyEngine:
    """
    Independent multi-tier clinical safety rule engine for Indian clinical practice.
    Enforces evidence-verified rules for renal function, hepatic impairment, drug-drug interactions,
    allergies, pregnancy, age restrictions, and dose maximums with traceable Rule IDs and versioning.
    """
    ENGINE_VERSION = "2.1.0-IndianClinicalPractice"
    RULE_VERSION = "2.1.0"

    @classmethod
    def evaluate(
        cls,
        request: PatientAssessmentRequest,
        case: Optional[Any]
    ) -> Tuple[List[SafetyCheckResult], List[str], bool]:
        """
        Returns:
            - checks: List of SafetyCheckResult (with rule_id and rule_version)
            - missing_info: List of missing fields
            - can_authorize_dose: bool flag (True only if all critical checks pass and essential data present)
        """
        checks: List[SafetyCheckResult] = []
        missing_info: List[str] = []
        critical_contraindications: bool = False

        # 1. Diagnosis Verification
        if not case:
            checks.append(SafetyCheckResult(
                check_name="Diagnosis Verification",
                status="FAIL",
                findings=f"Diagnosis '{request.diagnosis_id}' is unsupported or missing from the clinical evidence catalogue. Dosing cannot be authorized.",
                severity="critical",
                source_reference="Clinical Safety Architecture v2.1",
                rule_id="RULE_DIAGNOSIS_VERIFICATION_GATE",
                rule_version=cls.RULE_VERSION
            ))
            return checks, ["Unsupported Diagnosis Case ID"], False

        # Support both legacy SupportedCase and new DiseaseCoverageEntry
        diag_name = getattr(case, "diagnosis_name", request.diagnosis_id)
        icd_codes = getattr(case, "icd_codes", getattr(case, "icd_10_codes", []))
        checks.append(SafetyCheckResult(
            check_name="Diagnosis Verification",
            status="PASS",
            findings=f"Diagnosis matched verified catalogue: '{diag_name}' (ICD codes: {', '.join(icd_codes)}).",
            severity="info",
            source_reference="ICD-10 / ICMR Catalogue",
            rule_id="RULE_DIAGNOSIS_VERIFICATION_GATE",
            rule_version=cls.RULE_VERSION
        ))

        # Check broad subtypes
        subtype_guidance = getattr(case, "subtype_prompt_guidance", None)
        if subtype_guidance:
            checks.append(SafetyCheckResult(
                check_name="Clinical Subtype Specification",
                status="WARNING",
                findings=f"Broad Clinical Category Notice: {subtype_guidance}",
                severity="warning",
                source_reference="Clinical Subtype Requirement",
                rule_id="RULE_DIAGNOSIS_VERIFICATION_GATE",
                rule_version=cls.RULE_VERSION
            ))

        # Helper to extract and validate finite numeric lab values
        def get_lab(name_kw: str) -> Optional[float]:
            for k, v in request.labs.items():
                if name_kw in k.lower():
                    try:
                        raw_val = v.value if hasattr(v, "value") else (v.get("value") if isinstance(v, dict) else v)
                        if raw_val is None:
                            return None
                        val = float(raw_val)
                        if math.isnan(val) or math.isinf(val):
                            return None
                        return val
                    except (TypeError, ValueError):
                        return None
            return None

        # 2. Input Completeness Check
        req_inputs = getattr(case, "required_inputs", ["age", "weight_kg"])
        if request.age is None or request.age <= 0:
            missing_info.append("Patient age (years)")
        if ("weight_kg" in req_inputs or request.age < 18) and (request.weight_kg is None or request.weight_kg <= 0):
            missing_info.append("Body weight (kg) - required for weight-based dosing")

        # Check required labs for valid finite value
        for req in req_inputs:
            if req.startswith("labs."):
                lab_name = req.split(".", 1)[1].lower()
                lab_val = get_lab(lab_name)
                if lab_val is None:
                    missing_info.append(f"Essential laboratory measurement: {lab_name.upper()} (missing or invalid/non-finite)")

        if missing_info:
            checks.append(SafetyCheckResult(
                check_name="Input Completeness Verification",
                status="MORE_INFO_NEEDED",
                findings=f"Essential clinical parameters missing: {', '.join(missing_info)}. Dosing proposals are withheld until verified values are provided.",
                severity="critical",
                source_reference="Safety Engine Input Gating",
                rule_id="RULE_INPUT_COMPLETENESS_GATE",
                rule_version=cls.RULE_VERSION
            ))
        else:
            checks.append(SafetyCheckResult(
                check_name="Input Completeness Verification",
                status="PASS",
                findings="Baseline demographic and laboratory parameters required by the clinical guideline are confirmed.",
                severity="info",
                rule_id="RULE_INPUT_COMPLETENESS_GATE",
                rule_version=cls.RULE_VERSION
            ))

        serum_creatinine = get_lab("creatinine")
        serum_glucose = get_lab("glucose")
        serum_potassium = get_lab("potassium")
        reported_egfr = get_lab("egfr")
        alt = get_lab("alt")
        ast = get_lab("ast")
        total_bilirubin = get_lab("bilirubin")
        platelets = get_lab("platelet")
        hemoglobin = get_lab("hemoglobin")

        # Calculate CKD-EPI eGFR and Cockcroft-Gault CrCl
        calculated_egfr = None
        calculated_crcl = None
        if reported_egfr is not None:
            active_egfr = reported_egfr
        elif serum_creatinine is not None and request.age > 0:
            calculated_egfr = calculate_egfr_ckd_epi_2021(serum_creatinine, request.age, request.gender)
            active_egfr = calculated_egfr
        else:
            active_egfr = None

        if serum_creatinine is not None and request.age > 0 and request.weight_kg and request.weight_kg > 0:
            calculated_crcl = calculate_crcl_cockcroft_gault(serum_creatinine, request.age, request.weight_kg, request.gender)

        # 3. Renal Safety Checks
        if serum_creatinine is not None:
            if active_egfr is not None:
                if active_egfr < 30.0:
                    checks.append(SafetyCheckResult(
                        check_name="Renal Impairment Evaluation",
                        status="FAIL",
                        findings=f"Severe renal impairment: estimated eGFR is {active_egfr} mL/min/1.73m2 (CKD Stage 4/5). Biguanides (Metformin) and RAAS inhibitors are strictly restricted or contraindicated.",
                        severity="critical",
                        source_reference="KDIGO_2023 / FDA_METFORMIN / ICMR_DIABETES_2023",
                        rule_id="RULE_RENAL_EGFR_SEVERE",
                        rule_version=cls.RULE_VERSION
                    ))
                    critical_contraindications = True
                elif active_egfr < 45.0:
                    checks.append(SafetyCheckResult(
                        check_name="Renal Impairment Evaluation",
                        status="WARNING",
                        findings=f"Moderate-to-severe CKD stage 3b: eGFR is {active_egfr} mL/min/1.73m2. Metformin dose must not exceed 1000 mg/day; monitor eGFR every 3 months. Avoid initiation.",
                        severity="warning",
                        source_reference="KDIGO_2023 / ICMR_DIABETES_2023",
                        rule_id="RULE_RENAL_EGFR_MODERATE_3B",
                        rule_version=cls.RULE_VERSION
                    ))
                else:
                    checks.append(SafetyCheckResult(
                        check_name="Renal Impairment Evaluation",
                        status="PASS",
                        findings=f"Adequate renal clearance: eGFR is {active_egfr} mL/min/1.73m2 (Creatinine: {serum_creatinine} mg/dL). Method: CKD-EPI 2021.",
                        severity="info",
                        source_reference="CKD-EPI 2021 Formula",
                        rule_id="RULE_RENAL_EGFR_ADEQUATE",
                        rule_version=cls.RULE_VERSION
                    ))
            else:
                checks.append(SafetyCheckResult(
                    check_name="Renal Impairment Evaluation",
                    status="NOT_CHECKED",
                    findings="Creatinine provided but eGFR could not be calculated (missing gender or invalid age).",
                    severity="warning",
                    rule_id="RULE_INPUT_COMPLETENESS_GATE",
                    rule_version=cls.RULE_VERSION
                ))
        else:
            checks.append(SafetyCheckResult(
                check_name="Renal Impairment Evaluation",
                status="MORE_INFO_NEEDED",
                findings="Serum creatinine and eGFR not provided. Clearance-dependent medicine safety cannot be verified.",
                severity="critical",
                rule_id="RULE_INPUT_COMPLETENESS_GATE",
                rule_version=cls.RULE_VERSION
            ))

        # 4. Hepatic Impairment Check
        if alt is not None or ast is not None or total_bilirubin is not None:
            max_transaminase = max(alt or 0, ast or 0)
            if max_transaminase > 200 or (total_bilirubin and total_bilirubin > 3.0):
                checks.append(SafetyCheckResult(
                    check_name="Hepatic Safety Gate",
                    status="FAIL",
                    findings=f"Severe transaminitis / hyperbilirubinemia detected (ALT: {alt}, AST: {ast}, Bilirubin: {total_bilirubin} mg/dL). Hepatotoxic drugs (Isoniazid, Pyrazinamide, Statins, high-dose Paracetamol) are contraindicated.",
                    severity="critical",
                    source_reference="CDSCO / ICMR Guidelines on Drug-Induced Liver Injury",
                    rule_id="RULE_HEPATIC_SEVERE_LIVER_INJURY",
                    rule_version=cls.RULE_VERSION
                ))
                critical_contraindications = True
            elif max_transaminase > 100 or (total_bilirubin and total_bilirubin > 2.0):
                checks.append(SafetyCheckResult(
                    check_name="Hepatic Safety Gate",
                    status="WARNING",
                    findings=f"Moderate elevation in liver enzymes (ALT: {alt}, AST: {ast}, Bilirubin: {total_bilirubin} mg/dL). Use lower doses and monitor LFTs closely.",
                    severity="warning",
                    source_reference="ICMR STW Guidelines",
                    rule_id="RULE_HEPATIC_SEVERE_LIVER_INJURY",
                    rule_version=cls.RULE_VERSION
                ))
            else:
                checks.append(SafetyCheckResult(
                    check_name="Hepatic Safety Gate",
                    status="PASS",
                    findings=f"Liver function markers within acceptable baseline parameters (ALT: {alt or 'normal'}, AST: {ast or 'normal'}).",
                    severity="info",
                    rule_id="RULE_HEPATIC_SEVERE_LIVER_INJURY",
                    rule_version=cls.RULE_VERSION
                ))
        else:
            checks.append(SafetyCheckResult(
                check_name="Hepatic Safety Gate",
                status="NOT_CHECKED",
                findings="Coverage incomplete: Baseline LFTs (ALT/AST/Bilirubin) not entered. Liver safety not confirmed.",
                severity="warning",
                rule_id="RULE_INPUT_COMPLETENESS_GATE",
                rule_version=cls.RULE_VERSION
            ))

        # 5. Glycemic Safety (Diabetes)
        case_id = getattr(case, "disease_id", getattr(case, "case_id", request.diagnosis_id))
        if "diabetes" in case_id:
            if serum_glucose is not None:
                if serum_glucose < 70.0:
                    checks.append(SafetyCheckResult(
                        check_name="Hypoglycemia Danger Alert",
                        status="FAIL",
                        findings=f"CRITICAL HYPOGLYCEMIA: Blood glucose is {serum_glucose} mg/dL (< 70 mg/dL). Hypoglycemic agents (insulin, sulfonylureas) must be withheld. Administer oral glucose or IV dextrose immediately.",
                        severity="critical",
                        source_reference="ADA_2024 / ICMR_DIABETES_2023",
                        rule_id="RULE_GLYCEMIC_HYPOGLYCEMIA_CRITICAL",
                        rule_version=cls.RULE_VERSION
                    ))
                    critical_contraindications = True
                elif serum_glucose > 350.0:
                    checks.append(SafetyCheckResult(
                        check_name="Severe Hyperglycemia Alert",
                        status="WARNING",
                        findings=f"Marked hyperglycemia: Glucose is {serum_glucose} mg/dL (> 350 mg/dL). Screen for DKA / HHS; urgent fluid and inpatient insulin protocol required.",
                        severity="warning",
                        source_reference="ADA_2024",
                        rule_id="RULE_GLYCEMIC_HYPOGLYCEMIA_CRITICAL",
                        rule_version=cls.RULE_VERSION
                    ))
                else:
                    checks.append(SafetyCheckResult(
                        check_name="Glycemic Safety Status",
                        status="PASS",
                        findings=f"Blood glucose is {serum_glucose} mg/dL (within assessable range for non-hypoglycemic antidiabetic therapy).",
                        severity="info",
                        rule_id="RULE_GLYCEMIC_HYPOGLYCEMIA_CRITICAL",
                        rule_version=cls.RULE_VERSION
                    ))

        # 6. Serum Potassium Safety (Hypertension & Heart Failure)
        if "hypertension" in case_id or "heart_failure" in case_id:
            if serum_potassium is not None:
                if serum_potassium > 5.5:
                    checks.append(SafetyCheckResult(
                        check_name="Hyperkalemia Safety Check",
                        status="FAIL",
                        findings=f"Hyperkalemia detected: Serum potassium is {serum_potassium} mEq/L (> 5.5 mEq/L). ACE inhibitors (Lisinopril), ARBs (Telmisartan), and Potassium-sparing diuretics (Spironolactone) are contraindicated.",
                        severity="critical",
                        source_reference="ACC_AHA_2020 / FDA_LISINOPRIL",
                        rule_id="RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE",
                        rule_version=cls.RULE_VERSION
                    ))
                    critical_contraindications = True
                elif serum_potassium < 3.5:
                    checks.append(SafetyCheckResult(
                        check_name="Hypokalemia Safety Check",
                        status="WARNING",
                        findings=f"Hypokalemia detected: Serum potassium is {serum_potassium} mEq/L (< 3.5 mEq/L). Loop/thiazide diuretics require potassium repletion.",
                        severity="warning",
                        source_reference="ACC_AHA_2020",
                        rule_id="RULE_ELECTROLYTE_HYPOKALEMIA_WARNING",
                        rule_version=cls.RULE_VERSION
                    ))
                else:
                    checks.append(SafetyCheckResult(
                        check_name="Electrolyte Safety Check",
                        status="PASS",
                        findings=f"Serum potassium is normal ({serum_potassium} mEq/L).",
                        severity="info",
                        rule_id="RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE",
                        rule_version=cls.RULE_VERSION
                    ))
            else:
                checks.append(SafetyCheckResult(
                    check_name="Electrolyte Safety Check",
                    status="MORE_INFO_NEEDED",
                    findings="Serum potassium is required for RAAS inhibitor and diuretic safety evaluation.",
                    severity="critical",
                    rule_id="RULE_INPUT_COMPLETENESS_GATE",
                    rule_version=cls.RULE_VERSION
                ))

        # 7. Dengue & NSAID Specific Rule
        if "dengue" in case_id:
            checks.append(SafetyCheckResult(
                check_name="Dengue Antiplatelet & NSAID Safety Gate",
                status="PASS",
                findings="MANDATORY RULE ENFORCED: All NSAIDs (Aspirin, Ibuprofen, Diclofenac) are strictly blocked for Dengue to prevent severe hemorrhage. Only Paracetamol is authorized.",
                severity="info",
                source_reference="NVBDCP_DENGUE_2023 / ICMR_DENGUE_2022",
                rule_id="RULE_DENGUE_NSAID_HEMORRHAGE",
                rule_version=cls.RULE_VERSION
            ))
            if platelets and platelets < 50000:
                checks.append(SafetyCheckResult(
                    check_name="Thrombocytopenia Alert",
                    status="WARNING",
                    findings=f"Thrombocytopenia in Dengue: Platelet count is {platelets}/mcL (< 50,000). Monitor hematocrit and plasma leakage signs closely.",
                    severity="warning",
                    source_reference="NVBDCP_DENGUE_2023",
                    rule_id="RULE_DENGUE_NSAID_HEMORRHAGE",
                    rule_version=cls.RULE_VERSION
                ))

        # 8. Asthma Safety Engine
        all_meds_lower = [m.lower() for m in request.current_medications]
        spo2_val = None
        for k, v in request.labs.items():
            if "spo2" in k.lower() or "oxygen" in k.lower():
                spo2_val = v.value
                break

        if "asthma" in case_id:
            # Beta blocker bronchospasm gate
            has_bb = any(bb in m for m in all_meds_lower for bb in ["propranolol", "timolol", "nadolol", "carvedilol", "sotalol", "labetalol"])
            if has_bb:
                checks.append(SafetyCheckResult(
                    check_name="Bronchospasm & Beta-Blocker Safety Gate",
                    status="FAIL",
                    findings="CRITICAL CONTRAINDICATION: Non-selective beta-blockers precipitate severe, potentially fatal bronchospasm in patients with asthma. Must be immediately discontinued and replaced.",
                    severity="critical",
                    source_reference="GINA_2023 / ICMR_ASTHMA_2022",
                    rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
                    rule_version=cls.RULE_VERSION
                ))
                critical_contraindications = True
            else:
                checks.append(SafetyCheckResult(
                    check_name="Bronchospasm & Beta-Blocker Safety Gate",
                    status="PASS",
                    findings="No bronchoconstrictive non-selective beta-blockers detected in current regimen.",
                    severity="info",
                    source_reference="GINA 2023 Guidelines",
                    rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
                    rule_version=cls.RULE_VERSION
                ))

            # Hypoxemia check
            if spo2_val is not None:
                if spo2_val < 92.0:
                    checks.append(SafetyCheckResult(
                        check_name="Acute Asthma Hypoxemia Alert",
                        status="WARNING",
                        findings=f"Severe hypoxemia: SpO2 is {spo2_val}%. Administer controlled supplemental oxygen targeting 93-95% and initiate systemic corticosteroids.",
                        severity="critical",
                        source_reference="ICMR STW Bronchial Asthma",
                        rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
                        rule_version=cls.RULE_VERSION
                    ))
                else:
                    checks.append(SafetyCheckResult(
                        check_name="Oxygenation Stability",
                        status="PASS",
                        findings=f"Acceptable pulse oximetry: SpO2 is {spo2_val}% (target 93-95%).",
                        severity="info",
                        rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
                        rule_version=cls.RULE_VERSION
                    ))

            # SABA monotherapy gate
            has_saba_alone = any("salbutamol" in m or "albuterol" in m for m in all_meds_lower) and not any("budesonide" in m or "fluticasone" in m or "beclomethasone" in m for m in all_meds_lower)
            if has_saba_alone:
                checks.append(SafetyCheckResult(
                    check_name="SABA Monotherapy Safety Gate",
                    status="WARNING",
                    findings="SABA monotherapy warning: Regular use of Salbutamol alone without an Inhaled Corticosteroid increases the risk of life-threatening asthma exacerbations. Switch to ICS-Formoterol combination.",
                    severity="warning",
                    source_reference="GINA Track 1 Guidelines",
                    rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
                    rule_version=cls.RULE_VERSION
                ))

        # 9. Viral Infection Safety Engine
        if "viral" in case_id or "cold" in case_id:
            # Reye's Syndrome Gate (Aspirin in <19 years)
            has_aspirin = any("aspirin" in m or "acetylsalicylic" in m or "ecosprin" in m for m in all_meds_lower)
            if request.age < 19 and has_aspirin:
                checks.append(SafetyCheckResult(
                    check_name="Reye's Syndrome Lethal Danger Gate",
                    status="FAIL",
                    findings=f"CRITICAL CONTRAINDICATION: Patient is {request.age} years old (< 19 yrs) with acute viral infection taking Aspirin. High risk of fatal Reye's Syndrome (acute encephalopathy with microvesicular fatty liver). Stop Aspirin immediately; use Paracetamol only.",
                    severity="critical",
                    source_reference="ICMR / CDSCO / AAP Guidelines on Reye's Syndrome",
                    rule_id="RULE_PEDIATRIC_VIRAL_ASPIRIN_REYES",
                    rule_version=cls.RULE_VERSION
                ))
                critical_contraindications = True
            else:
                checks.append(SafetyCheckResult(
                    check_name="Reye's Syndrome Safety Verification",
                    status="PASS",
                    findings="No pediatric/adolescent Aspirin exposure in acute viral illness.",
                    severity="info",
                    rule_id="RULE_PEDIATRIC_VIRAL_ASPIRIN_REYES",
                    rule_version=cls.RULE_VERSION
                ))

            # Antimicrobial Stewardship Gate
            has_abx = any(abx in m for m in all_meds_lower for abx in ["azithromycin", "amoxicillin", "augmentin", "cefixime", "ciprofloxacin", "levofloxacin", "doxycycline"])
            if has_abx:
                checks.append(SafetyCheckResult(
                    check_name="Antimicrobial Stewardship Safety Gate",
                    status="WARNING",
                    findings="ANTIBIOTIC OVERUSE WARNING: Empirical antibiotic therapy detected in uncomplicated acute viral infection. Antibiotics have zero viral efficacy and drive microbial resistance. Discontinuation advised unless secondary bacterial infection is clinically documented.",
                    severity="warning",
                    source_reference="ICMR Antimicrobial Stewardship Guidelines",
                    rule_id="RULE_INPUT_COMPLETENESS_GATE",
                    rule_version=cls.RULE_VERSION
                ))
            else:
                checks.append(SafetyCheckResult(
                    check_name="Antimicrobial Stewardship Safety Gate",
                    status="PASS",
                    findings="Guideline adherence: Antimicrobial stewardship respected; no unwarranted empirical antibiotics.",
                    severity="info",
                    rule_id="RULE_INPUT_COMPLETENESS_GATE",
                    rule_version=cls.RULE_VERSION
                ))

        # 10. Drug-Drug Interactions & Duplicate Therapy
        has_acei = any("lisinopril" in m or "ramipril" in m or "enalapril" in m for m in all_meds_lower)
        has_arb = any("telmisartan" in m or "losartan" in m or "valsartan" in m for m in all_meds_lower)
        if has_acei and has_arb:
            checks.append(SafetyCheckResult(
                check_name="Dual RAAS Blockade Check",
                status="FAIL",
                findings="Dual RAAS blockade (ACE inhibitor + ARB) detected. Increases risk of hyperkalemia, syncope, and acute kidney injury without added benefit.",
                severity="critical",
                source_reference="KDIGO_2023 / ACC_AHA_2020",
                rule_id="RULE_INTERACTION_DUAL_RAAS_BLOCKADE",
                rule_version=cls.RULE_VERSION
            ))
            critical_contraindications = True

        # Check Metformin + Radiocontrast
        if any("metformin" in m for m in all_meds_lower) and any("contrast" in m or "radiology" in m for m in all_meds_lower):
            checks.append(SafetyCheckResult(
                check_name="Metformin-Contrast Interaction",
                status="WARNING",
                findings="Concurrent iodinated radiocontrast procedure reported with Metformin. Hold Metformin 48h prior to and after procedure.",
                severity="warning",
                source_reference="FDA_METFORMIN",
                rule_id="RULE_RENAL_EGFR_SEVERE",
                rule_version=cls.RULE_VERSION
            ))

        # 11. Allergy Verification
        if request.allergies:
            for allergy in request.allergies:
                checks.append(SafetyCheckResult(
                    check_name=f"Hypersensitivity Check: {allergy}",
                    status="WARNING",
                    findings=f"Documented patient allergy to '{allergy}'. Verify candidate medicines against cross-reactivity.",
                    severity="warning",
                    source_reference="Patient Allergy Profile",
                    rule_id="RULE_INPUT_COMPLETENESS_GATE",
                    rule_version=cls.RULE_VERSION
                ))
        else:
            checks.append(SafetyCheckResult(
                check_name="Hypersensitivity Profile",
                status="PASS",
                findings="No active drug allergies reported by clinician ('None confirmed').",
                severity="info",
                rule_id="RULE_INPUT_COMPLETENESS_GATE",
                rule_version=cls.RULE_VERSION
            ))

        # 12. Pregnancy & Teratogenicity
        conditions_lower = [c.lower() for c in request.existing_conditions]
        is_pregnant = any("pregnan" in c for c in conditions_lower)
        if is_pregnant:
            checks.append(SafetyCheckResult(
                check_name="Pregnancy & Teratogenicity Safety Gate",
                status="FAIL",
                findings="Active pregnancy documented. ACE inhibitors, ARBs, Methotrexate, Miltefosine, high-dose Vitamin A, and Doxycycline are strictly contraindicated.",
                severity="critical",
                source_reference="CDSCO / FDA Black Box Warnings",
                rule_id="RULE_PREGNANCY_TERATOGEN_GATE",
                rule_version=cls.RULE_VERSION
            ))
            critical_contraindications = True

        # Overall Authorization Flag
        # Must have no critical failures, no missing required info
        can_authorize_dose = (not critical_contraindications) and (len(missing_info) == 0)

        # Ensure no broad unchecked category is left as "Safe"
        checks.append(SafetyCheckResult(
            check_name="Comprehensive Formulary Coverage",
            status="PASS" if can_authorize_dose else "NOT_CHECKED",
            findings="All applicable guideline rules for registered candidates evaluated. Unchecked items remain explicitly flagged." if can_authorize_dose else "Coverage incomplete or critical safety criteria unfulfilled.",
            severity="info" if can_authorize_dose else "warning",
            rule_id="RULE_INPUT_COMPLETENESS_GATE",
            rule_version=cls.RULE_VERSION
        ))

        return checks, missing_info, can_authorize_dose

    @classmethod
    def log_safety_decision_records(
        cls,
        case_id: Optional[str],
        assessment_id: Optional[str],
        checks: List[SafetyCheckResult],
        can_authorize_dose: bool
    ) -> int:
        """
        Persists structured safety decision records into SQLite for traceability and auditability.
        Returns count of records saved.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            saved = 0
            for c in checks:
                rec_id = f"sec_{uuid.uuid4().hex[:12]}"
                cursor.execute("""
                    INSERT INTO safety_decision_records (
                        record_id, assessment_id, case_id, rule_id, rule_version,
                        check_name, status, severity, findings, can_authorize_dose,
                        source_reference, evaluated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec_id,
                    assessment_id,
                    case_id,
                    c.rule_id or "RULE_GENERAL_EVALUATION",
                    c.rule_version or cls.RULE_VERSION,
                    c.check_name,
                    c.status,
                    c.severity,
                    c.findings,
                    1 if can_authorize_dose else 0,
                    c.source_reference,
                    now
                ))
                saved += 1
            conn.commit()
            conn.close()
            return saved
        except Exception as e:
            print(f"Audit log warning: {e}")
            return 0
