import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AssessmentResultPage } from '../pages/AssessmentResultPage';
import { AssessmentFormPage } from '../pages/AssessmentFormPage';
import type { AssessmentResponse, SupportedCase, PatientAssessmentRequest } from '../types';

describe('Clinical UI Behavior & Safety Gating', () => {
  const mockAuthorizedResult: AssessmentResponse = {
    status: 'PROPOSAL_AVAILABLE',
    diagnosis_id: 'type_2_diabetes',
    diagnosis_name: 'Type 2 Diabetes Mellitus',
    eligible_group_match: true,
    candidate_medicines: ['Metformin', 'Insulin'],
    proposals: [
      {
        candidate_medicine: 'Metformin Hydrochloride',
        generic_name: 'Metformin',
        dose_display: '500',
        unit: 'mg',
        route: 'Oral (PO)',
        frequency: 'Twice daily',
        dose_status: 'AUTHORIZED',
        rationale: 'First-line biguanide with preserved renal function.',
        why_candidate: 'Standard ADA guideline therapy.',
        provenance: 'VERIFIED_CLINICAL_GUIDELINE'
      }
    ],
    safety_checks: [
      {
        check_name: 'Renal Clearance',
        status: 'PASS',
        findings: 'Adequate renal clearance (eGFR > 60).',
        severity: 'info'
      }
    ],
    missing_information: [],
    patient_factors_considered: { age: 58, weight_kg: 84.5 },
    clinical_explanation: 'Patient meets criteria for guideline-directed medical therapy.',
    model_provenance: { dataset: 'MIMIC-IV Demo' },
    sources: [],
    disclaimer: 'Research prototype only.'
  };

  const mockWithheldResult: AssessmentResponse = {
    status: 'MORE_INFO_NEEDED',
    diagnosis_id: 'type_2_diabetes',
    diagnosis_name: 'Type 2 Diabetes Mellitus',
    eligible_group_match: true,
    candidate_medicines: ['Metformin', 'Insulin'],
    proposals: [
      {
        candidate_medicine: 'Metformin Hydrochloride',
        generic_name: 'Metformin',
        dose_display: null,
        dose_status: 'WITHHELD_INSUFFICIENT_DATA',
        rationale: 'Withheld pending serum creatinine confirmation.',
        why_candidate: 'Oral antidiabetic candidate considered.',
        provenance: 'VERIFIED_CLINICAL_GUIDELINE'
      }
    ],
    safety_checks: [
      {
        check_name: 'Renal Impairment Evaluation',
        status: 'MORE_INFO_NEEDED',
        findings: 'Serum creatinine not reported.',
        severity: 'critical'
      }
    ],
    missing_information: ['Required lab measurement: CREATININE'],
    patient_factors_considered: { age: 58 },
    clinical_explanation: 'Missing essential clinical measurements: CREATININE.',
    model_provenance: { dataset: 'MIMIC-IV Demo' },
    sources: [],
    disclaimer: 'Research prototype only.'
  };

  it('renders authorized proposal with dose, unit, and route', () => {
    const handleBack = vi.fn();
    render(<AssessmentResultPage result={mockAuthorizedResult} onBackToForm={handleBack} />);

    expect(screen.getByText(/Dose Proposal Authorized/i)).toBeDefined();
    expect(screen.getByText('500')).toBeDefined();
    expect(screen.getByText('mg')).toBeDefined();
    expect(screen.getByText(/Oral \(PO\)/i)).toBeDefined();
    expect(screen.getAllByText('AUTHORIZED').length).toBeGreaterThan(0);
  });

  it('withholds exact dose display and marks banner when information is missing', () => {
    const handleBack = vi.fn();
    render(<AssessmentResultPage result={mockWithheldResult} onBackToForm={handleBack} />);

    expect(screen.getByText(/Clinical Dosing Withheld/i)).toBeDefined();
    expect(screen.getAllByText('WITHHELD').length).toBeGreaterThan(0);
    expect(screen.getByText(/Dose Display Withheld/i)).toBeDefined();
    expect(screen.getByText(/Required Clinical Inputs Still Missing/i)).toBeDefined();
    expect(screen.getByText(/Required lab measurement: CREATININE/i)).toBeDefined();
  });

  it('triggers return to form handler when return button is clicked', () => {
    const handleBack = vi.fn();
    render(<AssessmentResultPage result={mockAuthorizedResult} onBackToForm={handleBack} />);

    const returnBtn = screen.getByText(/Modify Patient Chart & Lab Parameters/i);
    fireEvent.click(returnBtn);
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it('validates diagnosis selection in assessment form', () => {
    const handleSubmit = vi.fn();
    const emptyData: PatientAssessmentRequest = {
      diagnosis_id: '',
      age: 0,
      allergies: [],
      current_medications: [],
      existing_conditions: [],
      labs: {}
    };
    const mockCases: SupportedCase[] = [
      {
        case_id: 'type_2_diabetes',
        diagnosis_name: 'Type 2 Diabetes Mellitus',
        icd_codes: ['E11'],
        eligible_patient_group: 'Adults with T2D',
        required_inputs: ['age', 'labs.glucose', 'labs.creatinine'],
        optional_inputs: [],
        candidate_medicines: ['Metformin'],
        dosing_method: 'eGFR stratified',
        exclusions: [],
        evidence_url: 'https://example.com',
        review_date: '2024-01-01',
        research_model_status: 'Active'
      }
    ];

    render(
      <AssessmentFormPage
        initialData={emptyData}
        supportedCases={mockCases}
        onSubmit={handleSubmit}
        isLoading={false}
        errorMessage={null}
      />
    );

    const form = document.querySelector('form')!;
    fireEvent.submit(form);

    expect(screen.getByText(/Please select a clinical diagnosis/i)).toBeDefined();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('renders PatientPanel with computed CKD-EPI eGFR and Cockcroft-Gault CrCl', async () => {
    const { PatientPanel } = await import('../components/PatientPanel');
    const mockCase: any = {
      case_id: 'case_test_1',
      title: 'Diabetes Evaluation',
      status: 'OPEN',
      created_at: '2026-09-30T10:00:00Z',
      patient_data: {
        age: 60,
        gender: 'M',
        weight_kg: 75,
        height_cm: 172,
        allergies: ['Penicillin'],
        current_medications: ['Metformin 500mg'],
        existing_conditions: ['T2D'],
        labs: {
          creatinine: { value: 1.2, unit: 'mg/dL' }
        },
        vitals: {}
      }
    };

    render(
      <PatientPanel
        currentCase={mockCase}
        onEditPatient={() => {}}
        isOpen={true}
        onClose={() => {}}
      />
    );

    // Verify patient factors
    expect(screen.getByText(/60 yrs/i)).toBeDefined();
    expect(screen.getByText(/75 kg/i)).toBeDefined();
    expect(screen.getByText(/Penicillin/i)).toBeDefined();

    // Verify Cockcroft-Gault CrCl calculation: (140 - 60) * 75 / (72 * 1.2) = 69.4 mL/min
    expect(screen.getByText(/69.4 mL\/min/i)).toBeDefined();
    // Verify CKD-EPI eGFR calculation exists and is rendered: 69.2 mL/min/1.73m²
    expect(screen.getByText(/69.2 mL\/min/i)).toBeDefined();
    expect(screen.getByText(/CKD-EPI 2021/i)).toBeDefined();
  });

  it('renders IndianMedicineModal verification disclaimer and title', async () => {
    const { IndianMedicineModal } = await import('../components/IndianMedicineModal');
    render(
      <IndianMedicineModal
        isOpen={true}
        onClose={() => {}}
        genericName="Metformin"
        desiredStrength="500 mg"
        desiredRoute="oral"
      />
    );

    expect(screen.getByText(/Matching Indian Commercial Medicines/i)).toBeDefined();
    expect(screen.getByText(/Prescribing Verification Notice/i)).toBeDefined();
    expect(screen.getByText(/Metformin/i)).toBeDefined();
  });

  it('renders Sidebar with Model Audit & Benchmarks tab', async () => {
    const { Sidebar } = await import('../components/Sidebar');
    const handleSetTab = vi.fn();
    render(
      <Sidebar
        activeTab="workspace"
        setActiveTab={handleSetTab}
        cases={[]}
        activeCaseId=""
        onSelectCase={() => {}}
        onNewCase={() => {}}
        isDarkTheme={false}
        onToggleTheme={() => {}}
        backendOnline={true}
        collapsed={false}
        onToggleCollapse={() => {}}
      />
    );

    const auditBtn = screen.getByText(/Model Audit & Benchmarks/i);
    expect(auditBtn).toBeDefined();
    fireEvent.click(auditBtn);
    expect(handleSetTab).toHaveBeenCalledWith('audit');
  });
});


