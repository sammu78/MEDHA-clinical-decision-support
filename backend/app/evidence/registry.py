from typing import Dict, List, Optional
from app.schemas.clinical import SupportedCase, EvidenceSource

SOURCES: Dict[str, EvidenceSource] = {
    "ADA_2024": EvidenceSource(
        source_id="ADA_2024",
        title="Standards of Care in Diabetes—2024: Pharmacologic Approaches to Glycemic Treatment",
        organization="American Diabetes Association (ADA)",
        publication_year=2024,
        url="https://doi.org/10.2337/dc24-S009",
        verified=True,
        review_date="2024-01-15",
        citation="American Diabetes Association. 9. Pharmacologic Approaches to Glycemic Treatment: Standards of Care in Diabetes—2024. Diabetes Care 2024;47(Suppl. 1):S158–S178."
    ),
    "ACC_AHA_2020": EvidenceSource(
        source_id="ACC_AHA_2020",
        title="2020 International Society of Hypertension / ACC/AHA Global Hypertension Practice Guidelines",
        organization="American College of Cardiology / American Heart Association",
        publication_year=2020,
        url="https://doi.org/10.1161/HYPERTENSIONAHA.120.15026",
        verified=True,
        review_date="2024-03-10",
        citation="Unger T, et al. 2020 International Society of Hypertension Global Hypertension Practice Guidelines. Hypertension. 2020;75(6):1334-1357."
    ),
    "KDIGO_2023": EvidenceSource(
        source_id="KDIGO_2023",
        title="KDIGO 2023 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease",
        organization="Kidney Disease: Improving Global Outcomes (KDIGO)",
        publication_year=2023,
        url="https://doi.org/10.1016/j.kint.2023.08.012",
        verified=True,
        review_date="2023-11-20",
        citation="Kidney Disease: Improving Global Outcomes (KDIGO) Diabetes Work Group. Kidney Int. 2023;104(5S):S1-S127."
    ),
    "FDA_METFORMIN": EvidenceSource(
        source_id="FDA_METFORMIN",
        title="Glucophage (metformin hydrochloride) Tablets - Prescribing Information & Renal Cutoffs",
        organization="U.S. Food and Drug Administration (FDA)",
        publication_year=2021,
        url="https://www.accessdata.fda.gov/drugsatfda_docs/label/2021/020357s039lbl.pdf",
        verified=True,
        review_date="2024-02-01",
        citation="U.S. FDA. Metformin Hydrochloride Prescribing Information: Boxed Warning for Lactic Acidosis and eGFR contraindications (<30 mL/min/1.73m2)."
    ),
    "FDA_LISINOPRIL": EvidenceSource(
        source_id="FDA_LISINOPRIL",
        title="Prinivil / Zestril (lisinopril) - FDA Prescribing Information",
        organization="U.S. Food and Drug Administration (FDA)",
        publication_year=2022,
        url="https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/019777s069lbl.pdf",
        verified=True,
        review_date="2024-02-01",
        citation="U.S. FDA. Lisinopril Tablets: Black Box Warning for Fetal Toxicity, Renal Artery Stenosis & Hyperkalemia Contraindications."
    ),
    "FDA_FUROSEMIDE": EvidenceSource(
        source_id="FDA_FUROSEMIDE",
        title="Lasix (furosemide) - FDA Prescribing Information & Electrolyte Warnings",
        organization="U.S. Food and Drug Administration (FDA)",
        publication_year=2021,
        url="https://www.accessdata.fda.gov/drugsatfda_docs/label/2021/016823s193lbl.pdf",
        verified=True,
        review_date="2024-01-10",
        citation="U.S. FDA. Furosemide Oral and Injection: Warnings regarding fluid and electrolyte depletion (hypokalemia, hyponatremia)."
    )
}

SUPPORTED_CASES: Dict[str, SupportedCase] = {
    "type_2_diabetes": SupportedCase(
        case_id="type_2_diabetes",
        diagnosis_name="Type 2 Diabetes Mellitus",
        icd_codes=["E11", "E11.9", "250.00", "250.02"],
        eligible_patient_group="Adults (age >= 18) with established Type 2 Diabetes requiring glycemic management",
        required_inputs=["age", "weight_kg", "labs.glucose", "labs.creatinine"],
        optional_inputs=["labs.egfr", "labs.hba1c", "labs.potassium"],
        candidate_medicines=["Metformin", "Insulin Regular / Basal", "Glipizide"],
        dosing_method="eGFR-stratified guideline dosing & MIMIC-IV historical regular insulin titration benchmarks",
        exclusions=[
            "Type 1 Diabetes Mellitus",
            "Diabetic Ketoacidosis (DKA) or Hyperosmolar Hyperglycemic State (HHS) requiring ICU continuous drip",
            "Severe renal failure (eGFR < 30 mL/min/1.73m2 contraindicates Metformin)",
            "Pregnancy or gestational diabetes"
        ],
        evidence_url="https://doi.org/10.2337/dc24-S009",
        review_date="2024-01-15",
        research_model_status="Active research benchmark on MIMIC-IV demo with patient-level split validation"
    ),
    "essential_hypertension": SupportedCase(
        case_id="essential_hypertension",
        diagnosis_name="Essential (Primary) Hypertension",
        icd_codes=["I10", "401.9", "401.1"],
        eligible_patient_group="Adults (age >= 18) with confirmed primary hypertension needing antihypertensive initiation or adjustment",
        required_inputs=["age", "labs.creatinine", "labs.potassium"],
        optional_inputs=["weight_kg", "labs.egfr"],
        candidate_medicines=["Amlodipine Besylate", "Lisinopril", "Metoprolol Tartrate"],
        dosing_method="ACC/AHA stepped-care guideline rules with renal and serum potassium safety checks",
        exclusions=[
            "Hypertensive emergency with acute end-organ damage (requires IV labetalol/nicardipine in ICU)",
            "Pregnancy (ACE-inhibitors like Lisinopril strictly contraindicated - Black Box Warning)",
            "History of ACEi-induced angioedema",
            "Severe baseline hyperkalemia (Potassium > 5.5 mEq/L)"
        ],
        evidence_url="https://doi.org/10.1161/HYPERTENSIONAHA.120.15026",
        review_date="2024-03-10",
        research_model_status="Active research benchmark on MIMIC-IV demo with patient-level split validation"
    ),
    "heart_failure": SupportedCase(
        case_id="heart_failure",
        diagnosis_name="Congestive Heart Failure / Volume Overload",
        icd_codes=["I50", "I50.9", "428.0", "428.9"],
        eligible_patient_group="Adults (age >= 18) with clinical congestion or chronic heart failure needing diuretic management",
        required_inputs=["age", "weight_kg", "labs.creatinine", "labs.potassium"],
        optional_inputs=["labs.sodium", "labs.egfr"],
        candidate_medicines=["Furosemide", "Metoprolol Tartrate", "Spironolactone"],
        dosing_method="Loop diuretic guideline dosing conditional on kidney status and serum potassium",
        exclusions=[
            "Anuria or severe acute tubular necrosis uncorrected",
            "Severe uncorrected hypokalemia (K < 3.0 mEq/L)",
            "Cardiogenic shock requiring inotropic support",
            "Documented sulfonamide severe hypersensitivity to furosemide"
        ],
        evidence_url="https://www.accessdata.fda.gov/drugsatfda_docs/label/2021/016823s193lbl.pdf",
        review_date="2024-01-10",
        research_model_status="Active research benchmark on MIMIC-IV demo with patient-level split validation"
    )
}

def get_supported_case(case_id: str) -> Optional[SupportedCase]:
    return SUPPORTED_CASES.get(case_id)

def get_all_supported_cases() -> List[SupportedCase]:
    return list(SUPPORTED_CASES.values())

def get_evidence_source(source_id: str) -> Optional[EvidenceSource]:
    return SOURCES.get(source_id)

def get_all_evidence_sources() -> List[EvidenceSource]:
    return list(SOURCES.values())
