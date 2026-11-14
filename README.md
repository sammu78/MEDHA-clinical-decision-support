# MEDHA — Medicine & Dosage Assessment

A clinical decision-support application designed to assist authorized physicians in evaluating medication options, calculating patient-specific dosages, and verifying independent clinical safety constraints. The system combines verified clinical practice guidelines (ADA 2024, ACC/AHA 2020, KDIGO 2023, CDSCO) with machine learning research benchmarks trained on the **MIMIC-IV Clinical Database**.

---

## ⚡ Simplified Clinical Workflow (Input → Output)

The main landing interface is designed for clinical simplicity:

**Enter Patient Details & Labs → Click "Analyze Medicine & Dosage" → Process Clinical Information → View Structured Results**

- **Clean Medical Landing View:** Completely free of developer dashboards, database record counts, CSV import logs, Fact–Dimension schema details, and model benchmark tables.
- **Single Organized Input Form:**
  - *Patient Information:* Case ID (optional), Age, Sex (biological), Diagnosis/Condition, Weight in kg.
  - *Pre-Decision Laboratory Panel:* Blood Glucose (mg/dL), Serum Creatinine (mg/dL), Potassium (mEq/L), Sodium (mEq/L), Blood Urea Nitrogen / BUN (mg/dL) with measurement timestamps.
  - *Optional Clinical Context:* Current active medications, documented allergies, comorbidities.
  - *Validation:* Strict client-side and server-side validation. Never silently fills missing clinical values.
- **One Prominent Action:** **"Analyze Medicine & Dosage"** with real-time progressive status indicators (*"Validating patient information…"*, *"Checking laboratory data and clinical safety…"*, *"Evaluating available medicine options…"*, *"Preparing assessment results…"*) and repeat-submission lockout.
- **Structured Clinical Results View:**
  - **A. Assessment Status:** Unambiguous status (*Assessment completed*, *Additional information required*, *Recommendation withheld by safety checks*, *Unable to complete assessment*) with clinical explanations.
  - **B. Medicine Options:** Generic name, candidate score / model probability accurately labeled, clinical indication, CDSCO formulations, and prescribing warnings distinguishing decision-support candidates from clinician-approved decisions.
  - **C. Dosage Information:** Numeric dose, units, route, administration schedule, and renal adjustment. *Strict withholding rule:* If contraindicated or missing required labs, numeric dose is withheld by safety protocol.
  - **D. Clinical Safety Engine:** Independent checks for acute hypoglycemia (<70 mg/dL), hyperkalemia (>5.5 mEq/L), renal impairment (eGFR/CrCl), and drug hypersensitivities.
  - **E. Collapsible Explanation ("Why was this result produced?"):** Summarizes clinical input parameters, TreeSHAP statistical attributions on dosage, and model limitations notice emphasizing that SHAP does not prove clinical causation.
  - **F. Actions:** *New Assessment*, *Edit Patient Information*, *View Supporting Evidence* (guideline citations modal), and *Print Assessment Summary* (formatted for clinical printout).
- **Developer / Admin Area:** Internal Fact–Dimension warehouse statistics, CSV import logs, MIMIC-IV benchmark metrics, and 27-disease evaluation matrices are safely preserved and isolated in a separate, dedicated portal accessible via the top-right *Developer / Admin Area* button.

---

## 🏛️ System Architecture

```text
final/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py          # FastAPI endpoints (/health, /dashboard/metrics, /cases, /medicines, /sources, /audit)
│   │   ├── data/
│   │   │   └── pipeline.py           # Pre-decision temporal lab extraction (zero data leakage)
│   │   ├── database/
│   │   │   ├── db.py                 # SQLite database connection & initialization
│   │   │   ├── schema.py             # Normalized Fact-Dimension schema DDL (dim_patient, fact_treatment_decision, etc.)
│   │   │   └── importer.py           # Validated, idempotent data warehouse importer with audit logging
│   │   ├── evidence/
│   │   │   ├── disease_catalogue.py  # 27-disease clinical coverage catalogue (ICMR STWs, CDSCO, KDIGO, ADA)
│   │   │   ├── registry.py           # Evidence source registry (ICMR, CDSCO, ADA, ACC/AHA, KDIGO)
│   │   │   ├── library.py            # Clinical guideline text chunks and metadata
│   │   │   └── retriever.py          # Hybrid FAISS + BM25 clinical guideline retrieval engine
│   │   ├── explanations/
│   │   │   └── generator.py          # Decision support explanation synthesizer with provenance attribution
│   │   ├── models/
│   │   │   ├── predictor.py          # Model inference and SHAP attribution engine
│   │   │   ├── train.py              # Patient-level splitting (GroupShuffleSplit) & baseline evaluation
│   │   │   └── evaluation_metrics.json
│   │   ├── safety/
│   │   │   └── checker.py            # Independent multi-tier clinical safety & dosing gate
│   │   ├── schemas/
│   │   │   └── clinical.py           # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── clinical_chat.py      # Case state management, SSE streaming, doctor notes entity extractor
│   │   │   ├── indian_medicines_service.py # Search & brand matching for 11,827 Indian commercial medicines
│   │   │   └── lab_retrieval_service.py # Leakage-free SQL-backed temporal pre-decision lab retrieval
│   │   └── main.py                   # FastAPI application entrypoint with CORS
│   ├── tests/
│   │   ├── test_backend.py           # Safety checks, dashboard metrics, case lifecycle & E2E tests
│   │   ├── test_lab_retrieval.py     # Leakage-free temporal lab retrieval unit tests
│   │   ├── test_extended_system.py   # Multi-disease and safety rule integrity tests
│   │   └── test_rag_pipeline.py      # Hybrid FAISS + BM25 RAG retrieval & QA tests
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DisclaimerBanner.tsx  # Prominent research disclaimer
│   │   │   ├── Sidebar.tsx           # Collapsible 10-section clinical navigation
│   │   │   ├── PatientPanel.tsx      # Patient vitals and auto-computed CKD-EPI / Cockcroft-Gault
│   │   │   ├── EditPatientModal.tsx  # Direct clinical parameter and lab editor modal
│   │   │   ├── IndianMedicineModal.tsx # Commercial Indian branded formulations popup
│   │   │   ├── CitationModal.tsx     # Full evidence citation & guideline viewer
│   │   │   └── ExportDraftModal.tsx  # Printable markdown clinical assessment report generator
│   │   ├── pages/
│   │   │   ├── OverviewDashboardPage.tsx # Live database KPI metrics, recent assessments, & import batches
│   │   │   ├── AssessmentFormPage.tsx # Guided multi-section clinical intake form (Patient, Labs, Meds, Review)
│   │   │   ├── AssessmentResultPage.tsx # Evidence-grounded results, safety gating status, and SHAP bars
│   │   │   ├── ChatWorkspace.tsx     # Conversational doctor chat with real-time SSE streaming
│   │   │   ├── CoverageMatrixPage.tsx # 27-disease ICMR/CDSCO coverage matrix & renal protocols
│   │   │   ├── IndianMedicinesPage.tsx # Search & filter 11,827 Indian commercial products
│   │   │   ├── EvidenceLibraryPage.tsx # Verified clinical guideline document viewer & RAG search
│   │   │   ├── ModelDetailsPage.tsx  # TreeSHAP feature attributions and benchmark comparisons
│   │   │   ├── ModelAuditPage.tsx    # MIMIC-IV benchmark metrics, patient splitting & data audit viewer
│   │   │   ├── SupportedCasesPage.tsx # Searchable supported diseases & indications registry
│   │   │   └── SettingsPage.tsx      # Clinical safety gate governance, theme, and API status
│   │   ├── services/
│   │   │   └── api.ts                # TypeScript client for FastAPI backend with SSE reader
│   │   ├── styles/
│   │   │   └── clinical.css          # Clinical design system (clean navy/teal accessible palette)
│   │   ├── tests/
│   │   │   └── clinical.test.tsx     # Vitest UI, renal calculators & safety gating unit tests
│   │   ├── types.ts                  # TypeScript clinical schemas & DashboardMetrics
│   │   └── App.tsx                   # Hospital top bar and persistent multi-view layout
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   ├── raw/mimic_demo/hosp/          # Source path to MIMIC-IV Demo tables
│   ├── staging/                      # Staging area for reference tables (indian_medicines.csv, d_dose.csv, etc.)
│   ├── processed/
│   │   └── mimic_treatment_decisions.csv # 2,010 cleaned pre-decision treatment decisions
│   └── clinical_decision_support.db  # SQLite database for cases, assessments, and indexed formulary
│
├── reports/
│   ├── data_audit.md                 # Complete audit of MIMIC-IV Demo & staging files
│   └── audit_data_raw.json
├── scripts/
│   ├── deep_audit.py                 # Multi-file data feasibility audit script
│   ├── run_audit.py                  # Initial audit runner
│   └── verify_clinical_e2e.py        # Automated end-to-end verification script for all 7 clinical workflows
└── README.md
```

---

## ⚡ Quick Start: Running on Windows

### 1. Backend Setup (FastAPI & Python 3.10+)

Open PowerShell in the project directory `final`:

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend test suite (13 clinical safety, case lifecycle & integrity tests)
python -m pytest tests/test_backend.py -v

# Run automated end-to-end verification across all 7 core clinical workflows
python ../scripts/verify_clinical_e2e.py

# Start FastAPI server (runs on http://127.0.0.1:8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger documentation will be available at:  
👉 **http://127.0.0.1:8000/docs**

---

### 2. Frontend Setup (React + Vite + TypeScript)

Open a second PowerShell window in `final`:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend Vitest tests (7 tests)
npm test

# Build production bundle to verify types
npm run build

# Start the Vite development server (runs on http://127.0.0.1:5173)
npm run dev
```

Access the clinical user interface at:  
👉 **http://127.0.0.1:5173/**

---

## 🚀 Deploying to Render

This project is pre-configured with a Render Blueprint (`render.yaml`) for 1-click zero-config deployment.

### Option A: 1-Click Blueprint (Recommended)
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository (`sammu78/MEDHA-clinical-decision-support`).
4. Render will automatically parse `render.yaml` and provision both:
   - **`medha-backend`** (Web Service): Runs FastAPI on Python with Uvicorn.
   - **`medha-frontend`** (Static Site): Builds React + Vite and serves via CDN, auto-wired to `medha-backend`.
5. Click **Apply**. Render will build and deploy both services!

### Option B: Manual Service Creation
If you prefer creating the services manually in Render:

#### 1. Backend Web Service:
* **Type:** Web Service
* **Name:** `medha-backend`
* **Root Directory:** `backend`
* **Environment:** `Python`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables:** `PYTHON_VERSION` = `3.10.10`

#### 2. Frontend Static Site:
* **Type:** Static Site
* **Name:** `medha-frontend`
* **Root Directory:** `frontend`
* **Build Command:** `npm install && npm run build`
* **Publish Directory:** `dist`
* **Rewrite Rule:** Source `/*` → Destination `/index.html`
* **Environment Variable:** `VITE_API_BASE_URL` = `https://<your-backend-slug>.onrender.com`

---

## 🧪 Data Audit & Pipeline Summary

A comprehensive data audit was conducted and saved to [`reports/data_audit.md`](file:///c:/Users/Sameer/OneDrive/Desktop/final/reports/data_audit.md).

* **Source Data**: Beth Israel Deaconess Medical Center MIMIC-IV Clinical Database Demo v2.2 (`hosp` module).
  - 100 unique patients, 275 hospital encounters, 18,087 prescription orders, 107,727 laboratory events.
* **Leakage-Free Temporal Window**:
  - Feature extraction strictly enforces $\text{lab\_charttime} \le \text{prescription\_starttime}$.
  - Future measurements taken after order placement are barred from the feature table.
* **Processed Dataset**:
  - 2,010 treatment decision records across 76 unique patients.
  - Primary cohorts: **Type 2 Diabetes Mellitus** (1,095 records), **Essential Hypertension** (528 records), **Congestive Heart Failure** (387 records).
* **Staging Repositories Inspection**:
  - `d_dose.csv`, `s_dose.csv`, `r_dose.csv`, `generic_disease_map.csv`, `indian_medicines.csv`: Staged for reference; clinical dosing locked pending verification.
  - `personalized_medication_dataset.csv` and `diabetes_with_dosage.csv`: Flagged as synthetic/unverified and **strictly barred from clinical treatment ground truth**.

---

## 🔬 Research Models & Evaluation

The research prototypes implement two distinct modeling tasks:

1. **Medicine Classification**:  
   Predicts medicine historically prescribed given pre-decision labs and age. Evaluated against a **Most Frequent Class Baseline**.
   - Type 2 Diabetes: Baseline Accuracy = 75.5%, Random Forest = **75.5%** (F1 = 0.650)
   - Essential Hypertension: Baseline Accuracy = 27.8%, Random Forest = **31.2%** (F1 = 0.197)
   - Congestive Heart Failure: Baseline Accuracy = 97.0%, Random Forest = **94.0%** (F1 = 0.940)

2. **Dose Regression**:  
   Models prescribed numeric dose conditional on route, pre-decision labs, and age. Evaluated against a **Median Dose Baseline Regressor**.
   - **Insulin (Subcutaneous, UNIT)**: Baseline MAE = 12.58 UNIT, Model MAE = **14.12 UNIT**
   - **Metoprolol (Oral, mg)**: Baseline MAE = 30.51 mg, Model MAE = **33.17 mg**
   - **Furosemide (IV, mg)**: Baseline MAE = 80.48 mg, Random Forest Regressor = **67.17 mg** (**13.3 mg MAE improvement**)

### 🔒 Patient-Level Splitting
To prevent data leakage, training uses **`GroupShuffleSplit` on `subject_id`**. Zero patients overlap between train and test sets.

### 💡 Explainability (SHAP)
Tree-based SHAP explainers attribute numeric influences of individual patient factors (e.g. Glucose +4.2 UNIT, Age -1.1 UNIT) to provide interpretable rationales for clinician review.

---

## 🛡️ Multi-Tier Clinical Safety Engine

Any automated proposal is strictly gated by clinical safety checks:

| Safety Gate | Trigger Condition | System Action |
|---|---|---|
| **Diagnosis Verification** | Diagnosis not in verified registry | Status: `UNSUPPORTED_CASE`. Dose withheld. |
| **Missing Laboratory Data** | Required lab missing (e.g. Glucose or Creatinine) | Status: `MORE_INFO_NEEDED`. Exact dose withheld. |
| **Acute Hypoglycemia** | Blood Glucose < 70 mg/dL | Status: `CONTRAINDICATED`. Metformin & Insulin withheld. Dextrose/carbohydrate protocol alert. |
| **Severe Hyperkalemia** | Serum Potassium > 5.5 mEq/L | Status: `CONTRAINDICATED`. Lisinopril & Spironolactone withheld. |
| **Severe Renal Failure** | eGFR < 30 mL/min/1.73m2 or Cr > 1.5 mg/dL | Metformin withheld (lactic acidosis risk). Dose adjustments required. |
| **Drug Allergies** | Documented ACEi allergy / angioedema history | Lisinopril contraindicated. |
| **Drug-Drug Interactions** | Concurrent Potassium supplement / Spironolactone | Hyperkalemia interaction warning displayed. |

---

## 🖥️ Clinical User Interface (React + Vite)

The UI adheres to modern clinical software standards:
* **Clean Clinical Aesthetics**: High-contrast white background, deep navy text (`#0f2744`), restrained clinical teal accents (`#0d9488`).
* **Quick Clinical Vignettes**: One-click preset scenarios for rapid evaluator demonstration:
  1. *T2D Hyperglycemia (Eligible)* → Shows authorized Metformin 500mg and Insulin titration with SHAP bars.
  2. *T2D Acute Hypoglycemia (<70 mg/dL)* → Triggers safety contraindication with withheld dose.
  3. *T2D Severe CKD (eGFR 22)* → Demonstrates renal safety gate withholding Metformin.
  4. *Primary HTN (Eligible)* → Authorized Amlodipine, Lisinopril, and Metoprolol.
  5. *HTN with Hyperkalemia (K=5.7)* → Withholds Lisinopril due to hyperkalemia.
  6. *Heart Failure Volume Overload* → Evaluates IV Furosemide with potassium stability check.
  7. *Missing Required Labs* → Demonstrates graceful data preservation and withheld dose.
* **Transparent Provenance**: Badges differentiate `VERIFIED CLINICAL GUIDELINE`, `RESEARCH ML MODEL`, and `HISTORICAL PRESCRIPTION BENCHMARK`.

---

## ⚠️ Known Limitations & Future Directions

1. **Retrospective Demo Scope**: The MIMIC-IV demo provides 100 patient profiles. While sufficient for end-to-end pipeline validation and research benchmarks, the cohort size is underpowered for independent clinical generalization.
2. **Billing vs Real-Time Diagnosis**: ICD-9/10 codes in EHR datasets are assigned at hospital discharge, not at order time.
3. **Inpatient Practice Divergence**: Hospitalized diabetics frequently receive subcutaneous insulin rather than outpatient metformin due to fasting and imaging procedures.
4. **Next Dataset Needed**: Further training requires access to the full MIMIC-IV v2.2 database (40,000+ patients) or prospective outpatient EHR feeds (e.g. eICU-CRD, UK Biobank, or FHIR-compliant ambulatory records).
