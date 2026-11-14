export type AssessmentStatus =
  | "PROPOSAL_AVAILABLE"
  | "MORE_INFO_NEEDED"
  | "UNSUPPORTED_CASE"
  | "CONTRAINDICATED";

export type SafetyStatus = "PASS" | "FAIL" | "WARNING" | "NOT_CHECKED" | "MORE_INFO_NEEDED";
export type SafetySeverity = "critical" | "warning" | "info";

export type DoseStatus =
  | "AUTHORIZED"
  | "WITHHELD_INSUFFICIENT_DATA"
  | "WITHHELD_CONTRAINDICATION"
  | "WITHHELD_RESEARCH_PROTOTYPE";

export type ProvenanceType =
  | "VERIFIED_CLINICAL_GUIDELINE"
  | "HISTORICAL_PRESCRIPTION_BENCHMARK"
  | "RESEARCH_ML_MODEL";

export interface LabMeasurement {
  name: string;
  value: number;
  unit: string;
  measurement_date?: string;
}

export interface PatientAssessmentRequest {
  diagnosis_id: string;
  age: number;
  weight_kg?: number;
  gender?: "M" | "F" | "Other";
  allergies: string[];
  current_medications: string[];
  existing_conditions: string[];
  labs: Record<string, LabMeasurement>;
}

export interface SafetyCheckResult {
  check_name: string;
  status: SafetyStatus;
  findings: string;
  severity: SafetySeverity;
  source_reference?: string;
}

export interface EvidenceSource {
  source_id: string;
  title: string;
  organization: string;
  publication_year: number;
  url: string;
  verified: boolean;
  review_date: string;
  citation: string;
}

export interface StandardDoseProtocol {
  generic_name: string;
  suggested_brand: string;
  brand_alternatives: string[];
  adult_dosage: string;
  pediatric_dosage?: string;
  route: string;
  frequency: string;
  timing_instructions?: string;
  renal_adjustment?: string;
  common_strengths?: string[];
}

export interface DoseProposal {
  candidate_medicine: string;
  generic_name: string;
  suggested_brand?: string;
  brand_names?: string[];
  dose_display: string | null;
  unit?: string;
  route?: string;
  frequency?: string;
  instructions?: string;
  dose_status: DoseStatus;
  rationale: string;
  why_candidate: string;
  provenance: ProvenanceType;
  model_confidence?: number;
  shap_contributions?: Record<string, number>;
}

export interface AssessmentResponse {
  status: AssessmentStatus;
  diagnosis_id: string;
  diagnosis_name: string;
  eligible_group_match: boolean;
  candidate_medicines: string[];
  proposals: DoseProposal[];
  safety_checks: SafetyCheckResult[];
  missing_information: string[];
  patient_factors_considered: Record<string, any>;
  clinical_explanation: string;
  model_provenance: Record<string, any>;
  sources: EvidenceSource[];
  disclaimer: string;
}

export interface SupportedCase {
  case_id: string;
  disease_id?: string;
  disease_name?: string;
  diagnosis_name: string;
  category?: string;
  icd_codes?: string[];
  icd_10_codes?: string[];
  eligible_patient_group?: string;
  required_inputs: string[];
  optional_inputs?: string[];
  candidate_medicines: string[];
  dosing_method?: string;
  dose_method_coverage?: string;
  dose_method_type?: string;
  evidence_coverage?: string;
  medicine_selection_coverage?: string;
  model_evaluation_status?: string;
  supported_age_group?: string;
  supported_subtypes?: string[];
  supported_severity?: string[];
  supported_care_setting?: string[];
  missing_data_requirements?: string[];
  subtype_prompt_guidance?: string | null;
  exclusions: string[];
  evidence_url?: string;
  review_date?: string;
  research_model_status?: string;
  is_dose_model_ready?: boolean;
  treatment_protocols?: StandardDoseProtocol[];
}


export interface DiseaseCoverageEntry extends SupportedCase {}

export interface IndianMedicineProduct {
  id: number;
  name: string;
  generic_ingredients: string;
  composition_raw: string;
  strength: string;
  units: string;
  formulation: string;
  route: string;
  release_type: string;
  is_combination: boolean;
  is_exact_strength_match?: boolean;
  uses: string;
  side_effects: string;
  image_url: string;
  source: string;
  verified_date: string;
  cdsco_prescribing_url: string;
  notice?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  structured_cards?: AssessmentResponse | null;
  citations?: EvidenceSource[] | null;
  created_at: string;
}

export interface ClinicalCase {
  case_id: string;
  doctor_id: string;
  title: string;
  diagnosis_id: string;
  diagnosis_name: string;
  patient_data: Record<string, any>;
  patient_version: number;
  status: string;
  approved_by_doctor: boolean;
  approved_at?: string | null;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
}

export interface AuditSummary {
  audit_file: string;
  content_markdown: string;
}

export interface EvidenceChunkMatch {
  chunk_id: string;
  doc_id: string;
  title: string;
  organization: string;
  url: string;
  publication_year: number;
  review_date: string;
  applicable_population: string;
  disease_tags: string[];
  medicine_tags: string[];
  section_name: string;
  text: string;
  citation: string;
  hybrid_score: number;
  bm25_score: number;
  dense_score: number;
}

export interface EvidenceSearchResponse {
  query: string;
  disease_tag?: string | null;
  results_count: number;
  results: EvidenceChunkMatch[];
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  confidence: number;
  sources: EvidenceChunkMatch[];
  warnings?: string[];
}

export interface DashboardMetrics {
  status: string;
  counts: {
    cases: number;
    assessments: number;
    commercial_medicines: number;
    evidence_documents: number;
    treatment_decisions: number;
    unique_patients: number;
    dosing_rules: number;
    supported_diseases: number;
  };
  recent_assessments: Array<{
    assessment_id: string;
    case_id: string;
    status: string;
    approved_by_doctor: boolean;
    created_at: string;
    title?: string;
    diagnosis_name?: string;
  }>;
  import_batches: Array<{
    batch_id: string;
    source_file: string;
    records_read: number;
    records_imported: number;
    records_rejected: number;
    status: string;
    imported_at: string;
  }>;
  model_evaluation: Record<string, any>;
  models_status: {
    classifiers: string[];
    regressors: string[];
  };
}

