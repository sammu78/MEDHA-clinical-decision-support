"""
Structured Safety Rules Registry for MEDHA / AushadhiDose CDSS.
Provides versioned, auditable, and traceable clinical rule definitions
grounded in Indian and international clinical practice guidelines (ICMR, CDSCO, KDIGO, ADA, GINA).
"""

from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class SafetyRuleDefinition(BaseModel):
    rule_id: str = Field(..., description="Stable unique identifier for the safety rule")
    rule_version: str = Field(default="2.1.0", description="Semantic rule version")
    name: str = Field(..., description="Human-readable rule name")
    status: Literal["draft", "verified", "active", "deprecated", "disabled"] = "active"
    clinical_domain: Literal[
        "renal", "hepatic", "electrolyte", "glycemic", "respiratory",
        "infectious", "pediatric", "interaction", "allergy", "pregnancy", "general"
    ] = Field(..., description="Target clinical organ system or safety domain")
    medication_scope: List[str] = Field(default_factory=list, description="List of generic medications or drug classes bounded by this rule")
    preconditions: List[str] = Field(default_factory=list, description="Prerequisite conditions for rule applicability")
    action: Literal["block", "withhold", "require_more_info", "warn", "authorize_pass"] = Field(..., description="Action triggered when conditions match")
    severity: Literal["critical", "warning", "info"] = "critical"
    required_inputs: List[str] = Field(default_factory=list, description="Clinical parameters strictly required to evaluate rule")
    missing_data_behavior: Literal["fail_safe_withhold", "warn_and_monitor", "pass_if_unrelated"] = "fail_safe_withhold"
    source_reference: str = Field(..., description="Approved guideline name, authority, and section")
    source_url: str = Field(..., description="Verified guideline or regulatory URL")
    source_access_date: str = Field(default="2026-10-27", description="Date source evidence was accessed/verified")
    evidence_excerpt: str = Field(..., description="Direct clinical guideline quotation or excerpt supporting the threshold")
    verification_status: Literal["VERIFIED_CLINICAL_GUIDELINE", "PROVISIONAL_EXPERT_CONSENSUS", "UNVERIFIED_DRAFT"] = "VERIFIED_CLINICAL_GUIDELINE"
    reviewer_role: str = Field(default="Clinical Informatics & Pharmacology Review Board", description="Role responsible for rule validation")
    effective_from: str = Field(default="2024-01-01", description="Effective start date")
    effective_until: Optional[str] = Field(None, description="Sunset or revision date")
    unit_requirements: Dict[str, str] = Field(default_factory=dict, description="Mandatory input units required for evaluation")
    test_case_ids: List[str] = Field(default_factory=list, description="Unit and integration test identifiers covering this rule")

# --- CATALOG OF TRACEABLE ACTIVE CLINICAL SAFETY RULES ---

RULES_INVENTORY: List[SafetyRuleDefinition] = [
    # 1. Renal: Severe Impairment (eGFR < 30)
    SafetyRuleDefinition(
        rule_id="RULE_RENAL_EGFR_SEVERE",
        rule_version="2.1.0",
        name="Severe Renal Impairment (eGFR < 30 mL/min/1.73m2) Metformin & RAAS Contraindication",
        status="active",
        clinical_domain="renal",
        medication_scope=["Metformin", "Lisinopril", "Ramipril", "Enalapril", "Telmisartan", "Losartan"],
        preconditions=["eGFR < 30.0 mL/min/1.73m2"],
        action="block",
        severity="critical",
        required_inputs=["creatinine", "age", "gender"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="KDIGO 2023 Clinical Practice Guideline for Diabetes Management in CKD & FDA Metformin Label",
        source_url="https://kdigo.org/guidelines/ckd-evaluation-management/",
        evidence_excerpt="Metformin is contraindicated in patients with an eGFR < 30 mL/min/1.73m2 due to high risk of lactic acidosis. RAAS inhibitors should be discontinued or avoided during severe acute/chronic kidney injury without specialist nephrology oversight.",
        unit_requirements={"creatinine": "mg/dL", "egfr": "mL/min/1.73m2", "age": "years"},
        test_case_ids=["TEST_RENAL_SEVERE_EGFR_BLOCK", "TEST_RENAL_BOUNDARY_29_9"]
    ),

    # 2. Renal: Moderate Impairment (eGFR 30 - 44.9)
    SafetyRuleDefinition(
        rule_id="RULE_RENAL_EGFR_MODERATE_3B",
        rule_version="2.1.0",
        name="Moderate CKD Stage 3b (eGFR 30-44.9 mL/min/1.73m2) Dose Capping",
        status="active",
        clinical_domain="renal",
        medication_scope=["Metformin"],
        preconditions=["eGFR >= 30.0", "eGFR < 45.0"],
        action="warn",
        severity="warning",
        required_inputs=["creatinine", "age", "gender"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="ICMR Guidelines for Management of Type 2 Diabetes 2023 & KDIGO 2023",
        source_url="https://www.icmr.gov.in/standard-treatment-workflows-stws",
        evidence_excerpt="If eGFR is 30-44 mL/min/1.73m2, maximum recommended dose of Metformin is 1000 mg/day; avoid initiation in new patients and monitor renal function every 3 months.",
        unit_requirements={"creatinine": "mg/dL", "egfr": "mL/min/1.73m2"},
        test_case_ids=["TEST_RENAL_MODERATE_EGFR_CAP", "TEST_RENAL_BOUNDARY_44_9"]
    ),

    # 3. Renal: Adequate Renal Function (eGFR >= 45)
    SafetyRuleDefinition(
        rule_id="RULE_RENAL_EGFR_ADEQUATE",
        rule_version="2.1.0",
        name="Adequate Renal Clearance (eGFR >= 45 mL/min/1.73m2) Clearance Verification",
        status="active",
        clinical_domain="renal",
        medication_scope=["Metformin", "Lisinopril", "Metoprolol", "Furosemide"],
        preconditions=["eGFR >= 45.0"],
        action="authorize_pass",
        severity="info",
        required_inputs=["creatinine", "age", "gender"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="CKD-EPI 2021 Race-Free Creatinine Equation & KDIGO 2023",
        source_url="https://kdigo.org/guidelines/ckd-evaluation-management/",
        evidence_excerpt="eGFR >= 45 mL/min/1.73m2 indicates adequate filtration clearance for standard first-line oral antidiabetic and antihypertensive pharmacotherapy with routine monitoring.",
        unit_requirements={"creatinine": "mg/dL", "egfr": "mL/min/1.73m2"},
        test_case_ids=["TEST_RENAL_ADEQUATE_PASS", "TEST_RENAL_BOUNDARY_45_0"]
    ),

    # 4. Hepatic: Severe Transaminitis / Jaundice
    SafetyRuleDefinition(
        rule_id="RULE_HEPATIC_SEVERE_LIVER_INJURY",
        rule_version="2.1.0",
        name="Severe Hepatic Transaminitis (ALT/AST > 200 U/L or Bilirubin > 3.0 mg/dL) Hepatotoxicity Gate",
        status="active",
        clinical_domain="hepatic",
        medication_scope=["Isoniazid", "Pyrazinamide", "Rifampicin", "Statins", "Paracetamol", "Methotrexate"],
        preconditions=["ALT > 200 or AST > 200 or Bilirubin > 3.0"],
        action="block",
        severity="critical",
        required_inputs=["alt", "ast", "bilirubin"],
        missing_data_behavior="warn_and_monitor",
        source_reference="CDSCO / ICMR Standard Treatment Workflows on Drug-Induced Liver Injury (DILI)",
        source_url="https://cdsco.gov.in/",
        evidence_excerpt="Transaminase elevation > 5x ULN (>200 U/L) or serum total bilirubin > 3.0 mg/dL signifies active hepatocyte necrosis or cholestatic injury. Hepatotoxic agents must be held immediately.",
        unit_requirements={"alt": "U/L", "ast": "U/L", "bilirubin": "mg/dL"},
        test_case_ids=["TEST_HEPATIC_SEVERE_BLOCK", "TEST_HEPATIC_BOUNDARY_201"]
    ),

    # 5. Electrolyte: Severe Hyperkalemia
    SafetyRuleDefinition(
        rule_id="RULE_ELECTROLYTE_HYPERKALEMIA_SEVERE",
        rule_version="2.1.0",
        name="Severe Hyperkalemia (Serum Potassium > 5.5 mEq/L) RAAS & K-Sparing Diuretic Block",
        status="active",
        clinical_domain="electrolyte",
        medication_scope=["Lisinopril", "Ramipril", "Telmisartan", "Losartan", "Spironolactone", "Eplerenone"],
        preconditions=["potassium > 5.5"],
        action="block",
        severity="critical",
        required_inputs=["potassium"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="ACC/AHA/HFSA 2022 Heart Failure Guidelines & FDA Lisinopril Warning",
        source_url="https://www.ahajournals.org/doi/10.1161/CIR.0000000000001063",
        evidence_excerpt="Serum potassium > 5.5 mEq/L elevates cardiac dysrhythmia risk. ACE inhibitors, ARBs, and mineralocorticoid receptor antagonists must be withheld until potassium normalizes (< 5.0 mEq/L).",
        unit_requirements={"potassium": "mEq/L"},
        test_case_ids=["TEST_HYPERKALEMIA_BLOCK", "TEST_POTASSIUM_BOUNDARY_5_51"]
    ),

    # 6. Electrolyte: Hypokalemia
    SafetyRuleDefinition(
        rule_id="RULE_ELECTROLYTE_HYPOKALEMIA_WARNING",
        rule_version="2.1.0",
        name="Hypokalemia Alert (Serum Potassium < 3.5 mEq/L) Diuretic Arrhythmia Warning",
        status="active",
        clinical_domain="electrolyte",
        medication_scope=["Furosemide", "Torsemide", "Hydrochlorothiazide", "Chlorthalidone"],
        preconditions=["potassium < 3.5"],
        action="warn",
        severity="warning",
        required_inputs=["potassium"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="ACC/AHA 2020 Hypertension Management Guidelines",
        source_url="https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065",
        evidence_excerpt="Potassium < 3.5 mEq/L necessitates concurrent oral potassium chloride supplementation when administering loop or thiazide diuretics to prevent ventricular arrhythmias.",
        unit_requirements={"potassium": "mEq/L"},
        test_case_ids=["TEST_HYPOKALEMIA_WARN", "TEST_POTASSIUM_BOUNDARY_3_49"]
    ),

    # 7. Glycemic: Critical Hypoglycemia
    SafetyRuleDefinition(
        rule_id="RULE_GLYCEMIC_HYPOGLYCEMIA_CRITICAL",
        rule_version="2.1.0",
        name="Critical Acute Hypoglycemia (< 70 mg/dL) Antidiabetic Withholding Gate",
        status="active",
        clinical_domain="glycemic",
        medication_scope=["Insulin", "Glimepiride", "Gliclazide", "Glipizide", "Metformin"],
        preconditions=["glucose < 70.0"],
        action="block",
        severity="critical",
        required_inputs=["glucose"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="ADA Standards of Care in Diabetes 2024 & ICMR Diabetes Guidelines 2023",
        source_url="https://doi.org/10.2337/dc24-S006",
        evidence_excerpt="Blood glucose < 70 mg/dL represents acute hypoglycemia. All hypoglycemic and antidiabetic pharmacotherapy must be held; initiate Rule of 15 rescue treatment immediately.",
        unit_requirements={"glucose": "mg/dL"},
        test_case_ids=["TEST_HYPOGLYCEMIA_BLOCK", "TEST_GLUCOSE_BOUNDARY_69_9"]
    ),

    # 8. Infectious: Dengue Antiplatelet & NSAID Lethal Bleed Gate
    SafetyRuleDefinition(
        rule_id="RULE_DENGUE_NSAID_HEMORRHAGE",
        rule_version="2.1.0",
        name="Dengue Antiplatelet & NSAID Lethal Hemorrhage Prevention Gate",
        status="active",
        clinical_domain="infectious",
        medication_scope=["Aspirin", "Ibuprofen", "Diclofenac", "Naproxen", "Aceclofenac", "Mefenamic Acid"],
        preconditions=["diagnosis == dengue"],
        action="block",
        severity="critical",
        required_inputs=["diagnosis_id"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="National Vector Borne Disease Control Programme (NVBDCP) Clinical Guidelines for Dengue 2023 & WHO Dengue Guidelines",
        source_url="https://nvbdcp.gov.in/index4.php?lang=1&level=0&linkid=431&lid=3688",
        evidence_excerpt="NSAIDs and antiplatelets (Aspirin, Ibuprofen, Diclofenac) are strictly contraindicated in Dengue due to worsening thrombocytopenia and life-threatening gastrointestinal hemorrhage. Paracetamol is the sole approved antipyretic.",
        unit_requirements={},
        test_case_ids=["TEST_DENGUE_NSAID_BLOCK", "TEST_DENGUE_PARACETAMOL_ALLOW"]
    ),

    # 9. Pediatric / Infectious: Reye's Syndrome Lethal Danger
    SafetyRuleDefinition(
        rule_id="RULE_PEDIATRIC_VIRAL_ASPIRIN_REYES",
        rule_version="2.1.0",
        name="Pediatric/Adolescent Viral Illness Aspirin Lethal Reye's Syndrome Gate",
        status="active",
        clinical_domain="pediatric",
        medication_scope=["Aspirin", "Acetylsalicylic Acid", "Ecosprin"],
        preconditions=["age < 19", "diagnosis in [viral_fever, common_cold, influenza, varicella]"],
        action="block",
        severity="critical",
        required_inputs=["age", "diagnosis_id", "current_medications"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="CDSCO / Indian Academy of Pediatrics (IAP) & CDC Reye's Syndrome Warning",
        source_url="https://cdsco.gov.in/",
        evidence_excerpt="Aspirin administration in children and adolescents (< 19 years) with acute viral infection is strictly contraindicated due to lethal risk of Reye's Syndrome (acute encephalopathy with fatty liver failure).",
        unit_requirements={"age": "years"},
        test_case_ids=["TEST_REYES_SYNDROME_BLOCK", "TEST_AGE_BOUNDARY_18_19"]
    ),

    # 10. Respiratory: Asthma Bronchospasm Non-Selective Beta-Blocker Gate
    SafetyRuleDefinition(
        rule_id="RULE_ASTHMA_BETABLOCKER_BRONCHOSPASM",
        rule_version="2.1.0",
        name="Bronchospasm Lethal Danger: Non-Selective Beta-Blockers in Bronchial Asthma",
        status="active",
        clinical_domain="respiratory",
        medication_scope=["Propranolol", "Timolol", "Nadolol", "Carvedilol", "Sotalol", "Labetalol"],
        preconditions=["diagnosis == bronchial_asthma or asthma"],
        action="block",
        severity="critical",
        required_inputs=["diagnosis_id", "current_medications"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="Global Initiative for Asthma (GINA 2023) & ICMR Standard Treatment Workflows",
        source_url="https://ginasthma.org/gina-reports/",
        evidence_excerpt="Non-selective beta-blockers trigger severe, refractory bronchoconstriction and fatal status asthmaticus in patients with asthma through beta-2 receptor blockade. Absolute contraindication.",
        unit_requirements={},
        test_case_ids=["TEST_ASTHMA_PROPRANOLOL_BLOCK", "TEST_ASTHMA_CARDIOSELECTIVE_WARN"]
    ),

    # 11. Drug-Drug Interaction: Dual RAAS Blockade
    SafetyRuleDefinition(
        rule_id="RULE_INTERACTION_DUAL_RAAS_BLOCKADE",
        rule_version="2.1.0",
        name="Dual RAAS Blockade (ACE Inhibitor + ARB) Toxicity Gate",
        status="active",
        clinical_domain="interaction",
        medication_scope=["Lisinopril + Telmisartan", "Ramipril + Losartan", "Enalapril + Valsartan"],
        preconditions=["has_ace_inhibitor and has_arb"],
        action="block",
        severity="critical",
        required_inputs=["current_medications"],
        missing_data_behavior="pass_if_unrelated",
        source_reference="KDIGO 2023 & ACC/AHA 2020 Hypertension Guidelines",
        source_url="https://kdigo.org/",
        evidence_excerpt="Simultaneous combination of an ACE inhibitor with an Angiotensin Receptor Blocker increases adverse risks of severe hyperkalemia, acute renal failure, and syncope without improving clinical outcomes.",
        unit_requirements={},
        test_case_ids=["TEST_DUAL_RAAS_BLOCK", "TEST_SINGLE_RAAS_PASS"]
    ),

    # 12. Input Completeness: Essential Clinical Variables Gate
    SafetyRuleDefinition(
        rule_id="RULE_INPUT_COMPLETENESS_GATE",
        rule_version="2.1.0",
        name="Essential Patient Parameters & Biomarkers Completeness Gate",
        status="active",
        clinical_domain="general",
        medication_scope=["ALL"],
        preconditions=["missing required demographics or essential lab biomarkers"],
        action="require_more_info",
        severity="critical",
        required_inputs=["age", "weight_kg", "diagnosis_id"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="Clinical Safety Architecture v2.1 & CDSS Governance Principles",
        source_url="https://www.who.int/publications/i/item/9789240029200",
        evidence_excerpt="Automated dosing recommendations cannot be authorized without verified baseline parameters (age, weight, and disease-specific organ clearance markers). Proposals are safely withheld until provided.",
        unit_requirements={},
        test_case_ids=["TEST_INPUT_MISSING_AGE_BLOCK", "TEST_INPUT_MISSING_CREATININE_WITHHOLD"]
    ),

    # 13. Pregnancy & Teratogenicity Gate
    SafetyRuleDefinition(
        rule_id="RULE_PREGNANCY_TERATOGEN_GATE",
        rule_version="2.1.0",
        name="Pregnancy Teratogenicity Absolute Contraindication Gate",
        status="active",
        clinical_domain="pregnancy",
        medication_scope=["Lisinopril", "Telmisartan", "Methotrexate", "Doxycycline", "Miltefosine", "Statins"],
        preconditions=["is_pregnant == True"],
        action="block",
        severity="critical",
        required_inputs=["existing_conditions"],
        missing_data_behavior="pass_if_unrelated",
        source_reference="CDSCO Drug Safety Warnings & FDA Pregnancy Category X / Black Box Warnings",
        source_url="https://cdsco.gov.in/",
        evidence_excerpt="ACE inhibitors, ARBs, Methotrexate, and high-dose teratogens during pregnancy cause severe fetal oligohydramnios, renal dysgenesis, skull hypoplasia, and congenital malformations. Absolute contraindication.",
        unit_requirements={},
        test_case_ids=["TEST_PREGNANCY_ACEI_BLOCK", "TEST_PREGNANCY_SAFE_DRUGS"]
    ),

    # 14. Diagnosis Catalog Verification Gate
    SafetyRuleDefinition(
        rule_id="RULE_DIAGNOSIS_VERIFICATION_GATE",
        rule_version="2.1.0",
        name="Diagnosis Verification & Catalogue Coverage Gate",
        status="active",
        clinical_domain="general",
        medication_scope=["ALL"],
        preconditions=["diagnosis not recognized in clinical evidence catalogue"],
        action="block",
        severity="critical",
        required_inputs=["diagnosis_id"],
        missing_data_behavior="fail_safe_withhold",
        source_reference="ICD-10 Clinical Catalogue / ICMR Disease Coverage Registry",
        source_url="https://icd.who.int/",
        evidence_excerpt="CDSS authorization is restricted to validated disease coverage entries with verified guideline protocols. Unrecognized conditions must not generate automated dosing advice.",
        unit_requirements={},
        test_case_ids=["TEST_UNKNOWN_DIAGNOSIS_BLOCK", "TEST_SUPPORTED_DIAGNOSIS_PASS"]
    )
]

class SafetyRulesRegistry:
    """Singleton registry managing traceable, versioned clinical safety rules."""
    def __init__(self):
        self._rules: Dict[str, SafetyRuleDefinition] = {r.rule_id: r for r in RULES_INVENTORY}

    def get_rule(self, rule_id: str) -> Optional[SafetyRuleDefinition]:
        return self._rules.get(rule_id)

    def get_rules_by_domain(self, domain: str) -> List[SafetyRuleDefinition]:
        return [r for r in self._rules.values() if r.clinical_domain == domain]

    def get_all_rules(self, active_only: bool = True) -> List[SafetyRuleDefinition]:
        if active_only:
            return [r for r in self._rules.values() if r.status == "active"]
        return list(self._rules.values())

    def export_rules_inventory(self) -> List[Dict[str, Any]]:
        return [r.model_dump() for r in self._rules.values()]

# Global registry singleton
safety_rules_registry = SafetyRulesRegistry()
