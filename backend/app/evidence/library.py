from typing import List, Dict
from pydantic import BaseModel

class ClinicalGuidelineChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    organization: str
    url: str
    publication_year: int
    review_date: str
    applicable_population: str
    disease_tags: List[str]
    medicine_tags: List[str]
    section_name: str
    text: str
    citation: str

INITIAL_EVIDENCE_LIBRARY: List[ClinicalGuidelineChunk] = [
    # 1. ICMR STW Diabetes 2023 & ADA 2024
    ClinicalGuidelineChunk(
        chunk_id="ICMR_T2D_01",
        doc_id="ICMR_T2D_2023",
        title="ICMR Guidelines for Management of Type 2 Diabetes",
        organization="Indian Council of Medical Research (ICMR)",
        url="https://www.icmr.gov.in/standard-treatment-workflows-stws",
        publication_year=2023,
        review_date="2024-01-15",
        applicable_population="Adults with Type 2 Diabetes in Indian Clinical Practice",
        disease_tags=["type_2_diabetes", "diabetes"],
        medicine_tags=["Metformin", "Insulin", "Glimepiride", "Teneligliptin"],
        section_name="First-line Pharmacotherapy & Renal Cutoffs",
        text="Metformin is the first-line oral pharmacological agent for glycemic management in Type 2 Diabetes. Initial dose is 500 mg once or twice daily with meals, titrated by 500 mg weekly to a target dose of 1500-2000 mg/day in divided doses. Renal safety thresholds: If eGFR is 45-59 mL/min/1.73m2, continue therapy with close monitoring (every 3-6 months). If eGFR is 30-44 mL/min/1.73m2, maximum recommended dose is 1000 mg/day; do not initiate therapy in new patients. If eGFR is < 30 mL/min/1.73m2, Metformin is strictly contraindicated due to elevated risk of lactic acidosis.",
        citation="ICMR Guidelines for Management of Type 2 Diabetes (2023). Indian Council of Medical Research, New Delhi."
    ),
    ClinicalGuidelineChunk(
        chunk_id="ADA_T2D_INPATIENT",
        doc_id="ADA_2024",
        title="Standards of Care in Diabetes—2024: Hospital Care",
        organization="American Diabetes Association (ADA)",
        url="https://doi.org/10.2337/dc24-S009",
        publication_year=2024,
        review_date="2024-01-15",
        applicable_population="Hospitalized adult diabetic patients",
        disease_tags=["type_2_diabetes", "inpatient_glycemia"],
        medicine_tags=["Insulin", "Regular Insulin", "Basal Insulin"],
        section_name="Inpatient Glycemic Targets and Sliding Scale Titration",
        text="For non-critically ill hospitalized patients, basal insulin or a basal-plus-bolus correction regimen is preferred over sliding-scale insulin alone. Preprandial glycemic target is 100-140 mg/dL, with random/postprandial glucose < 180 mg/dL. Subcutaneous regular insulin correction algorithms should be scaled according to insulin sensitivity and body weight. If blood glucose is < 70 mg/dL, all antihyperglycemic agents must be temporarily held and Rule of 15 (15-20g rapid-acting oral glucose or IV 50% dextrose) instituted.",
        citation="American Diabetes Association. 16. Diabetes Care in the Hospital: Standards of Care in Diabetes—2024. Diabetes Care 2024;47(Suppl. 1):S295–S306."
    ),

    # 2. Indian Guidelines on Hypertension (IGH-IV) & CDSCO Lisinopril
    ClinicalGuidelineChunk(
        chunk_id="IGH_IV_HTN_01",
        doc_id="IGH_IV_2022",
        title="Indian Guidelines on Hypertension - IV (IGH-IV)",
        organization="Association of Physicians of India & Hypertension Society of India",
        url="https://www.japi.org/indian-guidelines-on-hypertension-iv",
        publication_year=2022,
        review_date="2024-03-10",
        applicable_population="Adults with Essential Hypertension in India",
        disease_tags=["essential_hypertension", "hypertension"],
        medicine_tags=["Amlodipine", "Telmisartan", "Lisinopril", "Chlorthalidone"],
        section_name="Stepped Antihypertensive Initiation and Combination Therapy",
        text="Initial pharmacotherapy for Stage 1 hypertension consists of a low-dose single agent: Calcium Channel Blocker (Amlodipine 2.5-5 mg once daily), Angiotensin Receptor Blocker (Telmisartan 40 mg once daily), or Thiazide diuretic (Chlorthalidone 12.5 mg once daily). For Stage 2 hypertension (BP >= 140/90 mmHg or >= 20/10 mmHg above goal), initial dual combination therapy is strongly recommended. Target blood pressure in most Indian adults is < 130/80 mmHg. In diabetic kidney disease, an ARB or ACE inhibitor is mandatory first-line to retard albuminuria progression.",
        citation="Indian Guidelines on Hypertension-IV. J Assoc Physicians India 2022;70(Suppl 1):1-48."
    ),
    ClinicalGuidelineChunk(
        chunk_id="CDSCO_ACEI_SAFETY",
        doc_id="CDSCO_LISINOPRIL",
        title="CDSCO Prescribing Information - Lisinopril Tablets",
        organization="Central Drugs Standard Control Organisation (CDSCO)",
        url="https://cdsco.gov.in/opencms/opencms/en/Notifications/Prescribing-Information/",
        publication_year=2022,
        review_date="2024-02-01",
        applicable_population="Adults prescribed ACE inhibitors in India",
        disease_tags=["essential_hypertension", "heart_failure"],
        medicine_tags=["Lisinopril", "ACE Inhibitors"],
        section_name="Black Box Warnings & Electrolyte Precautions",
        text="Lisinopril carries a Boxed Warning: When pregnancy is detected, discontinue Lisinopril as soon as possible. Drugs that act directly on the renin-angiotensin system can cause serious fetal and neonatal injury and death (oligohydramnios, skull hypoplasia, renal failure). Contraindications include history of angioedema and baseline hyperkalemia (Potassium > 5.5 mEq/L). In patients with severe renal impairment (eGFR < 30 mL/min), initial dose should be reduced to 2.5-5 mg once daily with serial serum potassium and creatinine monitoring at 1-2 weeks.",
        citation="CDSCO Prescribing Information. Lisinopril Tablets USP. Ministry of Health & Family Welfare, Government of India."
    ),

    # 3. National Vector Borne Disease Control Programme (NVBDCP) - Malaria
    ClinicalGuidelineChunk(
        chunk_id="NVBDCP_MALARIA_01",
        doc_id="NVBDCP_MALARIA_2023",
        title="National Drug Policy on Malaria - 2023",
        organization="National Vector Borne Disease Control Programme (NVBDCP)",
        url="https://nvbdcp.gov.in/index4.php?lang=1&level=0&linkid=420&lid=3699",
        publication_year=2023,
        review_date="2024-02-15",
        applicable_population="Patients diagnosed with confirmed Plasmodium malaria in India",
        disease_tags=["malaria"],
        medicine_tags=["Artemether-Lumefantrine", "Artesunate", "Chloroquine", "Primaquine"],
        section_name="Species-Specific Treatment Regimens in India",
        text="1. Uncomplicated P. falciparum: Artemether 20 mg + Lumefantrine 120 mg (ACT) fixed-dose tablets administered as a 6-dose schedule over 3 days (taken with fatty meal or milk for absorption). Single-dose Primaquine 0.25 mg/kg body weight on Day 2 as a gametocytocidal agent (except in pregnancy and infants < 6 months). In the North Eastern states, Artemether-Lumefantrine is the exclusive first-line ACT.\n2. P. vivax: Chloroquine 25 mg base/kg body weight divided over 3 days (10 mg/kg Day 1, 10 mg/kg Day 2, 5 mg/kg Day 3) plus Primaquine 0.25 mg/kg/day daily for 14 days for radical cure. Primaquine MUST be preceded by G6PD status testing; G6PD-deficient patients risk severe acute intravascular hemolysis.\n3. Severe / Cerebral Malaria: Intravenous Artesunate 2.4 mg/kg IV on admission (time 0), repeated at 12h and 24h, then once daily until oral switch is tolerated.",
        citation="NVBDCP National Drug Policy on Malaria (2023). Directorate General of Health Services, MoHFW, New Delhi."
    ),

    # 4. National Tuberculosis Elimination Programme (NTEP) - Tuberculosis
    ClinicalGuidelineChunk(
        chunk_id="NTEP_TB_01",
        doc_id="NTEP_INDIA_2023",
        title="NTEP Guidelines on Management of Tuberculosis in India",
        organization="Central TB Division, Ministry of Health and Family Welfare",
        url="https://tbcindia.gov.in",
        publication_year=2023,
        review_date="2024-01-20",
        applicable_population="Adult and adolescent patients with drug-sensitive tuberculosis",
        disease_tags=["tuberculosis", "tb"],
        medicine_tags=["Isoniazid", "Rifampicin", "Pyrazinamide", "Ethambutol", "Pyridoxine"],
        section_name="Daily Weight-Banded Fixed-Dose Combination (FDC) Regimen",
        text="Daily fixed-dose combination (FDC) tablets are standard for new drug-sensitive pulmonary and extrapulmonary tuberculosis: 2 months of HRZE (Isoniazid 75 mg + Rifampicin 150 mg + Pyrazinamide 400 mg + Ethambutol 275 mg) in the intensive phase, followed by 4 months of HRE (Isoniazid + Rifampicin + Ethambutol) in the continuation phase.\nDosing is strictly weight-banded: 25-34 kg: 2 FDC tabs/day; 35-49 kg: 3 tabs/day; 50-64 kg: 4 tabs/day; 65-74 kg: 5 tabs/day; >=75 kg: 6 tabs/day. Pyridoxine (Vitamin B6) 20-40 mg daily must be co-prescribed to prevent isoniazid-induced peripheral neuropathy, especially in diabetics, alcoholics, and malnourished patients. Baseline LFTs are mandatory. If ALT/AST rises > 3x upper limit of normal with nausea/jaundice or > 5x without symptoms, hepatotoxic drugs (PZA, INH, RIF) must be immediately halted.",
        citation="National Tuberculosis Elimination Programme (NTEP). Technical and Operational Guidelines for TB Control in India (2023). Ministry of Health & Family Welfare."
    ),

    # 5. ICMR Dengue Clinical Management
    ClinicalGuidelineChunk(
        chunk_id="ICMR_DENGUE_01",
        doc_id="ICMR_DENGUE_2022",
        title="Clinical Management Guidelines for Dengue Fever",
        organization="Indian Council of Medical Research (ICMR) & NVBDCP",
        url="https://nvbdcp.gov.in/index4.php?lang=1&level=0&linkid=431&lid=3715",
        publication_year=2022,
        review_date="2024-03-01",
        applicable_population="Pediatric and adult patients presenting with suspected/confirmed Dengue",
        disease_tags=["dengue"],
        medicine_tags=["Paracetamol", "Normal Saline", "Ringer Lactate"],
        section_name="Judicious Fluid Management and Absolute NSAID Contraindication",
        text="The clinical management of dengue hinges upon timely, calculated fluid therapy and vigilance for warning signs (abdominal pain, persistent vomiting, mucosal bleeding, clinical fluid accumulation, lethargy, hematocrit rise with platelet drop).\nAntipyretic therapy: Paracetamol 500-650 mg PO q6h (max 3g/day in adults, 10-15 mg/kg/dose in children). All NSAIDs (Aspirin, Ibuprofen, Diclofenac, Mefenamic acid) and intramuscular injections are STRICTLY CONTRAINDICATED due to high risk of severe gastrointestinal hemorrhage and acute platelet dysfunction.\nIntravenous fluid protocol for hospitalized patients with warning signs: Initiate isotonic crystalloids (Ringer's Lactate or 0.9% Normal Saline) at 5-7 mL/kg/hour for 1-2 hours, titrating down to 3-5 mL/kg/h as vital signs and hematocrit normalize. Prophylactic platelet transfusions are NOT recommended for platelet counts > 10,000/mcL in the absence of active systemic bleeding.",
        citation="ICMR-NVBDCP Guidelines for Clinical Management of Dengue (2022). National Vector Borne Disease Control Programme, New Delhi."
    ),

    # 6. ICMR STW - Community-Acquired Pneumonia
    ClinicalGuidelineChunk(
        chunk_id="ICMR_CAP_01",
        doc_id="ICMR_CAP_2022",
        title="ICMR Standard Treatment Workflow: Community-Acquired Pneumonia (CAP)",
        organization="Indian Council of Medical Research (ICMR)",
        url="https://www.icmr.gov.in/standard-treatment-workflows-stws",
        publication_year=2022,
        review_date="2024-02-10",
        applicable_population="Adults presenting with Community-Acquired Pneumonia",
        disease_tags=["pneumonia"],
        medicine_tags=["Amoxicillin-Clavulanate", "Azithromycin", "Ceftriaxone", "Levofloxacin"],
        section_name="Stratification by CURB-65 and Care Setting",
        text="Empiric antibiotic selection in adult CAP must be guided by severity score (CURB-65: Confusion, Urea > 19 mg/dL, Respiratory rate >= 30, BP < 90/60 mmHg, Age >= 65):\n1. Outpatient (CURB-65 = 0-1): Oral Amoxicillin-Clavulanic acid 625 mg PO three times daily (or 1g PO twice daily) PLUS Azithromycin 500 mg PO once daily for 5-7 days.\n2. Inpatient Medical Ward (CURB-65 = 2): Intravenous Ceftriaxone 1-2g IV once daily PLUS Azithromycin 500 mg IV or PO once daily.\n3. Inpatient ICU (CURB-65 >= 3 or septic shock): IV Piperacillin-Tazobactam 4.5g IV q6h (or Meropenem 1g IV q8h) PLUS IV Azithromycin 500 mg daily or IV Levofloxacin 750 mg daily.\nIn penicillin-allergic patients, oral or IV respiratory fluoroquinolone (Levofloxacin 500-750 mg daily) is recommended with renal dose adjustments.",
        citation="ICMR Standard Treatment Workflows. Community Acquired Pneumonia (2022). Indian Council of Medical Research."
    ),

    # 7. ICMR Enteric Fever (Typhoid)
    ClinicalGuidelineChunk(
        chunk_id="ICMR_TYPHOID_01",
        doc_id="ICMR_TYPHOID_2022",
        title="Evidence-Based Treatment of Enteric Fever in Indian Clinical Practice",
        organization="Indian Council of Medical Research (ICMR)",
        url="https://www.icmr.gov.in/standard-treatment-workflows-stws",
        publication_year=2022,
        review_date="2024-02-20",
        applicable_population="Patients with confirmed or suspected Salmonella enterica serovar Typhi",
        disease_tags=["typhoid"],
        medicine_tags=["Azithromycin", "Ceftriaxone", "Cefixime"],
        section_name="Antimicrobial Resistance & First-Line Regimens",
        text="Due to extensive quinolone resistance (>85% nalidixic acid resistance / elevated ciprofloxacin MIC) across India, Ciprofloxacin and Ofloxacin are NO LONGER recommended as empiric first-line therapy for enteric fever.\nRecommended first-line therapy:\n- Uncomplicated / Outpatient Enteric Fever: Oral Azithromycin 20 mg/kg/day (Adult dose: 1g PO on Day 1, followed by 500 mg PO once daily on Days 2-7, total 7 days) OR Oral Cefixime 20 mg/kg/day (Adult dose: 400 mg PO twice daily for 14 days).\n- Complicated / Severe / Inpatient Enteric Fever: Intravenous Ceftriaxone 50-75 mg/kg/day (Adult dose: 2g IV once daily or 1g IV twice daily) for 10-14 days. Defervescence typically occurs within 4-6 days.",
        citation="ICMR Guidelines on Treatment of Antimicrobial Resistance in Enteric Fever (2022). ICMR AMR Surveillance Network."
    ),

    # 8. Anemia Mukt Bharat - Anaemia
    ClinicalGuidelineChunk(
        chunk_id="AMB_ANEMIA_01",
        doc_id="AMB_INDIA_2023",
        title="Anemia Mukt Bharat (AMB) Clinical Management Guidelines",
        organization="Ministry of Health and Family Welfare (MoHFW), Government of India",
        url="https://anemiamuktbharat.info",
        publication_year=2023,
        review_date="2024-03-01",
        applicable_population="Children, adolescents, pregnant women, and adults with nutritional anemia",
        disease_tags=["anaemia", "anemia"],
        medicine_tags=["Ferrous Ascorbate", "Ferric Carboxymaltose", "Iron Sucrose", "Folic Acid", "Cyanocobalamin"],
        section_name="Etiology Classification & Ganzoni Parenteral Replacement",
        text="Anemia must be classified prior to treatment: Microcytic hypochromic (iron deficiency, thalassemia), Macrocytic (Vitamin B12/Folate deficiency), or Normocytic (chronic disease, hemolysis).\n1. Mild to Moderate Iron Deficiency (Hb 7.0-10.9 g/dL): Oral elemental iron 100-200 mg daily (Ferrous Ascorbate or Ferrous Fumarate) + 500 mcg Folic acid, taken on an empty stomach or with Vitamin C, continued for 3 months after Hb normalizes.\n2. Severe Iron Deficiency (Hb < 7.0 g/dL or oral intolerance / second-third trimester pregnancy): Intravenous Iron Sucrose or Ferric Carboxymaltose calculated using the Ganzoni Formula: Total Iron Deficit (mg) = [Body weight (kg) x (Target Hb - Actual Hb g/dL) x 2.4] + 500 mg (iron store depot).\n3. Macrocytic Megaloblastic Anemia: Always verify Vitamin B12 before administering high-dose folic acid alone; treating B12 deficiency with folic acid alone corrects hematologic parameters but precipitates subacute combined degeneration of the spinal cord.",
        citation="Anemia Mukt Bharat Guidelines (2023). Ministry of Health and Family Welfare, Government of India."
    ),

    # 9. IADVL Dermatophytosis (Ringworm & Athlete's Foot)
    ClinicalGuidelineChunk(
        chunk_id="IADVL_TINEA_01",
        doc_id="IADVL_DERM_2022",
        title="IADVL Consensus Guidelines on Management of Dermatophytosis in India",
        organization="Indian Association of Dermatologists, Venereologists and Leprologists (IADVL)",
        url="https://ijdvl.com",
        publication_year=2022,
        review_date="2024-01-30",
        applicable_population="Patients presenting with Tinea corporis, cruris, or pedis in India",
        disease_tags=["ringworm", "athletes_foot"],
        medicine_tags=["Clotrimazole", "Terbinafine", "Itraconazole", "Luliconazole"],
        section_name="Rational Antifungal Therapy & Ban on Topical Steroid FDCs",
        text="India is experiencing an epidemic of recalcitrant, extensive dermatophytosis driven by rampant over-the-counter use of topical fixed-dose combinations (FDCs) containing super-potent corticosteroids (Clobetasol, Betamethasone). Topical steroid formulations are STRICTLY CONTRAINDICATED in fungal infections; they cause tinea incognito, steroid-induced rosacea, atrophy, and drug recalcitrance.\nManagement Protocol:\n- Localized Tinea: Topical allylamines (Terbinafine 1% cream) or azoles (Luliconazole 1%, Clotrimazole 1%) applied twice daily for 2-4 weeks (continued 1-2 weeks after complete erythema resolution).\n- Extensive or Recalcitrant Tinea: Systemic Itraconazole 100-200 mg PO once daily after a heavy meal (requires gastric acidity for absorption) for 3-4 weeks. Monitor hepatic transaminases. Avoid in congestive heart failure. Oral Terbinafine 250 mg daily is an alternative where local Trichophyton indotineae resistance is absent.",
        citation="IADVL Guidelines on Management of Dermatophytosis in India. Indian J Dermatol Venereol Leprol 2022;88:145-168."
    ),

    # 10. ICMR-NIN Nutritional Deficiencies (Scurvy, Rickets, Beriberi, Night Blindness)
    ClinicalGuidelineChunk(
        chunk_id="ICMR_NIN_MICRONUTRIENTS",
        doc_id="ICMR_NIN_2024",
        title="Dietary Guidelines for Indians & Micronutrient Therapeutic Deficiencies",
        organization="ICMR - National Institute of Nutrition (NIN)",
        url="https://www.nin.res.in",
        publication_year=2024,
        review_date="2024-02-15",
        applicable_population="Pediatric and adult patients with clinically manifest vitamin deficiencies",
        disease_tags=["scurvy", "rickets", "beriberi", "night_blindness"],
        medicine_tags=["Ascorbic Acid", "Cholecalciferol", "Thiamine", "Vitamin A", "Elemental Calcium"],
        section_name="Therapeutic Replacement Protocols for Manifest Deficiencies",
        text="1. Scurvy (Vitamin C Deficiency): Therapeutic replacement requires Ascorbic Acid 250-500 mg PO twice daily for adults (100 mg tid for pediatrics) for 2 weeks, then 100 mg daily until full healing.\n2. Rickets (Vitamin D Deficiency): Cholecalciferol (Vitamin D3) 60,000 IU once weekly for 6 weeks (children >= 1 year), PLUS mandatory elemental calcium 500 mg/day orally to prevent hypocalcemic tetany (hungry bone syndrome).\n3. Beriberi (Thiamine / Vitamin B1 Deficiency): Wet Beriberi (acute high-output heart failure / lactic acidosis) is an extreme medical emergency: Thiamine Hydrochloride 100-200 mg IV three times daily for 3-5 days. CRITICAL WARNING: In suspected thiamine deficiency or malnutrition, intravenous glucose must NEVER be administered before Thiamine; giving glucose without thiamine precipitates acute fatal Wernicke's encephalopathy.\n4. Night Blindness / Xerophthalmia (Vitamin A Deficiency): High-dose therapeutic Vitamin A oral oily solution on Days 1, 2, and 14 (200,000 IU per dose for children >= 12 months & adults; 100,000 IU for infants 6-11 months; 50,000 IU for infants < 6 months). In pregnant women, single doses > 10,000 IU are strictly contraindicated due to teratogenicity; use daily dose < 10,000 IU.",
        citation="ICMR-National Institute of Nutrition (NIN). Dietary Guidelines for Indians & Micronutrient Protocol (2024). ICMR, Hyderabad."
    ),

    # 11. ICMR STW - Bronchial Asthma
    ClinicalGuidelineChunk(
        chunk_id="ICMR_ASTHMA_01",
        doc_id="ICMR_ASTHMA_2022",
        title="ICMR Standard Treatment Workflow: Bronchial Asthma in Adults and Children",
        organization="Indian Council of Medical Research (ICMR)",
        url="https://www.icmr.gov.in/standard-treatment-workflows-stws",
        publication_year=2022,
        review_date="2024-03-01",
        applicable_population="Patients with bronchial asthma across primary and tertiary care in India",
        disease_tags=["asthma"],
        medicine_tags=["Budesonide", "Formoterol", "Salbutamol", "Prednisolone"],
        section_name="Inhaled Corticosteroid-Formoterol Anti-Inflammatory Reliever Strategy",
        text="In accordance with ICMR and GINA Track 1 recommendations, short-acting beta-agonist (SABA, e.g. Salbutamol) monotherapy is NO LONGER recommended for asthma due to increased risk of severe exacerbations and asthma-related mortality.\nThe preferred regimen across Step 1 to Step 4 is Inhaled Corticosteroid (ICS) + Formoterol (e.g. Budesonide 160-200 mcg + Formoterol 4.5-6 mcg) as both maintenance and reliever. For acute asthma exacerbations in primary care, administer oxygen to target SpO2 93-95%, nebulized Salbutamol 2.5-5 mg + Ipratropium 0.5 mg, and initiate systemic oral Prednisolone 40-50 mg daily for 5-7 days. Non-selective beta-blockers and aspirin in AERD are strictly contraindicated.",
        citation="ICMR Standard Treatment Workflows. Bronchial Asthma (2022). Indian Council of Medical Research."
    ),

    # 12. Indian Rheumatology Association (IRA) - Arthritis
    ClinicalGuidelineChunk(
        chunk_id="IRA_ARTHRITIS_01",
        doc_id="IRA_RHEUM_2022",
        title="IRA Guidelines for the Management of Rheumatoid Arthritis & Acute Gout",
        organization="Indian Rheumatology Association (IRA)",
        url="https://indianjrheumatol.com",
        publication_year=2022,
        review_date="2024-01-25",
        applicable_population="Adults presenting with arthritis in Indian clinical practice",
        disease_tags=["arthritis"],
        medicine_tags=["Methotrexate", "Hydroxychloroquine", "Colchicine", "Naproxen", "Allopurinol"],
        section_name="Subtype Differentiation, Weekly Methotrexate, and Colchicine Gating",
        text="Arthritis requires rigorous subtype differentiation prior to therapy:\n1. Rheumatoid Arthritis: Anchor DMARD is Methotrexate (MTX). MTX is administered ONCE WEEKLY (initial dose 7.5-15 mg/week PO, titrated to 20-25 mg/week). DAILY METHOTREXATE IS FATAL due to bone marrow aplasia and severe mucositis. Co-administer Folic Acid 5 mg weekly (taken 24h after MTX). MTX is strictly contraindicated in pregnancy (teratogenic abortifacient) and severe liver disease.\n2. Acute Gouty Arthritis: Initiate low-dose Colchicine (1 mg PO stat, followed by 0.5 mg 1 hour later, max 1.5 mg in 24 hours) or short-term NSAIDs (Naproxen 500 mg bid). Colchicine dose must be halved in moderate CKD and avoided in severe renal failure. Never initiate Allopurinol during an acute gout flare (precipitates flare worsening); start Allopurinol 1-2 weeks after flare resolution with Colchicine prophylaxis.",
        citation="Indian Rheumatology Association (IRA). Guidelines for Management of Rheumatoid Arthritis & Gout (2022). Indian J Rheumatol."
    ),

    # 13. National Kala-azar Elimination Programme NVBDCP
    ClinicalGuidelineChunk(
        chunk_id="NVBDCP_VL_01",
        doc_id="NVBDCP_VL_2022",
        title="Guidelines for Clinical Management of Visceral Leishmaniasis (Kala-Azar) in India",
        organization="National Vector Borne Disease Control Programme (NVBDCP)",
        url="https://nvbdcp.gov.in/index4.php?lang=1&level=0&linkid=427&lid=3707",
        publication_year=2022,
        review_date="2024-02-05",
        applicable_population="Patients diagnosed with confirmed Visceral Leishmaniasis in endemic states (Bihar, Jharkhand, West Bengal, UP)",
        disease_tags=["kala_azar"],
        medicine_tags=["Liposomal Amphotericin B", "Miltefosine", "Paromomycin"],
        section_name="Single-Dose Liposomal Amphotericin B Protocol",
        text="The national first-line treatment of choice for Visceral Leishmaniasis in India is a single intravenous infusion of Liposomal Amphotericin B (AmBisome) at 10 mg/kg body weight, administered in 5% dextrose infusion over 2 hours.\nMiltefosine (oral capsules) is an alternative or combination agent: 50 mg PO twice daily (for weight >= 25 kg) for 28 days. CRITICAL SAFETY GATING: Miltefosine is strictly teratogenic and contraindicated in pregnancy. Female patients of reproductive potential must have a negative pregnancy test and adhere to verified barrier contraception during therapy and for 3 months post-treatment. Liposomal Amphotericin B is safe in pregnancy.",
        citation="NVBDCP National Guidelines on Clinical Management of Kala-Azar (2022). MoHFW, Government of India."
    )
]

def get_all_guideline_chunks() -> List[ClinicalGuidelineChunk]:
    return INITIAL_EVIDENCE_LIBRARY
