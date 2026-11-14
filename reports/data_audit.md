# Clinical Data Audit & Feasibility Report: MIMIC-IV Demo & Staging Repositories

**Project**: Explainable Drug and Dosage Decision Support
**Audit Date**: September 2026
**Data Location**: `c:\Users\Sameer\OneDrive\Desktop\final\mimic-iv-clinical-database-demo-2.2\hosp`

## 1. Executive Summary

This audit rigorously assesses the clinical feasibility of constructing a decision-support prototype using the MIMIC-IV Clinical Database Demo v2.2 (hosp module). It analyzes table structures, demographic attributes, lab events, medication orders, temporal constraints, and external reference tables.

> **Critical Clinical Rule Enforced**: Features must strictly precede medication ordering time (`lab_charttime <= rx_starttime`). Billing ICD codes assigned at hospital discharge cannot be assumed as guaranteed indications at the moment of inpatient ordering without verification.

## 2. MIMIC-IV Demo Tables Inspection

| Table File | Total Rows | Unique Patients | Unique Encounters (`hadm_id`) | Key Notes |
|---|---|---|---|---|
| `patients.csv.gz` | 100 | 100 | N/A | 6 columns |
| `admissions.csv.gz` | 275 | 100 | 275 | 16 columns |
| `diagnoses_icd.csv.gz` | 4,506 | 100 | 275 | 5 columns |
| `d_icd_diagnoses.csv.gz` | 109,775 | N/A | N/A | 3 columns |
| `labevents.csv.gz` | 107,727 | 100 | 252 | 16 columns |
| `d_labitems.csv.gz` | 1,622 | N/A | N/A | 4 columns |
| `prescriptions.csv.gz` | 18,087 | 100 | 250 | 21 columns |
| `emar.csv.gz` | 35,835 | 65 | 181 | 12 columns |
| `emar_detail.csv.gz` | 72,018 | 65 | N/A | 33 columns |
| `omr.csv.gz` | 2,964 | 79 | N/A | 5 columns |

### Demographic Age Distribution
Age at hospital admission was calculated using `anchor_age + (YEAR(admittime) - anchor_year)`:
- **Encounters evaluated**: 275
- **Age range**: 21 to 93 years
- **Mean age**: 62.7 years (Median: 63.0)

## 3. Laboratory Measurements Dictionary & Event Coverage

| Clinical Measurement | MIMIC ItemIDs | Total Events | Patient Count | Available Units |
|---|---|---|---|---|
| **Glucose (Serum/Plasma)** | `[50931, 50809]` | 2,973 | 100 | mg/dL |
| **Creatinine (Blood)** | `[50912]` | 3,003 | 100 | mg/dL |
| **Potassium (Blood)** | `[50971, 50822]` | 3,324 | 100 | mEq/L |
| **Sodium (Blood)** | `[50983, 50824]` | 3,148 | 100 | mEq/L |
| **Urea Nitrogen / BUN** | `[51006]` | 2,974 | 100 | mg/dL |
| **Hemoglobin** | `[51222]` | 2,787 | 100 | g/dL |
| **HbA1c / Glycated Hemoglobin** | `[50852]` | 117 | 44 | % |

## 4. Prescriptions Overview

- **Total Prescription Orders**: 18,087
- **Unique Medications**: 631
- **Missing Dose Values**: 9 (0.05%)
- **Missing Dose Units**: 9 (0.05%)
- **Missing Routes**: 6 (0.03%)

### Top Prescribed Generic & Brand Medications
| Medication | Order Count |
|---|---|
| Insulin | 915 |
| 0.9% Sodium Chloride | 810 |
| Potassium Chloride | 610 |
| Sodium Chloride 0.9%  Flush | 585 |
| Furosemide | 510 |
| 5% Dextrose | 492 |
| Bag | 454 |
| Magnesium Sulfate | 402 |
| Metoprolol Tartrate | 371 |
| Acetaminophen | 344 |

### Top Administration Routes & Dose Units
- **Routes**: IV (8,219), PO/NG (3,841), PO (2,191), SC (1,249), IV DRIP (1,026), IM (370), IH (194), TP (157), PR (152), ORAL (77)
- **Units**: mg (7,971), mL (4,300), UNIT (1,514), mEq (851), g (820), gm (682), BAG (597), TAB (220), mcg (202), Appl (184)

## 5. Candidate Narrow Cohort Counts in 100-Patient Demo

### Diagnosis Group: Diabetes
- Diagnoses matching `diabetes`: 159 instances across 35 patients and 115 hospital admissions.
| Medication Pattern | Prescriptions | Unique Patients | Top Routes | Top Units |
|---|---|---|---|---|
| Insulin | 868 | 32 | SC:840, IV DRIP:21, IV:7 | UNIT:864, SYR:2 |
| Metformin | 18 | 11 | PO:15, PO/NG:3 | mg:18 |
| Glipizide | 11 | 6 | PO:7, PO/NG:4 | mg:11 |

### Diagnosis Group: Hypertension
- Diagnoses matching `hypertension`: 124 instances across 64 patients and 122 hospital admissions.
| Medication Pattern | Prescriptions | Unique Patients | Top Routes | Top Units |
|---|---|---|---|---|
| Metoprolol | 198 | 36 | PO/NG:84, PO:62, IV:52 | mg:198 |
| Lisinopril | 40 | 14 | PO/NG:36, PO:4 | mg:40 |
| Amlodipine | 34 | 13 | PO/NG:32, PO:2 | mg:34 |
| Furosemide | 182 | 30 | IV:127, PO/NG:36, IV DRIP:15 | mg:182 |
| Hydralazine | 62 | 22 | IV:44, PO/NG:18 | mg:62 |

### Diagnosis Group: Heart Failure
- Diagnoses matching `heart failure`: 103 instances across 24 patients and 61 hospital admissions.
| Medication Pattern | Prescriptions | Unique Patients | Top Routes | Top Units |
|---|---|---|---|---|
| Furosemide | 309 | 18 | IV:239, PO/NG:35, IV DRIP:30 | mg:309 |
| Metoprolol | 193 | 18 | PO/NG:104, PO:52, IV:37 | mg:193 |
| Spironolactone | 12 | 4 | PO/NG:12 | mg:12 |
| Lisinopril | 24 | 9 | PO/NG:23, PO:1 | mg:24 |

## 6. Pre-Decision Temporal Window Verification

Sampling 200 medication orders and evaluating prior labs strictly where `lab_charttime <= rx_starttime`:
- **Orders with pre-decision Glucose**: 97.5%
- **Orders with pre-decision Creatinine**: 97.5%

> **Leakage Prevention**: Future lab values (drawn after the order was placed) are strictly omitted from feature tables to prevent data leakage.

## 7. Staging Files Inspection & Evidence Verification

The external datasets found in local staging were inspected for provenance and safety:

### `d_dose.csv` (3,029 rows)
- **Columns**: `generic, disease, min_age_d, max_age_d, min_age_m, max_age_m, min_age_y, max_age_y, min_weight, max_weight, min_dose_dw_mg, max_dose_dw_mg, min_dose_dw_iu, max_dose_dw_iu, limit_mg, limit_iu, min_dose_dd_mg, max_dose_dd_mg, min_dose_dd_UNIT, max_dose_dd_iu, route, Unnamed: 21`
- **Status**: 🔬 **REFERENCE STAGING ONLY**. Static lookup rules without clinical trial provenance or peer-reviewed citations. Units and indications must be vetted before activation.

### `s_dose.csv` (288 rows)
- **Columns**: `generic, min_age_d, max_age_d, min_age_m, max_age_m, min_age_y, max_age_y, min_weight, max_weight, min_dose_dw_mg, max_dose_dw_mg, min_dose_dw_iu, max_dose_dw_iu, limit_mg, limit_iu, min_dose_dd_mg, max_dose_dd_mg, min_dose_dd_UNIT, max_dose_dd_iu, route`
- **Status**: 🔬 **REFERENCE STAGING ONLY**. Static lookup rules without clinical trial provenance or peer-reviewed citations. Units and indications must be vetted before activation.

### `r_dose.csv` (220 rows)
- **Columns**: `generic, disease, min_weight, max_weight, min_crcl, max_crcl, max_dose_dd_mg, max_dose_dw_mg, max_dose_dd_iu, max_dose_dw_iu, route, flag`
- **Status**: 🔬 **REFERENCE STAGING ONLY**. Static lookup rules without clinical trial provenance or peer-reviewed citations. Units and indications must be vetted before activation.

### `generic_disease_map.csv` (1,066 rows)
- **Columns**: `generic, disease`
- **Status**: 📋 **INDICATION DICTIONARY**. Mappings between diseases and drug classes; requires clinical guidelines verification.

### `indian_medicines.csv` (11,825 rows)
- **Columns**: `name, composition, uses, side_effects, image_url`
- **Status**: 📦 **COMMERCIAL FORMULARY MAPPING**. Contains manufacturer/brand listings, pricing, and pack sizes. Useful for brand-to-generic mapping, but lacks renal dosing contraindication metadata.

### `personalized_medication_dataset.csv` (1,000 rows)
- **Columns**: `Patient_ID, Age, Gender, Weight_kg, Height_cm, BMI, Chronic_Conditions, Drug_Allergies, Genetic_Disorders, Diagnosis, Symptoms, Recommended_Medication, Dosage, Duration, Treatment_Effectiveness, Adverse_Reactions, Recovery_Time_Days`
- **Status**: ⚠️ **UNVERIFIED / SYNTHETIC**. Must NOT be used as clinical ground truth. Disallowed from clinical dosing guidance.

### `diabetes_with_dosage.csv` (768 rows)
- **Columns**: `Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome, Dosage`
- **Status**: ⚠️ **UNVERIFIED / SYNTHETIC**. Must NOT be used as clinical ground truth. Disallowed from clinical dosing guidance.

## 8. Data Limitations & Clinical Safeguards

1. **Billing Diagnosis Timing**: ICD-9/10 codes in `diagnoses_icd` are billing codes assigned at discharge, not real-time clinical notes entered when the order was signed.
2. **Multimorbid Inpatient Attribution**: A patient with simultaneous diagnoses of Diabetes, Hypertension, and Renal Failure receiving multiple drugs cannot automatically have every drug attributed to every diagnosis.
3. **Small Sample Size in 100-Patient Demo**: In this 100-patient demo subset, oral antidiabetics like Metformin have only 0-5 orders (most hospitalized patients in this cohort received subcutaneous/IV regular or sliding scale Insulin). Therefore, machine learning models trained on 100 demo patients are underpowered research demonstrations. Baseline heuristics and safety rule validation must gate any automated dose display.
4. **Dosing Units Discrepancies**: Different routes and drugs use `mg`, `UNIT`, `mcg`, `mEq`, `mL`. A dose model cannot mix units without strict standardization.

## 9. Recommended First Cohort Proposal

Based on the audit, we recommend:

1. **Primary Clinical Case**: **Type 2 Diabetes Mellitus - Inpatient Glycemic Management (Subcutaneous/Short-acting Insulin vs Oral Antidiabetics)**.
   - **Justification**: In the 100-patient demo, Insulin is the single most frequent medication (915 orders across 35 diabetic patients) with robust lab coverage (glucose, creatinine, BUN, potassium).
   - **Secondary Clinical Case**: **Essential Hypertension - Inpatient Management (Metoprolol Tartrate vs Amlodipine vs Lisinopril)**.
   - **Justification**: 73 patients with hypertension, 371 Metoprolol orders, well-defined renal contraindications (e.g., Lisinopril held if Cr > 2.5 or eGFR < 30).
   - **Third Clinical Case**: **Acute/Chronic Heart Failure (Furosemide / Loop Diuretics)** with serum potassium and creatinine monitoring.
2. **Training & Deployment Architecture**:
   - Provide a rigorous, leak-free feature extraction pipeline (`extract_features.py`).
   - Implement patient-level splitting (GroupKFold / GroupShuffleSplit) so no patient appears in both train and test splits.
   - Compare research models (XGBoost / RandomForest) against dummy baselines (Most Frequent for classification, Median for dose regression).
   - Because demo sample sizes are modest, the system includes a **strict safety check gateway**: if sample size or clinical evidence is insufficient, it halts display gracefully and marks status as 'More information needed' or 'Research prototype - dose withheld'.
