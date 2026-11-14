from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class LabMeasurement(BaseModel):
    name: str = Field(..., description="Standardized lab name e.g. glucose, creatinine, potassium, egfr, hba1c")
    value: float = Field(..., description="Numeric lab result value")
    unit: str = Field(..., description="Lab unit e.g. mg/dL, mEq/L, g/dL, %")
    measurement_date: Optional[str] = Field(None, description="Date or timestamp of measurement (ISO format or YYYY-MM-DD)")

class AllergyEntry(BaseModel):
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[Literal["mild", "moderate", "severe"]] = "moderate"

class CurrentMedicationEntry(BaseModel):
    drug_name: str
    dose: Optional[float] = None
    unit: Optional[str] = None
    route: Optional[str] = None

class PatientAssessmentRequest(BaseModel):
    diagnosis_id: str = Field(..., description="Standardized diagnosis case ID, e.g. 'type_2_diabetes', 'essential_hypertension', 'heart_failure'")
    age: int = Field(..., ge=0, le=125, description="Patient age in years")
    weight_kg: Optional[float] = Field(None, ge=1.0, le=400.0, description="Patient body weight in kilograms")
    gender: Optional[Literal["M", "F", "Other"]] = None
    allergies: List[str] = Field(default_factory=list, description="Known drug or food allergies")
    current_medications: List[str] = Field(default_factory=list, description="Currently active medications")
    existing_conditions: List[str] = Field(default_factory=list, description="Comorbidities, e.g. CKD, asthma, liver failure")
    labs: Dict[str, LabMeasurement] = Field(default_factory=dict, description="Dictionary of recent lab measurements keyed by standard test name")

class SafetyCheckResult(BaseModel):
    check_name: str
    status: Literal["PASS", "FAIL", "WARNING", "NOT_CHECKED", "MORE_INFO_NEEDED"]
    findings: str
    severity: Literal["critical", "warning", "info"] = "info"
    source_reference: Optional[str] = None
    rule_id: Optional[str] = None
    rule_version: Optional[str] = None

class EvidenceSource(BaseModel):
    source_id: str
    title: str
    organization: str
    publication_year: int
    url: str
    verified: bool
    review_date: str
    citation: str

class StandardDoseProtocol(BaseModel):
    generic_name: str
    suggested_brand: str
    brand_alternatives: List[str] = Field(default_factory=list)
    adult_dosage: str
    pediatric_dosage: Optional[str] = None
    route: str
    frequency: str
    timing_instructions: Optional[str] = None
    renal_adjustment: Optional[str] = None
    common_strengths: List[str] = Field(default_factory=list)

class DoseProposal(BaseModel):
    candidate_medicine: str
    generic_name: str
    suggested_brand: Optional[str] = None
    brand_names: List[str] = Field(default_factory=list)
    dose_display: Optional[str] = None
    unit: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    instructions: Optional[str] = None
    dose_status: Literal["AUTHORIZED", "WITHHELD_INSUFFICIENT_DATA", "WITHHELD_CONTRAINDICATION", "WITHHELD_RESEARCH_PROTOTYPE"]
    rationale: str
    provenance: Literal["VERIFIED_CLINICAL_GUIDELINE", "HISTORICAL_PRESCRIPTION_BENCHMARK", "RESEARCH_ML_MODEL"]
    why_candidate: str
    model_confidence: Optional[float] = None
    shap_contributions: Optional[Dict[str, float]] = None


class AssessmentResponse(BaseModel):
    status: Literal["PROPOSAL_AVAILABLE", "MORE_INFO_NEEDED", "UNSUPPORTED_CASE", "CONTRAINDICATED"]
    diagnosis_id: str
    diagnosis_name: str
    eligible_group_match: bool
    candidate_medicines: List[str]
    proposals: List[DoseProposal]
    safety_checks: List[SafetyCheckResult]
    missing_information: List[str]
    patient_factors_considered: Dict[str, Any]
    clinical_explanation: str
    model_provenance: Dict[str, Any]
    sources: List[EvidenceSource]
    disclaimer: str

class SupportedCase(BaseModel):
    case_id: str
    diagnosis_name: str
    icd_codes: List[str]
    eligible_patient_group: str
    required_inputs: List[str]
    optional_inputs: List[str]
    candidate_medicines: List[str]
    dosing_method: str
    exclusions: List[str]
    evidence_url: str
    review_date: str
    research_model_status: str
    treatment_protocols: List[StandardDoseProtocol] = Field(default_factory=list)

class ModelEvaluationInfo(BaseModel):
    case_id: str
    cohort_name: str
    total_records: int
    unique_patients: int
    features_used: List[str]
    train_test_split_method: str
    baseline_classification_accuracy: float
    model_classification_accuracy: float
    baseline_dose_mae: float
    model_dose_mae: float
    dose_unit: str
    known_limitations: List[str]
    clinical_safety_gate_active: bool
