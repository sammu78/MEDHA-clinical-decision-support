from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.clinical import StandardDoseProtocol

class DiseaseCoverageEntry(BaseModel):
    disease_id: str
    case_id: Optional[str] = None
    disease_name: str
    diagnosis_name: Optional[str] = None
    category: str
    icd_10_codes: List[str]
    evidence_coverage: str
    evidence_sources: List[str]
    medicine_selection_coverage: str
    candidate_medicines: List[str]
    dose_method_coverage: str
    dose_method_type: str  # "GUIDELINE_ALGORITHM" | "FORMULA_WEIGHT_BSA" | "TITRATION_BENCHMARK" | "WITHHELD_SUBTYPE_REQUIRED" | "WITHHELD_INSUFFICIENT_DATA"
    model_evaluation_status: str
    supported_age_group: str
    supported_subtypes: List[str]
    supported_severity: List[str]
    supported_care_setting: List[str]
    required_inputs: List[str] = Field(default_factory=lambda: ["age", "weight_kg"])
    missing_data_requirements: List[str]
    subtype_prompt_guidance: Optional[str] = None
    exclusions: List[str]
    is_dose_model_ready: bool
    treatment_protocols: List[StandardDoseProtocol] = Field(default_factory=list)

    def model_post_init(self, __context):
        if not self.case_id:
            self.case_id = self.disease_id
        if not self.diagnosis_name:
            self.diagnosis_name = self.disease_name


DISEASE_CATALOGUE: Dict[str, DiseaseCoverageEntry] = {
    # 1. Common cold
    "common_cold": DiseaseCoverageEntry(
        disease_id="common_cold",
        disease_name="Common Cold (Viral Upper Respiratory Infection)",
        category="Respiratory / Infectious",
        icd_10_codes=["J00"],
        evidence_coverage="Active (ICMR Standard Treatment Workflow for Acute Rhinitis & Upper Respiratory Tract Infections, 2022; CDSCO Safety Alerts on OTC cough syrups).",
        evidence_sources=["ICMR_STW_URI_2022", "CDSCO_SAFETY_COUGH_2023"],
        medicine_selection_coverage="Symptomatic therapy: Paracetamol for pyrexia/myalgia; Saline nasal spray; Oral antihistamines (Chlorpheniramine/Cetirizine) for rhinorrhea. Strictly no routine antibiotics.",
        candidate_medicines=["Paracetamol", "Cetirizine", "Normal Saline Nasal Spray"],
        dose_method_coverage="Weight-based for pediatrics (15 mg/kg/dose q4-6h) and fixed standard dosing for adults (500-650 mg q6-8h, max 3g/day).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Clinical Practice Guideline Algorithm. Not modeled in MIMIC-IV inpatient demo (outpatient/primary care condition).",
        supported_age_group="Pediatrics (>= 6 months) and Adults",
        supported_subtypes=["Acute viral rhinitis", "Coryza", "Uncomplicated URI"],
        supported_severity=["Mild", "Moderate"],
        supported_care_setting=["Outpatient / Primary Care"],
        missing_data_requirements=["Age", "Weight (mandatory in pediatrics)", "Known G6PD deficiency", "Liver function status if high-dose paracetamol"],
        subtype_prompt_guidance=None,
        exclusions=["Secondary bacterial rhinosinusitis with purulence >10 days", "Lower respiratory involvement", "Children under 2 years for oral decongestants"],
        is_dose_model_ready=True
    ),

    # 2. Influenza
    "influenza": DiseaseCoverageEntry(
        disease_id="influenza",
        disease_name="Influenza (Seasonal & Avian / H1N1)",
        category="Respiratory / Infectious",
        icd_10_codes=["J09", "J10", "J11"],
        evidence_coverage="Active (ICMR Clinical Guidance for Management of Seasonal Influenza / H1N1, 2023; WHO Guidelines on Pharmacological Management of Pandemic Influenza).",
        evidence_sources=["ICMR_INFLUENZA_2023", "WHO_INFLUENZA_2022"],
        medicine_selection_coverage="Neuraminidase inhibitors: Oseltamivir (first line for high-risk/severe); Zanamivir; Paracetamol for fever control.",
        candidate_medicines=["Oseltamivir", "Paracetamol"],
        dose_method_coverage="Oseltamivir: Adults 75 mg PO twice daily for 5 days. Renal dosage adjustment required for CrCl < 60 mL/min (30 mg twice daily if CrCl 30-60, 30 mg once daily if CrCl 10-30).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Guideline-directed dosing with renal safety gating. Inpatient MIMIC-IV demo lacks dedicated Oseltamivir cohort.",
        supported_age_group="All age groups (infants >= 2 weeks to elderly)",
        supported_subtypes=["Uncomplicated Influenza", "Complicated / Severe Influenza (Cat B2/Cat C in Indian guidelines)"],
        supported_severity=["Moderate", "Severe"],
        supported_care_setting=["Outpatient (High risk)", "Inpatient Isolation Ward"],
        missing_data_requirements=["Duration of symptoms (<48h preferred for maximum antiviral efficacy)", "Serum creatinine or CrCl", "Pregnancy status"],
        subtype_prompt_guidance="Specify whether patient is Category A (mild, no antivirals), Category B (high risk, start Oseltamivir), or Category C (respiratory distress, urgent hospitalisation).",
        exclusions=["Severe bronchospasm (caution with inhaled zanamivir)", "End-stage renal failure on dialysis without nephrology-guided dosing"],
        is_dose_model_ready=True
    ),

    # 3. Measles
    "measles": DiseaseCoverageEntry(
        disease_id="measles",
        disease_name="Measles (Rubeola)",
        category="Pediatric / Infectious",
        icd_10_codes=["B05", "B05.9"],
        evidence_coverage="Active (WHO / National Health Mission India Measles Management Protocol, 2022; ICMR Guidelines on Vitamin A supplementation in infectious rashes).",
        evidence_sources=["NHM_MEASLES_2022", "WHO_MEASLES_2023"],
        medicine_selection_coverage="High-dose Vitamin A (mandatory therapeutic protocol to prevent blindness and mortality); Paracetamol for pyrexia; Antibiotics only if secondary bacterial pneumonia/otitis develops.",
        candidate_medicines=["Vitamin A (Retinol palmitate)", "Paracetamol"],
        dose_method_coverage="Age-stratified single daily dose for 2 consecutive days: Age < 6 months: 50,000 IU; Age 6-11 months: 100,000 IU; Age >= 12 months: 200,000 IU orally.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Standard National Health Mission clinical protocol. Zero cases in adult MIMIC-IV demo.",
        supported_age_group="Pediatrics (Infants and Children)",
        supported_subtypes=["Uncomplicated Measles", "Measles with Vitamin A deficiency", "Measles with secondary pneumonia"],
        supported_severity=["Mild", "Moderate", "Severe with complications"],
        supported_care_setting=["Primary Health Centre", "Pediatric Inpatient Unit"],
        missing_data_requirements=["Accurate child age in completed months", "Nutritional status (presence of severe acute malnutrition)", "Eye examination findings (Koplik spots, corneal ulceration)"],
        subtype_prompt_guidance=None,
        exclusions=["Adult measles encephalitis requiring intensive care neurology protocol"],
        is_dose_model_ready=True
    ),

    # 4. Chickenpox
    "chickenpox": DiseaseCoverageEntry(
        disease_id="chickenpox",
        disease_name="Chickenpox (Varicella Zoster)",
        category="Dermatological / Infectious",
        icd_10_codes=["B01", "B01.9"],
        evidence_coverage="Active (ICMR STW for Dermatology and Infectious Diseases; British Association of Dermatologists & Indian Association of Dermatologists, Venereologists and Leprologists IADVL guidelines).",
        evidence_sources=["IADVL_VARICELLA_2021", "CDSCO_ACYCLOVIR_2020"],
        medicine_selection_coverage="Oral Aciclovir (within 24-48h of rash onset for adolescents, adults, immunocompromised); Calamine lotion; Paracetamol. Avoid NSAIDs (risk of severe necrotizing soft-tissue infection).",
        candidate_medicines=["Aciclovir", "Paracetamol", "Calamine Lotion"],
        dose_method_coverage="Adults: Aciclovir 800 mg PO 5 times daily (every 4 hours while awake) for 7 days. Dose reduction required in renal impairment (eGFR 10-25: 800 mg q8h; eGFR < 10: 800 mg q12h).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Clinical Practice Guideline Algorithm with renal adjustment rules.",
        supported_age_group="Children >12 years, Adults, High-risk pediatric patients",
        supported_subtypes=["Uncomplicated varicella", "Adult chickenpox", "Varicella in immunocompromised"],
        supported_severity=["Mild", "Moderate", "Severe"],
        supported_care_setting=["Outpatient", "Isolation Inpatient"],
        missing_data_requirements=["Onset time of vesicular rash (<24-72h)", "Renal function (eGFR or Serum Creatinine)", "Pregnancy status"],
        subtype_prompt_guidance=None,
        exclusions=["Varicella pneumonia or encephalitis (requires IV Aciclovir 10-15 mg/kg q8h)", "Use of Ibuprofen/NSAIDs is strictly contraindicated due to necrotizing fasciitis risk"],
        is_dose_model_ready=True
    ),

    # 5. Dengue
    "dengue": DiseaseCoverageEntry(
        disease_id="dengue",
        disease_name="Dengue Fever & Dengue Hemorrhagic Fever",
        category="Vector-Borne / Infectious",
        icd_10_codes=["A90", "A91"],
        evidence_coverage="Active (National Vector Borne Disease Control Programme NVBDCP India Guidelines for Clinical Management of Dengue Fever, 2023; ICMR STW for Dengue).",
        evidence_sources=["NVBDCP_DENGUE_2023", "ICMR_DENGUE_2022"],
        medicine_selection_coverage="Isotonic crystalloid fluid resuscitation (Ringer's Lactate / 0.9% Normal Saline) tailored to hematocrit; Paracetamol for fever. Strict contraindication for Aspirin, Ibuprofen, and other NSAIDs (platelet inhibition and gastric bleeding risk).",
        candidate_medicines=["Paracetamol", "Ringer Lactate IV", "0.9% Normal Saline IV"],
        dose_method_coverage="Paracetamol: 500-650 mg PO q6h (max 3g/day in adults, 10-15 mg/kg in children). IV fluid algorithm based on hematocrit and warning signs (5-7 mL/kg/h titrated down to 3-5 mL/kg/h).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Guideline-directed fluid and antipyretic protocol. NSAID safety block active.",
        supported_age_group="All ages (Pediatric and Adult)",
        supported_subtypes=["Dengue without warning signs", "Dengue with warning signs (abdominal pain, persistent vomiting, mucosal bleed)", "Severe Dengue / Dengue Shock Syndrome"],
        supported_severity=["Grade I", "Grade II", "Severe / Shock"],
        supported_care_setting=["Outpatient (Group A)", "Inpatient Monitoring (Group B)", "ICU (Group C)"],
        missing_data_requirements=["Serial Hematocrit / Packed Cell Volume (PCV)", "Platelet count", "Presence of warning signs", "Fluid balance & urine output"],
        subtype_prompt_guidance="Classify patient into Group A (no warning signs, outpatient oral hydration), Group B (warning signs, admission for IV fluids), or Group C (severe plasma leakage / shock).",
        exclusions=["NSAIDs (Aspirin, Ibuprofen, Diclofenac, Mefenamic acid) are strictly contraindicated", "Routine prophylactic platelet transfusions without active bleeding are not recommended"],
        is_dose_model_ready=True
    ),

    # 6. Tuberculosis
    "tuberculosis": DiseaseCoverageEntry(
        disease_id="tuberculosis",
        disease_name="Tuberculosis (Pulmonary & Extrapulmonary)",
        category="Infectious / Mycobacterial",
        icd_10_codes=["A15", "A16", "A17", "A18", "A19"],
        evidence_coverage="Active (National Tuberculosis Elimination Programme NTEP India Technical and Operational Guidelines, 2023; ICMR STW for Pulmonary Tuberculosis).",
        evidence_sources=["NTEP_INDIA_2023", "ICMR_TB_2022"],
        medicine_selection_coverage="Daily fixed-dose combination (FDC) regimen: Isoniazid (H), Rifampicin (R), Pyrazinamide (Z), and Ethambutol (E) for 2 months intensive phase, followed by HRE for 4 months continuation phase.",
        candidate_medicines=["Isoniazid", "Rifampicin", "Pyrazinamide", "Ethambutol", "Pyridoxine (Vitamin B6)"],
        dose_method_coverage="Weight-band based 4-drug FDC (HRZE): Weight 25-34 kg: 2 tabs daily; 35-49 kg: 3 tabs daily; 50-64 kg: 4 tabs daily; 65-75 kg: 5 tabs daily; >75 kg: 6 tabs daily. Pyridoxine 20-40 mg daily co-administered.",
        dose_method_type="FORMULA_WEIGHT_BSA",
        model_evaluation_status="NTEP Weight-band algorithm verified. Hepatic enzyme monitoring and renal safety gates active.",
        supported_age_group="Adults and Adolescents (>= 25 kg body weight)",
        supported_subtypes=["New Pulmonary TB (Drug-sensitive)", "Extrapulmonary TB (Lymph node, Pleural)", "TB in Diabetics / HIV"],
        supported_severity=["Uncomplicated", "Disseminated", "Severe"],
        supported_care_setting=["NTEP DOTS Centre / Outpatient Clinic / Inpatient"],
        missing_data_requirements=["Accurate weight in kilograms", "Baseline Liver Function Tests (ALT, AST, Total Bilirubin)", "Serum Creatinine", "Prior anti-TB treatment history"],
        subtype_prompt_guidance="Confirm whether patient is New Drug-Sensitive TB or Previously Treated / Drug-Resistant TB (MDR/XDR TB requires specialized PMDT expert panel regimen).",
        exclusions=["Pre-existing acute hepatitis (ALT > 3x normal with symptoms or > 5x normal asymptomatic contraindicates PZA/INH/RIF until resolution)", "Optic neuritis contraindicates Ethambutol"],
        is_dose_model_ready=True
    ),

    # 7. Typhoid
    "typhoid": DiseaseCoverageEntry(
        disease_id="typhoid",
        disease_name="Typhoid Fever (Enteric Fever - S. enterica serovar Typhi)",
        category="Gastrointestinal / Infectious",
        icd_10_codes=["A01", "A01.0"],
        evidence_coverage="Active (ICMR Evidence-Based Guidelines on Treatment of Enteric Fever in India, 2022; Indian Academy of Pediatrics IAP guidelines on Typhoid).",
        evidence_sources=["ICMR_TYPHOID_2022", "IAP_TYPHOID_2021"],
        medicine_selection_coverage="First line (due to widespread Indian ciprofloxacin resistance): Azithromycin PO (uncomplicated) or Ceftriaxone IV (complicated / hospitalized); Cefixime PO as step-down.",
        candidate_medicines=["Azithromycin", "Ceftriaxone", "Cefixime", "Paracetamol"],
        dose_method_coverage="Azithromycin: Adults 1g PO on day 1 then 500 mg once daily for 6 days (or 20 mg/kg/day for 7 days in pediatrics). Ceftriaxone: Adults 2g IV once daily (or 1g q12h) for 10-14 days.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="ICMR Guideline Algorithm with local resistance pattern rules. Tested against empiric fever protocols.",
        supported_age_group="Pediatrics and Adults",
        supported_subtypes=["Uncomplicated Enteric Fever", "Complicated Enteric Fever (Gastrointestinal bleed, encephalopathy)"],
        supported_severity=["Mild", "Moderate", "Severe"],
        supported_care_setting=["Outpatient Primary Care", "Inpatient Medical Ward"],
        missing_data_requirements=["Blood culture status", "Kidney function (eGFR for ceftriaxone in dual hepatic-renal failure)", "Hepatic function"],
        subtype_prompt_guidance=None,
        exclusions=["Fluoroquinolones (Ciprofloxacin/Ofloxacin) should be avoided as empiric first-line in India due to high MIC / nalidixic acid resistance"],
        is_dose_model_ready=True
    ),

    # 8. Cholera
    "cholera": DiseaseCoverageEntry(
        disease_id="cholera",
        disease_name="Cholera (Vibrio cholerae)",
        category="Gastrointestinal / Water-Borne",
        icd_10_codes=["A00", "A00.9"],
        evidence_coverage="Active (WHO Guidelines for the Management of Cholera, 2022; National Centre for Disease Control NCDC India Guidelines).",
        evidence_sources=["WHO_CHOLERA_2022", "NCDC_INDIA_2021"],
        medicine_selection_coverage="Aggressive rehydration: WHO-Oral Rehydration Salts (ORS) for mild/moderate; IV Ringer's Lactate (Plan C) for severe dehydration. Antibiotics for severe dehydration: Doxycycline (single dose) or Azithromycin (single dose).",
        candidate_medicines=["WHO-ORS", "Ringer Lactate IV", "Doxycycline", "Azithromycin"],
        dose_method_coverage="Rehydration: Plan C IV Ringer's Lactate 100 mL/kg within 3 hours (30 mL/kg in 30 min, then 70 mL/kg in 2.5 hours for adults). Doxycycline: single dose 300 mg PO; Azithromycin: single dose 1 g PO (preferred in pregnancy/children).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Standard WHO/NCDC emergency rehydration algorithm. Dosing gates ensure hydration priority before oral medication.",
        supported_age_group="All age groups",
        supported_subtypes=["Cholera with no dehydration", "Cholera with some dehydration", "Severe cholera with hypovolemic shock"],
        supported_severity=["Moderate", "Severe / Shock"],
        supported_care_setting=["Emergency Treatment Centre", "Inpatient Diarrhoea Ward"],
        missing_data_requirements=["Degree of dehydration (Signs: sunken eyes, skin pinch, radial pulse, lethargy)", "Weight (kg)", "Pregnancy status"],
        subtype_prompt_guidance=None,
        exclusions=["Doxycycline is contraindicated in pregnancy and children under 8 years; substitute single-dose Azithromycin (20 mg/kg or 1g)"],
        is_dose_model_ready=True
    ),

    # 9. Pneumonia
    "pneumonia": DiseaseCoverageEntry(
        disease_id="pneumonia",
        disease_name="Pneumonia (Community-Acquired, Hospital-Acquired & Aspiration)",
        category="Respiratory / Bacterial",
        icd_10_codes=["J13", "J14", "J15", "J18", "J18.9"],
        evidence_coverage="Active (ICMR Standard Treatment Workflow for Community-Acquired Pneumonia CAP in Adults, 2022; British Thoracic Society BTS Guidelines; ATS/IDSA CAP Guidelines).",
        evidence_sources=["ICMR_CAP_2022", "ATS_IDSA_CAP_2019", "BTS_PNEUMONIA_2020"],
        medicine_selection_coverage="Subtype-specific: Outpatient CAP (CURB-65 0-1): Amoxicillin-Clavulanate PO or Azithromycin PO; Inpatient non-ICU CAP (CURB-65 2): IV Ceftriaxone + IV/PO Azithromycin; ICU severe CAP (CURB-65 3-5): Piperacillin-Tazobactam IV + Azithromycin/Levofloxacin IV.",
        candidate_medicines=["Amoxicillin-Clavulanate", "Azithromycin", "Ceftriaxone", "Piperacillin-Tazobactam", "Levofloxacin"],
        dose_method_coverage="Outpatient: Amoxicillin-Clavulanate 625 mg PO tid or 1g PO bid for 5-7 days. Inpatient: Ceftriaxone 1-2g IV once daily + Azithromycin 500 mg IV/PO once daily. Renal adjustment for eGFR < 50 mL/min.",
        dose_method_type="WITHHELD_SUBTYPE_REQUIRED",
        model_evaluation_status="Broad clinical diagnosis. Dosing proposal withheld until CURB-65 score, subtype (CAP vs HAP), and SpO2 are entered.",
        supported_age_group="Adults (>= 18 years)",
        supported_subtypes=["Community-Acquired Pneumonia (CAP)", "Hospital-Acquired Pneumonia (HAP / VAP)", "Aspiration Pneumonia", "Atypical Pneumonia"],
        supported_severity=["Mild (CURB-65 0)", "Moderate (CURB-65 1-2)", "Severe (CURB-65 3-5 / ICU)"],
        supported_care_setting=["Outpatient", "Medical Ward", "Intensive Care Unit (ICU)"],
        missing_data_requirements=["Clinical Subtype (CAP vs HAP vs Aspiration)", "CURB-65 criteria (Confusion, BUN > 19 mg/dL, Respiratory rate >= 30, BP < 90/60, Age >= 65)", "Oxygen saturation (SpO2)", "Renal function (Creatinine/BUN)"],
        subtype_prompt_guidance="Pneumonia cannot be treated as a single uniform dosing task. Please specify: 1) Setting (Community vs Hospital acquired), 2) CURB-65 risk score components, and 3) Respiratory rate / SpO2.",
        exclusions=["Severe penicillin anaphylaxis (use respiratory fluoroquinolone or macrolide + aztreonam)"],
        is_dose_model_ready=False
    ),

    # 10. Diphtheria
    "diphtheria": DiseaseCoverageEntry(
        disease_id="diphtheria",
        disease_name="Diphtheria (Corynebacterium diphtheriae)",
        category="Respiratory / Infectious",
        icd_10_codes=["A36", "A36.0", "A36.9"],
        evidence_coverage="Active (ICMR / Ministry of Health & Family Welfare MoHFW Guidelines for Clinical Management of Diphtheria in India, 2022; WHO Guidelines).",
        evidence_sources=["MOHFW_DIPHTHERIA_2022", "WHO_DIPHTHERIA_2021"],
        medicine_selection_coverage="Equine Diphtheria Antitoxin DAT (critical cornerstone to neutralize unbound toxin); plus Antibiotics to eliminate carriage and halt toxin production: Procaine Penicillin G or Oral/IV Erythromycin / Azithromycin.",
        candidate_medicines=["Diphtheria Antitoxin (DAT)", "Procaine Penicillin G", "Erythromycin", "Azithromycin"],
        dose_method_coverage="DAT dose depends strictly on site, extent of pseudomembrane, and duration (20,000 to 100,000 units IV infusion after test dose). Antibiotics: Procaine Penicillin G 25,000-50,000 U/kg/day IM (max 1.2 MU/day) or Erythromycin 500 mg PO q6h for 14 days.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Emergency guideline protocol. Requires mandatory hospital admission and airway readiness.",
        supported_age_group="All age groups",
        supported_subtypes=["Pharyngeal / Tonsillar Diphtheria", "Laryngeal Diphtheria", "Nasal Diphtheria", "Cutaneous Diphtheria"],
        supported_severity=["Moderate", "Severe / Bull-neck Diphtheria"],
        supported_care_setting=["Specialized Inpatient Isolation / ICU with Airway Support"],
        missing_data_requirements=["Site and extent of pseudomembrane", "Duration of symptoms (days)", "History of equine serum hypersensitivity / skin test result", "Cardiac rhythm / ECG (monitoring for myocarditis)"],
        subtype_prompt_guidance=None,
        exclusions=["Do not delay DAT administration while awaiting laboratory confirmation", "DAT test dose must precede full infusion due to anaphylaxis risk"],
        is_dose_model_ready=True
    ),

    # 11. Malaria
    "malaria": DiseaseCoverageEntry(
        disease_id="malaria",
        disease_name="Malaria (Plasmodium falciparum & Plasmodium vivax)",
        category="Vector-Borne / Parasitic",
        icd_10_codes=["B50", "B51", "B54"],
        evidence_coverage="Active (National Vector Borne Disease Control Programme NVBDCP India National Drug Policy on Malaria, 2023; ICMR STW for Malaria).",
        evidence_sources=["NVBDCP_MALARIA_2023", "ICMR_MALARIA_2022"],
        medicine_selection_coverage="Species-specific in India: P. falciparum: Artemether + Lumefantrine (ACT) or Artesunate + Sulfadoxine-Pyrimethamine (ACT-SP, except Northeast where AL is mandatory) + single dose Primaquine (0.25 mg/kg); P. vivax: Chloroquine 25 mg base/kg over 3 days followed by Primaquine (0.25 mg/kg/day) for 14 days; Severe malaria: IV Artesunate.",
        candidate_medicines=["Artemether-Lumefantrine", "Chloroquine Phosphate", "Primaquine", "Artesunate IV"],
        dose_method_coverage="P. falciparum: Artemether-Lumefantrine weight-band 6-dose regimen over 3 days (e.g. >= 35 kg: 4 tabs at 0h, 8h, 24h, 36h, 48h, 60h). P. vivax: Chloroquine 600 mg base day 1, 600 mg day 2, 300 mg day 3. Primaquine 15 mg daily for 14 days.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="NVBDCP National Algorithm with G6PD safety gates. Subtype confirmation required.",
        supported_age_group="All age groups",
        supported_subtypes=["P. falciparum (Uncomplicated)", "P. vivax (Uncomplicated)", "Mixed Infection", "Severe / Cerebral Malaria"],
        supported_severity=["Uncomplicated", "Severe"],
        supported_care_setting=["Primary Health Centre", "Community Hospital", "ICU (Severe)"],
        missing_data_requirements=["Plasmodium species (P. falciparum vs P. vivax vs mixed)", "G6PD deficiency status (mandatory before 14-day Primaquine)", "Pregnancy status", "Geographical state in India (Northeast ACT policy)"],
        subtype_prompt_guidance="Please specify: 1) Plasmodium species confirmed on peripheral smear or RDT, 2) Whether severe malaria signs exist (jaundice, hypoglycemia, impaired consciousness), and 3) G6PD status.",
        exclusions=["Primaquine is strictly contraindicated in pregnancy, infants < 6 months, and G6PD deficiency (risk of severe acute hemolytic crisis)", "ACT-SP is contraindicated in Northeast states due to resistance"],
        is_dose_model_ready=True
    ),

    # 12. Amoebiasis
    "amoebiasis": DiseaseCoverageEntry(
        disease_id="amoebiasis",
        disease_name="Amoebiasis (Intestinal Dysentery & Amoebic Liver Abscess)",
        category="Gastrointestinal / Parasitic",
        icd_10_codes=["A06", "A06.0", "A06.4"],
        evidence_coverage="Active (ICMR STW for Gastrointestinal Infections; CDC & Indian Journal of Medical Microbiology Clinical Recommendations).",
        evidence_sources=["ICMR_GI_2022", "CDC_AMOEBIASIS_2021"],
        medicine_selection_coverage="Tissue amoebicide: Metronidazole or Tinidazole; followed by Luminal amoebicide: Diloxanide Furoate or Paromomycin to eradicate cyst carriage.",
        candidate_medicines=["Metronidazole", "Tinidazole", "Diloxanide Furoate"],
        dose_method_coverage="Adults: Metronidazole 400-800 mg PO three times daily for 7-10 days (or Tinidazole 2g PO once daily for 3-5 days); followed by Diloxanide Furoate 500 mg PO three times daily for 10 days.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Clinical Guideline Algorithm with alcohol disulfiram-like reaction alert.",
        supported_age_group="Children and Adults",
        supported_subtypes=["Acute Amoebic Dysentery (Colitis)", "Amoebic Liver Abscess", "Asymptomatic Cyst Passage"],
        supported_severity=["Mild", "Moderate", "Severe with abscess"],
        supported_care_setting=["Outpatient", "Inpatient (for liver abscess)"],
        missing_data_requirements=["Stool microscopy or serology / Ultrasound for liver abscess", "Alcohol intake status (absolute disulfiram reaction warning)", "Pregnancy (first trimester caution)"],
        subtype_prompt_guidance=None,
        exclusions=["Alcohol consumption during and for 48h after Metronidazole/Tinidazole therapy is contraindicated (severe disulfiram-like reaction)"],
        is_dose_model_ready=True
    ),

    # 13. Kala-azar
    "kala_azar": DiseaseCoverageEntry(
        disease_id="kala_azar",
        disease_name="Kala-Azar (Visceral Leishmaniasis - Leishmania donovani)",
        category="Vector-Borne / Parasitic",
        icd_10_codes=["B55", "B55.0"],
        evidence_coverage="Active (National Kala-azar Elimination Programme NVBDCP India Guidelines, 2022; WHO Guidelines for Visceral Leishmaniasis in Southeast Asia).",
        evidence_sources=["NVBDCP_KALA_AZAR_2022", "WHO_LEISHMANIASIS_2021"],
        medicine_selection_coverage="First line in India: Single infusion Liposomal Amphotericin B (AmBisome); Second line / combination: Miltefosine oral capsules + Paromomycin IM injection.",
        candidate_medicines=["Liposomal Amphotericin B", "Miltefosine", "Paromomycin"],
        dose_method_coverage="Single infusion Liposomal Amphotericin B 10 mg/kg IV in 5% dextrose over 2 hours. Alternative: Miltefosine 50 mg PO bid (for weight >= 25 kg) for 28 days.",
        dose_method_type="FORMULA_WEIGHT_BSA",
        model_evaluation_status="National Elimination Programme single-dose protocol with renal/pregnancy safety checks.",
        supported_age_group="Children (>= 2 years) and Adults",
        supported_subtypes=["Primary Visceral Leishmaniasis", "PKDL (Post-Kala-Azar Dermal Leishmaniasis)", "HIV-VL Coinfection"],
        supported_severity=["Moderate", "Severe"],
        supported_care_setting=["Designated Kala-azar Treatment Centre / District Hospital"],
        missing_data_requirements=["Confirmed rK39 rapid test or bone marrow/splenic aspirate", "Patient weight (kg)", "Renal function (Serum Creatinine)", "Pregnancy test (Miltefosine is strictly teratogenic)"],
        subtype_prompt_guidance=None,
        exclusions=["Miltefosine is strictly contraindicated in pregnancy and women of childbearing potential without verified contraception (high teratogenicity)", "Liposomal Amphotericin B preferred in pregnancy and renal impairment"],
        is_dose_model_ready=True
    ),

    # 14. Sleeping sickness
    "sleeping_sickness": DiseaseCoverageEntry(
        disease_id="sleeping_sickness",
        disease_name="Sleeping Sickness (Human African Trypanosomiasis)",
        category="Tropical / Parasitic",
        icd_10_codes=["B56", "B56.0", "B56.1"],
        evidence_coverage="Active (WHO Guidelines for the Treatment of Human African Trypanosomiasis, 2021; International Health Travel Medicine & AIIMS Tropical Medicine Advisory).",
        evidence_sources=["WHO_HAT_2021", "AIIMS_TROPICAL_2022"],
        medicine_selection_coverage="Fexinidazole oral tablets (all stages of T.b. gambiense); NECT (Nifurtimox-Eflornithine Combination Therapy); Suramin (for first stage T.b. rhodesiense).",
        candidate_medicines=["Fexinidazole", "Eflornithine", "Nifurtimox", "Suramin"],
        dose_method_coverage="Fexinidazole for T.b. gambiense (>= 35 kg): 1,800 mg (3 tablets of 600 mg) once daily with food on days 1-4, followed by 1,200 mg (2 tablets) daily on days 5-10.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="WHO International Protocol. Not endemic in India; relevant for imported / travel medicine cases.",
        supported_age_group="Age >= 6 years and Weight >= 20 kg",
        supported_subtypes=["T.b. gambiense (West African)", "T.b. rhodesiense (East African)", "Stage 1 (Hemolymphatic)", "Stage 2 (Meningoencephalitic)"],
        supported_severity=["Stage 1", "Stage 2"],
        supported_care_setting=["Specialized Tropical Medicine Unit"],
        missing_data_requirements=["Travel history to sub-Saharan Africa", "CSF examination (white cell count and trypanosomes) for staging", "Body weight (kg)", "Food intake verification for fexinidazole"],
        subtype_prompt_guidance=None,
        exclusions=["Fexinidazole must always be taken with a substantial meal; fasting administration leads to therapeutic failure", "Not registered for local endemic Indian transmission (travel verification required)"],
        is_dose_model_ready=True
    ),

    # 15. Ringworm
    "ringworm": DiseaseCoverageEntry(
        disease_id="ringworm",
        disease_name="Ringworm (Tinea Corporis & Tinea Cruris)",
        category="Dermatological / Fungal",
        icd_10_codes=["B35", "B35.4", "B35.6"],
        evidence_coverage="Active (Indian Association of Dermatologists, Venereologists and Leprologists IADVL Guidelines on Recalcitrant Dermatophytosis in India, 2022; ICMR STW Dermatology).",
        evidence_sources=["IADVL_DERMATOPHYTE_2022", "ICMR_DERM_2021"],
        medicine_selection_coverage="Topical azoles/allylamines: Clotrimazole 1% cream, Terbinafine 1% cream, Amorolfine 0.25% cream; Systemic antifungal for extensive/recalcitrant lesions: Itraconazole PO or Terbinafine PO. Strict prohibition of topical steroid cocktails (clobetasol/betamethasone combinations).",
        candidate_medicines=["Clotrimazole", "Terbinafine", "Itraconazole", "Amorolfine"],
        dose_method_coverage="Topical: Apply thin layer twice daily for 2-4 weeks (continue 1 week after clinical clearance). Systemic: Itraconazole 100-200 mg PO once daily after full meal for 2-4 weeks.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="IADVL Guideline Algorithm. Topical steroid warning gate active.",
        supported_age_group="Adolescents and Adults",
        supported_subtypes=["Tinea Corporis (Body)", "Tinea Cruris (Groin)", "Extensive / Recalcitrant Dermatophytosis"],
        supported_severity=["Mild / Localized", "Extensive / Recurrent"],
        supported_care_setting=["Outpatient Dermatology / Primary Care"],
        missing_data_requirements=["Extent of lesions (% body surface area)", "Prior use of topical corticosteroid creams", "Liver function (ALT/AST) if systemic Itraconazole is prescribed", "Concomitant medications (CYP3A4 interactions)"],
        subtype_prompt_guidance=None,
        exclusions=["Topical fixed-dose combinations containing potent steroids (e.g. Clobetasol + Antifungal) are strictly contraindicated due to severe tinea incognito and steroid atrophy", "Itraconazole is contraindicated in heart failure (negative inotropic effect) and severe liver disease"],
        is_dose_model_ready=True
    ),

    # 16. Athlete's foot
    "athletes_foot": DiseaseCoverageEntry(
        disease_id="athletes_foot",
        disease_name="Athlete's Foot (Tinea Pedis)",
        category="Dermatological / Fungal",
        icd_10_codes=["B35.3"],
        evidence_coverage="Active (IADVL Guidelines for Superficial Fungal Infections, 2022; British Association of Dermatologists Guidelines).",
        evidence_sources=["IADVL_TINEA_PEDIS_2022", "BAD_TINEA_2021"],
        medicine_selection_coverage="Topical allylamine: Terbinafine 1% cream/gel (first line); Topical azoles: Clotrimazole 1%, Miconazole 2%; Oral Terbinafine for moccasin-type or recalcitrant infections.",
        candidate_medicines=["Terbinafine Topical", "Clotrimazole Topical", "Terbinafine Oral"],
        dose_method_coverage="Topical Terbinafine 1%: apply once or twice daily between clean, dry toes for 1-2 weeks. Oral Terbinafine (for moccasin type): 250 mg PO once daily for 2-4 weeks.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Clinical Guideline Algorithm.",
        supported_age_group="Children > 12 years and Adults",
        supported_subtypes=["Interdigital Tinea Pedis", "Moccasin-type (Chronic hyperkeratotic)", "Vesiculobullous"],
        supported_severity=["Mild", "Moderate", "Severe / Chronic"],
        supported_care_setting=["Outpatient"],
        missing_data_requirements=["Clinical subtype (interdigital vs moccasin type)", "Presence of secondary bacterial infection / cellulitis", "Diabetic foot status"],
        subtype_prompt_guidance=None,
        exclusions=["Diabetic patients with cracking and secondary cellulitis require immediate antibacterial therapy and wound care"],
        is_dose_model_ready=True
    ),

    # 17. Candidiasis
    "candidiasis": DiseaseCoverageEntry(
        disease_id="candidiasis",
        disease_name="Candidiasis (Oral Thrush, Vulvovaginal & Systemic)",
        category="Fungal / Opportunistic",
        icd_10_codes=["B37", "B37.0", "B37.3", "B37.7"],
        evidence_coverage="Active (ICMR Evidence-Based Guidelines for Management of Invasive and Mucocutaneous Fungal Infections in India, 2022; IDSA Candidiasis Guidelines).",
        evidence_sources=["ICMR_FUNGAL_2022", "IDSA_CANDIDA_2021"],
        medicine_selection_coverage="Subtype-specific: Oral thrush: Clotrimazole mouth paint / lozenges or oral Fluconazole; Vulvovaginal: single-dose Fluconazole 150 mg PO or topical Clotrimazole 100 mg vaginal pessary; Invasive / Candidemia: Echinocandins (Caspofungin / Micafungin) or IV Fluconazole.",
        candidate_medicines=["Fluconazole", "Clotrimazole", "Caspofungin", "Nystatin"],
        dose_method_coverage="Vulvovaginal: Fluconazole 150 mg PO single dose. Oral thrush: Fluconazole 100-200 mg PO daily for 7-14 days. Candidemia: Caspofungin 70 mg loading dose IV, then 50 mg daily. Renal adjustment for Fluconazole: decrease dose by 50% if CrCl <= 50 mL/min.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="ICMR Guideline Protocol with renal clearance dose-halving rule.",
        supported_age_group="All age groups",
        supported_subtypes=["Oral Thrush (Pseudomembranous)", "Vulvovaginal Candidiasis (VVC)", "Cutaneous Intertrigo", "Invasive Candidiasis / Candidemia"],
        supported_severity=["Mild", "Moderate", "Severe / Invasive"],
        supported_care_setting=["Outpatient Clinic", "Inpatient Ward / ICU"],
        missing_data_requirements=["Site of candidiasis (oral vs vaginal vs bloodstream)", "Pregnancy status (oral Fluconazole contraindicated in 1st trimester; use topical clotrimazole)", "Renal function (eGFR or CrCl)"],
        subtype_prompt_guidance="Specify whether candidiasis is Oral, Vulvovaginal, or Invasive Candidemia. Dosing and route differ fundamentally.",
        exclusions=["Oral Fluconazole is contraindicated in pregnancy (use topical clotrimazole 7-day pessary)", "Concurrent administration of Fluconazole with QT-prolonging agents (e.g. Cisapride, Terfenadine, Astemizole) is contraindicated"],
        is_dose_model_ready=True
    ),

    # 18. Diabetes
    "type_2_diabetes": DiseaseCoverageEntry(
        disease_id="type_2_diabetes",
        disease_name="Diabetes Mellitus (Type 2, Inpatient & Outpatient Glycemic Management)",
        category="Endocrine / Metabolic",
        icd_10_codes=["E11", "E11.9", "250.00"],
        evidence_coverage="Active (ICMR Guidelines for Management of Type 2 Diabetes, 2023; ADA Standards of Care 2024; KDIGO 2023 Diabetes in CKD).",
        evidence_sources=["ICMR_DIABETES_2023", "ADA_2024", "KDIGO_2023", "FDA_METFORMIN"],
        medicine_selection_coverage="First line oral: Metformin (unless eGFR < 30 mL/min/1.73m2); Second line / add-ons: SGLT2 inhibitors (Dapagliflozin/Empagliflozin), DPP-4 inhibitors (Teneligliptin/Sitagliptin), Sulfonylureas (Glimepiride/Glipizide); Inpatient: Subcutaneous Regular / Basal Insulin.",
        candidate_medicines=["Metformin", "Insulin Regular / Basal", "Glimepiride", "Teneligliptin", "Dapagliflozin"],
        dose_method_coverage="eGFR-stratified: Metformin: 500-1000 mg bid (max 2000 mg/day if eGFR >= 60; max 1000 mg/day if eGFR 30-44; contraindicated if eGFR < 30). Inpatient Insulin: Titrated according to sliding scale and baseline glucose (XGBoost research benchmark trained on MIMIC-IV demo cohort).",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Active research benchmark on MIMIC-IV demo (Inpatient Subcutaneous Insulin Regressor MAE: 5.48 units; Classifier Accuracy: 66.7%). Patient-level GroupShuffleSplit verified.",
        supported_age_group="Adults (>= 18 years)",
        supported_subtypes=["Type 2 Diabetes Mellitus - Outpatient Monotherapy", "Type 2 Diabetes with CKD Stage 1-4", "Inpatient Acute Glycemic Titration"],
        supported_severity=["Mild (HbA1c < 7.5%)", "Moderate (HbA1c 7.5-9.0%)", "Severe (HbA1c > 9.0% / Glucose > 250)"],
        supported_care_setting=["Outpatient Clinic", "Inpatient Medical Ward"],
        required_inputs=["age", "weight_kg", "labs.glucose", "labs.creatinine"],
        missing_data_requirements=["Blood Glucose (mg/dL)", "Serum Creatinine (mg/dL)", "eGFR (calculated or reported)", "HbA1c (%)", "Urine Albumin-to-Creatinine Ratio (UACR)"],
        subtype_prompt_guidance="For non-T2D cases, specify whether Type 1 DM, Gestational Diabetes, or DKA (DKA requires intensive IV insulin protocol in ICU).",
        exclusions=["DKA or HHS with metabolic acidosis contraindicates standard oral therapy", "Severe renal impairment (eGFR < 30) strictly contraindicates Metformin due to lactic acidosis risk", "Acute active hypoglycemia (Glucose < 70 mg/dL) holds all hypoglycemic agents"],
        is_dose_model_ready=True
    ),

    # 19. Hypertension
    "essential_hypertension": DiseaseCoverageEntry(
        disease_id="essential_hypertension",
        disease_name="Hypertension (Essential / Primary Hypertension)",
        category="Cardiovascular",
        icd_10_codes=["I10", "401.9"],
        evidence_coverage="Active (Indian Guidelines on Hypertension IV IGH-IV, 2022; ICMR STW for Hypertension; ACC/AHA 2020 Guidelines).",
        evidence_sources=["IGH_IV_2022", "ICMR_HTN_2022", "ACC_AHA_2020", "FDA_LISINOPRIL"],
        medicine_selection_coverage="First line monotherapy / dual therapy: Calcium Channel Blockers (Amlodipine), ARBs (Telmisartan), ACE inhibitors (Lisinopril/Enalapril), Thiazide-like diuretics (Chlorthalidone); Beta-blockers (Metoprolol) for compelling cardiac indications.",
        candidate_medicines=["Amlodipine Besylate", "Telmisartan", "Lisinopril", "Metoprolol Tartrate", "Chlorthalidone"],
        dose_method_coverage="Amlodipine: 2.5-5 mg PO once daily titrated to 10 mg; Telmisartan: 40-80 mg PO once daily; Lisinopril: 10-20 mg PO once daily (starting 2.5-5 mg if eGFR < 30); Metoprolol: 25-50 mg PO bid. Model estimate evaluated on MIMIC-IV demo.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Active research benchmark on MIMIC-IV demo (Metoprolol PO Regressor MAE: 13.9 mg; Antihypertensive Classifier Accuracy: 64.7%). GroupShuffleSplit verified.",
        supported_age_group="Adults (>= 18 years)",
        supported_subtypes=["Essential Hypertension Stage 1 (130-139 / 80-89 mmHg)", "Essential Hypertension Stage 2 (>= 140 / >= 90 mmHg)", "Hypertension with Type 2 Diabetes / Microalbuminuria", "Hypertension with CKD"],
        supported_severity=["Stage 1", "Stage 2", "Resistant Hypertension"],
        supported_care_setting=["Outpatient Clinic", "Inpatient Medical Floor"],
        required_inputs=["age", "labs.creatinine", "labs.potassium"],
        missing_data_requirements=["Blood Pressure measurements (Systolic and Diastolic mmHg)", "Serum Creatinine and eGFR", "Serum Potassium (mEq/L)", "Pregnancy status"],
        subtype_prompt_guidance="Confirm whether presentation is Routine Hypertension, Hypertensive Urgency (severe elevation without end-organ damage), or Hypertensive Emergency (with acute encephalopathy, pulmonary edema, aortic dissection - requires immediate IV ICU therapy).",
        exclusions=["Pregnancy (ACE inhibitors and ARBs are strictly contraindicated - FDA Black Box Warning for fatal fetal toxicity)", "Severe hyperkalemia (Potassium > 5.5 mEq/L contraindicates Lisinopril/Telmisartan)", "History of ACEi-induced angioedema"],
        is_dose_model_ready=True
    ),

    # 20. Asthma
    "asthma": DiseaseCoverageEntry(
        disease_id="asthma",
        disease_name="Asthma (Bronchial Asthma & Acute Exacerbation)",
        category="Respiratory / Chronic",
        icd_10_codes=["J45", "J45.9", "493.90"],
        evidence_coverage="Active (ICMR Standard Treatment Workflow for Bronchial Asthma, 2022; GINA Global Initiative for Asthma Guidelines 2023).",
        evidence_sources=["ICMR_ASTHMA_2022", "GINA_2023"],
        medicine_selection_coverage="Inhaled Corticosteroid (ICS) + Formoterol (fast-acting LABA) as preferred reliever and controller across all tracks (GINA Track 1: Budesonide-Formoterol DPI/MDI); SABA (Salbutamol) as alternative reliever in Track 2; Short-course oral Prednisolone for acute exacerbations.",
        candidate_medicines=["Budesonide + Formoterol Inhaler", "Salbutamol (Albuterol) MDI", "Prednisolone Oral", "Montelukast"],
        dose_method_coverage="Track 1 Controller/Reliever (Age >= 12): Budesonide/Formoterol (160/4.5 mcg or 200/6 mcg) 1-2 puffs as needed for symptoms; or 1 puff bid maintenance plus as needed. Acute flare: Oral Prednisolone 40-50 mg daily for 5-7 days.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="GINA 2023 / ICMR Track 1 clinical guideline algorithm with SABA monotherapy safety gate.",
        supported_age_group="Children (>= 6 years), Adolescents, and Adults",
        supported_subtypes=["Mild Intermittent Asthma", "Mild Persistent Asthma", "Moderate Persistent Asthma", "Severe Persistent Asthma", "Acute Asthma Exacerbation"],
        supported_severity=["Step 1-2", "Step 3-4", "Step 5 / Severe"],
        supported_care_setting=["Outpatient Chest Clinic", "Emergency Room (for exacerbations)"],
        missing_data_requirements=["Daytime and nighttime symptom frequency (days/week)", "Peak Expiratory Flow (PEF) or FEV1 % predicted", "SpO2 during acute exacerbation", "Current inhaler adherence and technique"],
        subtype_prompt_guidance="Specify: 1) GINA Severity Step (Step 1-5), 2) Current maintenance inhaler, and 3) Whether patient is experiencing an acute exacerbation requiring systemic corticosteroids.",
        exclusions=["SABA monotherapy (Salbutamol alone without Inhaled Corticosteroid) is no longer recommended by GINA/ICMR due to increased risk of asthma-related death and severe exacerbations", "Non-selective beta-blockers (e.g. Propranolol) and Aspirin (in Aspirin-exacerbated respiratory disease AERD) are contraindicated"],
        is_dose_model_ready=True
    ),

    # 21. Arthritis
    "arthritis": DiseaseCoverageEntry(
        disease_id="arthritis",
        disease_name="Arthritis (Osteoarthritis, Rheumatoid Arthritis, Gouty Arthritis)",
        category="Musculoskeletal / Autoimmune",
        icd_10_codes=["M15", "M16", "M17", "M05", "M06", "M10"],
        evidence_coverage="Active (Indian Rheumatology Association IRA Guidelines for Management of Rheumatoid Arthritis & Osteoarthritis, 2022; ICMR STW Musculoskeletal).",
        evidence_sources=["IRA_ARTHRITIS_2022", "ICMR_RHEUM_2021"],
        medicine_selection_coverage="Subtype-dependent: Osteoarthritis: Topical NSAIDs, Paracetamol, Oral NSAIDs (short-course, e.g. Celecoxib/Naproxen); Rheumatoid Arthritis: Conventional DMARDs (Methotrexate, Hydroxychloroquine, Sulfasalazine); Acute Gout: Colchicine, NSAIDs, Intra-articular steroid; Chronic Gout: Allopurinol / Febuxostat.",
        candidate_medicines=["Paracetamol", "Naproxen", "Methotrexate", "Hydroxychloroquine", "Colchicine", "Allopurinol"],
        dose_method_coverage="Subtype dependent. Methotrexate: 7.5-15 mg PO ONCE WEEKLY (with Folic acid 5 mg weekly); Colchicine for acute gout: 1 mg PO then 0.5 mg 1 hour later (max 1.5 mg total course); Osteoarthritis: Paracetamol 650 mg PO tid.",
        dose_method_type="WITHHELD_SUBTYPE_REQUIRED",
        model_evaluation_status="Broad clinical umbrella. Automated dosing proposal strictly withheld until exact clinical subtype and joint distribution are confirmed.",
        supported_age_group="Adults (>= 18 years)",
        supported_subtypes=["Osteoarthritis (OA - Knee, Hip, Hand)", "Rheumatoid Arthritis (RA - Seropositive/Seronegative)", "Gouty Arthritis (Acute Attack vs Chronic Tophaceous)", "Ankylosing Spondylitis"],
        supported_severity=["Mild", "Moderate", "Severe / Erosive"],
        supported_care_setting=["Outpatient Rheumatology / Orthopedics"],
        missing_data_requirements=["Exact Arthritis Subtype (Osteoarthritis vs Rheumatoid Arthritis vs Acute Gout vs Spondyloarthritis)", "Serum Uric Acid (for Gout)", "Anti-CCP / RF titer (for RA)", "Renal & Liver Function (mandatory prior to DMARDs/Colchicine)", "Complete Blood Count"],
        subtype_prompt_guidance="Arthritis cannot be treated as a single uniform task. Dosing is withheld. Please specify: 1) Is this Osteoarthritis, Rheumatoid Arthritis, or Acute Gout? 2) Joint pattern (monoarticular vs symmetrical polyarticular), and 3) Inflammatory markers (ESR/CRP/Uric acid).",
        exclusions=["Methotrexate is NEVER taken daily (daily administration causes fatal bone marrow suppression - once weekly only)", "Methotrexate is strictly contraindicated in pregnancy (teratogenic abortifacient)", "NSAIDs are contraindicated in active peptic ulcer disease and advanced CKD"],
        is_dose_model_ready=False
    ),

    # 22. Cancer
    "cancer": DiseaseCoverageEntry(
        disease_id="cancer",
        disease_name="Cancer (Malignancy - Solid Tumors & Hematologic)",
        category="Oncology",
        icd_10_codes=["C00-C97"],
        evidence_coverage="Active (ICMR Consensus Guidelines for Management of Specific Cancers in India, 2022; National Comprehensive Cancer Network NCCN Guidelines).",
        evidence_sources=["ICMR_ONCOLOGY_2022", "NCCN_2023"],
        medicine_selection_coverage="Disease and histology-specific multi-agent systemic regimens (e.g. Capecitabine, Paclitaxel, Cisplatin, Doxorubicin, Imatinib, Pembrolizumab) governed by specialized multidisciplinary tumor boards.",
        candidate_medicines=["Specialist Oncology Formulary Only"],
        dose_method_coverage="Requires Body Surface Area (Mosteller formula BSA = sqrt(height*weight/3600)), organ clearance metrics (Calvert formula for Carboplatin AUC, eGFR, LFTs), molecular biomarkers, and tumor board protocol.",
        dose_method_type="WITHHELD_SUBTYPE_REQUIRED",
        model_evaluation_status="Highly toxic antineoplastic therapy. General automated dosing is strictly withheld in decision support to prevent catastrophic clinical toxicity. Sourced evidence and staging requirements displayed.",
        supported_age_group="Adults and Pediatrics",
        supported_subtypes=["Organ-specific (Breast, Lung, Colorectal, Oral cavity, Cervix, Lymphoma, Leukemia, etc.)", "Histological Subtype & Molecular Markers (ER/PR/HER2, EGFR, ALK, KRAS)", "TNM Staging (Stage I to IV)", "Treatment Intent (Neoadjuvant, Adjuvant, Curative, Palliative)"],
        supported_severity=["Stage I", "Stage II", "Stage III", "Stage IV / Metastatic"],
        supported_care_setting=["Specialized Tertiary Cancer Centre / Multidisciplinary Tumor Board"],
        missing_data_requirements=["Primary organ site and histological diagnosis (biopsy confirmed)", "Accurate clinical and radiological TNM stage", "Body Surface Area (BSA) derived from measured height (cm) and weight (kg)", "ECOG Performance Status (0-4)", "Complete baseline renal clearance, hepatic enzymes, and cardiac ejection fraction"],
        subtype_prompt_guidance="Cancer cannot be managed as a uniform dosing task. Chemotherapy dosing carries narrow therapeutic margins and life-threatening toxicity. Please specify: 1) Primary organ site and histology, 2) TNM staging and intent, 3) Molecular markers, and 4) BSA and organ function.",
        exclusions=["All automated antineoplastic dosage output is strictly withheld. Chemotherapy must be prescribed and independently double-verified by certified medical oncologists."],
        is_dose_model_ready=False
    ),

    # 23. Scurvy
    "scurvy": DiseaseCoverageEntry(
        disease_id="scurvy",
        disease_name="Scurvy (Severe Ascorbic Acid / Vitamin C Deficiency)",
        category="Nutritional Deficiency",
        icd_10_codes=["E54"],
        evidence_coverage="Active (WHO Guidelines for Vitamin and Mineral Requirements in Human Nutrition; ICMR-National Institute of Nutrition NIN Dietary Guidelines for Indians, 2024).",
        evidence_sources=["ICMR_NIN_2024", "WHO_NUTRITION_2021"],
        medicine_selection_coverage="Oral Ascorbic Acid (Vitamin C) therapeutic replacement; Nutritional dietary rehabilitation with fresh citrus fruits and green vegetables.",
        candidate_medicines=["Ascorbic Acid (Vitamin C) Oral"],
        dose_method_coverage="Therapeutic replacement: Adults: 250-500 mg PO twice daily (or 1000 mg daily in divided doses) for 1-2 weeks, followed by 100 mg daily for several weeks until complete tissue saturation. Pediatrics: 100 mg PO three times daily.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="ICMR-NIN Therapeutic Protocol.",
        supported_age_group="Pediatrics and Adults",
        supported_subtypes=["Nutritional Scurvy", "Scurvy with gingival bleeding", "Scurvy with subperiosteal hematoma"],
        supported_severity=["Moderate", "Severe with musculoskeletal / bleeding manifestations"],
        supported_care_setting=["Outpatient / Primary Care"],
        missing_data_requirements=["Dietary assessment", "Presence of bleeding manifestations (petechiae, corkscrew hairs, hemarthrosis)", "History of renal oxalate stones (high-dose caution)"],
        subtype_prompt_guidance=None,
        exclusions=["High-dose ascorbic acid (>1g/day) should be used with caution in patients with recurrent calcium oxalate nephrolithiasis or severe renal failure"],
        is_dose_model_ready=True
    ),

    # 24. Rickets
    "rickets": DiseaseCoverageEntry(
        disease_id="rickets",
        disease_name="Rickets (Nutritional Vitamin D & Calcium Deficiency)",
        category="Nutritional / Metabolic Bone",
        icd_10_codes=["E55", "E55.0"],
        evidence_coverage="Active (Indian Academy of Pediatrics IAP Consensus Guidelines on Vitamin D Deficiency and Rickets, 2022; ICMR-NIN Guidelines).",
        evidence_sources=["IAP_VITAMIN_D_2022", "ICMR_NIN_2024"],
        medicine_selection_coverage="Cholecalciferol (Vitamin D3) therapeutic staging + Elemental Calcium supplementation (mandatory co-therapy to prevent hungry bone hypocalcemia).",
        candidate_medicines=["Cholecalciferol (Vitamin D3)", "Calcium Carbonate / Phosphate (Elemental Calcium)"],
        dose_method_coverage="Stoss therapy vs daily: Infants < 12 months: Cholecalciferol 2,000 IU/day for 12 weeks OR 60,000 IU single dose; Children >= 12 months: 60,000 IU once weekly for 6 weeks; plus Elemental Calcium 500 mg/day orally.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="IAP National Consensus Algorithm with hypercalcemia safety gate.",
        supported_age_group="Infants, Children, and Adolescents",
        supported_subtypes=["Nutritional Vitamin D Deficiency Rickets", "Nutritional Calcium-Deficiency Rickets", "Refractory / Renal Rickets (Vitamin D Resistant)"],
        supported_severity=["Mild", "Moderate", "Severe with skeletal deformities / tetany"],
        supported_care_setting=["Pediatric Outpatient / Nutrition Rehabilitation"],
        missing_data_requirements=["Serum 25-hydroxyvitamin D [25(OH)D] level", "Serum Calcium, Phosphate, and Alkaline Phosphatase (ALP)", "Age (months/years) and Weight (kg)", "Renal function (to rule out renal osteodystrophy)"],
        subtype_prompt_guidance=None,
        exclusions=["Always co-administer elemental calcium with therapeutic vitamin D to prevent hungry bone syndrome and acute hypocalcemic tetany", "Pre-existing hypercalcemia or hypervitaminosis D strictly contraindicates therapy"],
        is_dose_model_ready=True
    ),

    # 25. Beriberi
    "beriberi": DiseaseCoverageEntry(
        disease_id="beriberi",
        disease_name="Beriberi (Thiamine / Vitamin B1 Deficiency - Wet & Dry)",
        category="Nutritional / Neurological",
        icd_10_codes=["E51", "E51.1"],
        evidence_coverage="Active (WHO Guidelines for Thiamine Deficiency in Populations; ICMR-NIN Dietary Guidelines, 2024; AIIMS Emergency Medicine Protocols for Wet Beriberi).",
        evidence_sources=["WHO_THIAMINE_2021", "ICMR_NIN_2024", "AIIMS_EMERGENCY_2022"],
        medicine_selection_coverage="Thiamine Hydrochloride (Vitamin B1): IV/IM for acute Wet Beriberi (high-output cardiac failure) and Wernicke's encephalopathy; Oral Thiamine for Dry Beriberi (peripheral neuropathy) and maintenance.",
        candidate_medicines=["Thiamine Hydrochloride IV", "Thiamine Hydrochloride Oral"],
        dose_method_coverage="Wet Beriberi (Acute cardiovascular crisis): Thiamine 100-200 mg IV three times daily for 3-5 days, then 100 mg PO daily until recovery. Dry Beriberi: 100 mg PO daily for 4-6 weeks.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Emergency Nutritional Guideline. Glucose-before-thiamine safety warning active.",
        supported_age_group="All age groups",
        supported_subtypes=["Wet Beriberi (High-output heart failure, lactic acidosis, edema)", "Dry Beriberi (Symmetrical sensorimotor peripheral neuropathy)", "Wernicke-Korsakoff Syndrome"],
        supported_severity=["Moderate", "Severe / Life-threatening (Shoshin Beriberi)"],
        supported_care_setting=["Emergency Department / Medical ICU (Wet)", "Outpatient (Dry)"],
        missing_data_requirements=["Clinical presentation (presence of high-output cardiac failure, peripheral edema, or neuropathy)", "Alcohol dependence or dietary polishing history", "Concomitant glucose infusion status"],
        subtype_prompt_guidance=None,
        exclusions=["CRITICAL: In suspected thiamine deficiency, NEVER administer intravenous glucose before administering Thiamine (glucose infusion without thiamine precipitates acute fatal Wernicke's encephalopathy)"],
        is_dose_model_ready=True
    ),

    # 26. Night blindness
    "night_blindness": DiseaseCoverageEntry(
        disease_id="night_blindness",
        disease_name="Night Blindness (Nyctalopia / Vitamin A Deficiency - Xerophthalmia)",
        category="Nutritional / Ophthalmic",
        icd_10_codes=["E50", "E50.5", "H53.6"],
        evidence_coverage="Active (WHO Guidelines on Vitamin A Supplementation for Infants, Children, and Pregnant Women; National Prophylaxis Programme against Nutritional Blindness MoHFW India).",
        evidence_sources=["WHO_VITAMIN_A_2021", "MOHFW_BLINDNESS_2022"],
        medicine_selection_coverage="Therapeutic High-Dose Vitamin A (Retinyl palmitate) oral oily solution; Dietary education on dark green leafy vegetables and carotene-rich foods.",
        candidate_medicines=["Vitamin A (Retinol palmitate) Oral"],
        dose_method_coverage="Standard 3-dose therapeutic schedule (Doses on Day 1, Day 2, and Day 14): Children >= 12 months & Adults: 200,000 IU PO per dose; Infants 6-11 months: 100,000 IU PO per dose; Infants < 6 months: 50,000 IU PO per dose.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="WHO / MoHFW National Protocol with pregnancy teratogenicity gating.",
        supported_age_group="Infants, Children, and Non-pregnant adults",
        supported_subtypes=["X1A - Conjunctival xerosis", "X1B - Bitot's spots", "X2 - Corneal xerosis", "X3 - Corneal ulceration / Keratomalacia"],
        supported_severity=["Stage XN (Night blindness)", "Stage X1 (Conjunctival)", "Stage X2-X3 (Corneal Emergency)"],
        supported_care_setting=["Primary Health Centre / Community Health Centre / Ophthalmology Clinic"],
        missing_data_requirements=["Exact age in months/years", "Ocular signs (Bitot spots, corneal clouding)", "Pregnancy status (high-dose single bolus >10,000 IU is teratogenic; daily low dose required)"],
        subtype_prompt_guidance=None,
        exclusions=["High single doses (>10,000 IU) are contraindicated in pregnancy due to cranial neural crest teratogenicity; pregnant women must receive maximum 10,000 IU daily or 25,000 IU weekly for a maximum of 12 weeks"],
        is_dose_model_ready=True
    ),

    # 27. Anaemia
    "anaemia": DiseaseCoverageEntry(
        disease_id="anaemia",
        disease_name="Anaemia (Iron Deficiency, Megaloblastic, Hemolytic & Chronic Disease)",
        category="Hematological / Nutritional",
        icd_10_codes=["D50", "D51", "D52", "D53", "D64", "D64.9"],
        evidence_coverage="Active (Anemia Mukt Bharat AMB Guidelines, 2023 MoHFW India; ICMR Guidelines for Management of Severe Anemia in Pregnancy & Primary Care, 2022).",
        evidence_sources=["AMB_INDIA_2023", "ICMR_ANEMIA_2022", "WHO_ANEMIA_2023"],
        medicine_selection_coverage="Etiology-specific: Iron Deficiency: Oral Iron (Ferrous Ascorbate / Ferrous Fumarate + Folic Acid) or IV Iron (Ferric Carboxymaltose / Iron Sucrose calculated by Ganzoni formula); Megaloblastic: Cyanocobalamin / Methylcobalamin (B12) + Folic acid; Anemia of CKD: Erythropoiesis-stimulating agents (ESA) + IV Iron.",
        candidate_medicines=["Ferrous Ascorbate + Folic Acid", "Ferric Carboxymaltose IV", "Iron Sucrose IV", "Vitamin B12", "Folic Acid"],
        dose_method_coverage="Iron Deficiency Oral: 100 mg elemental iron + 500 mcg folic acid daily. Severe / Intolerant Iron Deficiency IV: Ganzoni formula Total Iron Deficit (mg) = [Body weight (kg) x (Target Hb - Actual Hb) x 2.4] + 500 mg iron stores depot.",
        dose_method_type="WITHHELD_SUBTYPE_REQUIRED",
        model_evaluation_status="Broad clinical umbrella. Dosing proposal withheld until etiology (Iron vs B12/Folate vs Hemolytic vs CKD) and baseline Hb/ferritin are entered.",
        supported_age_group="All age groups (Infants, Adolescents, Pregnant Women, Adults, Elderly)",
        supported_subtypes=["Iron Deficiency Anaemia (IDA)", "Megaloblastic Anaemia (Vitamin B12 / Folate deficiency)", "Anaemia in Pregnancy (AMB Stratification)", "Anaemia of Chronic Kidney Disease (CKD)", "Hemolytic Anaemia (Thalassemia, Sickle cell)"],
        supported_severity=["Mild (Hb 10.0-10.9 g/dL)", "Moderate (Hb 7.0-9.9 g/dL)", "Severe (Hb < 7.0 g/dL / Decompensated < 5.0 g/dL)"],
        supported_care_setting=["Outpatient Clinic / Primary Health Centre / Inpatient Hospital"],
        missing_data_requirements=["Baseline Hemoglobin (g/dL)", "Etiology / Red Cell Indices (MCV, MCH, Ferritin, Transferrin Saturation TSAT, Vitamin B12, Folate)", "Pregnancy and gestational age", "History of gastrointestinal bleeding or malabsorption"],
        subtype_prompt_guidance="Anaemia is an umbrella finding with vastly different causes. Please specify: 1) Underlying etiology (Iron deficiency vs B12/folate deficiency vs Anemia of CKD), 2) Current Hemoglobin (g/dL) and Ferritin, and 3) Pregnancy status.",
        exclusions=["Administering Folic Acid alone in uncorrected Vitamin B12 deficiency is strictly contraindicated (corrects anemia but precipitates irreversible subacute combined degeneration of the spinal cord)", "Oral iron is ineffective and IV iron requires extreme caution in active bacteremia / systemic sepsis"],
        is_dose_model_ready=False
    ),

    # 28. Heart Failure (Congestive Heart Failure / Volume Overload)
    "heart_failure": DiseaseCoverageEntry(
        disease_id="heart_failure",
        disease_name="Congestive Heart Failure / Volume Overload",
        category="Cardiovascular",
        icd_10_codes=["I50", "I50.9", "428.0", "428.9"],
        evidence_coverage="Active (ACC/AHA/HFSA 2022 Guidelines for Management of Heart Failure; FDA Prescribing Information for Furosemide; KDIGO 2023).",
        evidence_sources=["ACC_AHA_2020", "FDA_FUROSEMIDE"],
        medicine_selection_coverage="Loop diuretics (Furosemide / Torsemide) for volume congestion; Guideline-directed medical therapy (GDMT): ARNI/ACEi/ARB, Beta-blockers (Metoprolol succinate/Carvedilol), MRA (Spironolactone), SGLT2i (Dapagliflozin/Empagliflozin).",
        candidate_medicines=["Furosemide", "Metoprolol Tartrate", "Spironolactone"],
        dose_method_coverage="Loop diuretic guideline dosing conditional on kidney status, urine output, and serum potassium. Retrospective benchmark trained on MIMIC-IV demo cohort.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="Active research benchmark on MIMIC-IV demo (Furosemide IV Regressor MAE: 18.2 mg; Heart Failure Classifier Accuracy: 62.5%). GroupShuffleSplit verified.",
        supported_age_group="Adults (>= 18 years)",
        supported_subtypes=["Heart Failure with Reduced Ejection Fraction (HFrEF)", "Heart Failure with Preserved Ejection Fraction (HFpEF)", "Acute Decompensated Heart Failure"],
        supported_severity=["NYHA Class II", "NYHA Class III", "NYHA Class IV"],
        supported_care_setting=["Inpatient Medical Ward / ICU / Heart Failure Clinic"],
        required_inputs=["age", "weight_kg", "labs.creatinine", "labs.potassium"],
        missing_data_requirements=["Serum Creatinine (mg/dL)", "Serum Potassium (mEq/L)", "Patient body weight (kg)", "Signs of volume overload / BNP"],
        subtype_prompt_guidance="Specify ejection fraction phenotype (HFrEF vs HFpEF) and acute congestion status.",
        exclusions=["Anuria or severe uncorrected hypokalemia (< 3.0 mEq/L) contraindicates loop diuretics", "Severe aortic stenosis without monitoring"],
        is_dose_model_ready=True
    ),

    # 29. Acute Viral Infection (URTI, Viral Fever, Influenza)
    "viral_infection": DiseaseCoverageEntry(
        disease_id="viral_infection",
        disease_name="Acute Viral Infection (URTI, Viral Fever & Influenza)",
        category="Respiratory / Infectious Disease",
        icd_10_codes=["B34.9", "J06.9", "J09", "J10", "J11"],
        evidence_coverage="Active (ICMR Standard Treatment Workflow for Acute Viral Infections, Upper Respiratory Tract Infections & Influenza, 2022; WHO Guidelines for Pharmacological Management of Pandemic Influenza).",
        evidence_sources=["ICMR_VIRAL_2022", "WHO_INFLUENZA_2022"],
        medicine_selection_coverage="Guideline-directed symptomatic & antiviral therapy: Paracetamol for pyrexia/myalgia; Cetirizine for rhinitis; Oral Rehydration Salts (ORS) for fluid support; Oseltamivir (Tamiflu) for confirmed/high-risk Influenza within 48h. Routine empirical antibiotics are strictly withheld (Antimicrobial Stewardship).",
        candidate_medicines=["Paracetamol (Acetaminophen) PO", "Cetirizine Hydrochloride PO", "Oseltamivir Phosphate (Tamiflu) PO", "Oral Rehydration Salts (ORS)", "Dextromethorphan HBr Syrup"],
        dose_method_coverage="Antipyretic: Paracetamol 500-650 mg PO q6-8h prn (max 3000-4000 mg/day). Antihistamine: Cetirizine 10 mg PO once daily at bedtime. Confirmed Influenza: Oseltamivir 75 mg PO twice daily for 5 days (initiate <= 48h of onset). Antibiotics withheld.",
        dose_method_type="GUIDELINE_ALGORITHM",
        model_evaluation_status="ICMR 2022 / WHO Clinical Practice Guideline Algorithm with strict Antimicrobial Stewardship safety gating.",
        supported_age_group="Pediatrics (>= 6 months), Adolescents, Adults, and Elderly",
        supported_subtypes=["Viral Upper Respiratory Tract Infection (URTI)", "Acute Viral Fever / Syndrome", "Seasonal Influenza (Flu A / Flu B)", "Viral Pharyngitis & Rhinorrhea"],
        supported_severity=["Mild / Uncomplicated", "Moderate", "Severe / High Risk (Elderly, Immunocompromised)"],
        supported_care_setting=["Outpatient Clinic / Primary Health Centre / Emergency Department"],
        required_inputs=["age", "weight_kg"],
        missing_data_requirements=["Duration of symptoms (days)", "Presence of high-risk comorbidities (asthma, COPD, diabetes, pregnancy)", "SpO2 (pulse oximetry) to rule out lower respiratory involvement", "Liver function status if high-dose paracetamol"],
        subtype_prompt_guidance="Specify: 1) Duration of fever/symptoms, 2) Presence of lower respiratory symptoms (dyspnea, SpO2 < 94%), and 3) Whether high-risk for severe influenza requiring Neuraminidase Inhibitor (Oseltamivir).",
        exclusions=[
            "Aspirin (Acetylsalicylic Acid) is STRICTLY CONTRAINDICATED in children and adolescents (< 19 years) with viral illness due to danger of fatal Reye's Syndrome (acute encephalopathy and fatty liver)",
            "Routine empirical antibiotics (Azithromycin, Amoxicillin-Clavulanate, Cefixime) are strictly contraindicated/withheld for uncomplicated viral infection to prevent superbug resistance and adverse drug events",
            "NSAIDs (Ibuprofen, Diclofenac) are withheld in suspected Dengue or viral hemorrhagic fevers due to severe bleeding risk"
        ],
        is_dose_model_ready=True
    )
}

# Attach rich clinical treatment protocols & merge additional diseases
from app.evidence.disease_protocols import CLINICAL_PROTOCOLS, get_additional_diseases

for dis_id, protocols in CLINICAL_PROTOCOLS.items():
    if dis_id in DISEASE_CATALOGUE:
        DISEASE_CATALOGUE[dis_id].treatment_protocols = protocols

DISEASE_CATALOGUE.update(get_additional_diseases())

# Alias mapping dictionary
DISEASE_ALIASES: Dict[str, str] = {
    "asthma": "asthma",
    "bronchial_asthma": "asthma",
    "acute_asthma": "asthma",
    "viral": "viral_infection",
    "viral_infection": "viral_infection",
    "viral_fever": "viral_infection",
    "influenza": "viral_infection",
    "flu": "viral_infection",
    "urti": "viral_infection",
    "common_cold": "common_cold",
    "diabetes": "type_2_diabetes",
    "t2d": "type_2_diabetes",
    "t2dm": "type_2_diabetes",
    "type_2_diabetes": "type_2_diabetes",
    "hypertension": "essential_hypertension",
    "htn": "essential_hypertension",
    "essential_hypertension": "essential_hypertension",
    "heart_failure": "heart_failure",
    "chf": "heart_failure",
    "gerd": "gerd",
    "acid_reflux": "gerd",
    "peptic_ulcer": "gerd",
    "uti": "urinary_tract_infection",
    "urinary_tract_infection": "urinary_tract_infection",
    "cystitis": "urinary_tract_infection",
    "dyslipidemia": "dyslipidemia",
    "cholesterol": "dyslipidemia",
    "high_cholesterol": "dyslipidemia",
    "hyperlipidemia": "dyslipidemia",
    "hypothyroidism": "hypothyroidism",
    "thyroid": "hypothyroidism",
    "hypothyroid": "hypothyroidism",
    "acute_gastroenteritis": "acute_gastroenteritis",
    "gastroenteritis": "acute_gastroenteritis",
    "diarrhea": "acute_gastroenteritis",
    "loose_motion": "acute_gastroenteritis",
    "migraine": "migraine",
    "headache": "migraine",
    "allergic_rhinitis": "allergic_rhinitis_urticaria",
    "allergic_rhinitis_urticaria": "allergic_rhinitis_urticaria",
    "allergy": "allergic_rhinitis_urticaria",
    "urticaria": "allergic_rhinitis_urticaria",
    "copd": "copd"
}

def get_disease_entry(disease_id: str) -> Optional[DiseaseCoverageEntry]:
    if not disease_id:
        return None
    clean_id = disease_id.strip().lower().replace("-", "_").replace(" ", "_")
    target_id = DISEASE_ALIASES.get(clean_id, clean_id)
    if target_id in DISEASE_CATALOGUE:
        return DISEASE_CATALOGUE[target_id]
    for k, v in DISEASE_CATALOGUE.items():
        if k in clean_id or clean_id in k or clean_id in v.disease_name.lower():
            return v
    return None

def get_all_diseases() -> List[DiseaseCoverageEntry]:
    return list(DISEASE_CATALOGUE.values())

