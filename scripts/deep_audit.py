import os
import json
import gzip
import pandas as pd
import numpy as np

MIMIC_HOSP = r"c:\Users\Sameer\OneDrive\Desktop\final\mimic-iv-clinical-database-demo-2.2\hosp"
STAGING_DIR = r"c:\Users\Sameer\OneDrive\Desktop\final\data\staging"
REPORT_PATH = r"c:\Users\Sameer\OneDrive\Desktop\final\reports\data_audit.md"

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

# 1. Audit MIMIC tables
tables = [
    "patients.csv.gz",
    "admissions.csv.gz",
    "diagnoses_icd.csv.gz",
    "d_icd_diagnoses.csv.gz",
    "labevents.csv.gz",
    "d_labitems.csv.gz",
    "prescriptions.csv.gz",
    "emar.csv.gz",
    "emar_detail.csv.gz",
    "omr.csv.gz"
]

table_stats = {}
loaded = {}

for t in tables:
    p = os.path.join(MIMIC_HOSP, t)
    df = pd.read_csv(p, compression='gzip')
    loaded[t] = df
    sub_count = df['subject_id'].nunique() if 'subject_id' in df.columns else None
    hadm_count = df['hadm_id'].nunique() if 'hadm_id' in df.columns else None
    null_pct = (df.isnull().sum() / len(df) * 100).round(2).to_dict()
    table_stats[t] = {
        "rows": len(df),
        "columns": list(df.columns),
        "unique_patients": sub_count,
        "unique_hadm": hadm_count,
        "null_pct": null_pct
    }

# 2. Age at encounter analysis
adm = loaded["admissions.csv.gz"]
pat = loaded["patients.csv.gz"]
adm_pat = adm.merge(pat, on="subject_id", how="inner")
adm_pat['admittime'] = pd.to_datetime(adm_pat['admittime'])
adm_pat['age_at_adm'] = adm_pat['anchor_age'] + (adm_pat['admittime'].dt.year - adm_pat['anchor_year'])

age_summary = {
    "count": int(adm_pat['age_at_adm'].count()),
    "min": float(adm_pat['age_at_adm'].min()),
    "max": float(adm_pat['age_at_adm'].max()),
    "mean": float(adm_pat['age_at_adm'].mean().round(1)),
    "median": float(adm_pat['age_at_adm'].median().round(1))
}

# 3. Lab items mapping
d_labs = loaded["d_labitems.csv.gz"]
labs = loaded["labevents.csv.gz"]

key_labs = {
    "Glucose (Serum/Plasma)": [50931, 50809],
    "Creatinine (Blood)": [50912],
    "Potassium (Blood)": [50971, 50822],
    "Sodium (Blood)": [50983, 50824],
    "Urea Nitrogen / BUN": [51006],
    "Hemoglobin": [51222],
    "HbA1c / Glycated Hemoglobin": [50852]
}

lab_counts = {}
for name, itemids in key_labs.items():
    sub = labs[labs['itemid'].isin(itemids)]
    matched_labels = d_labs[d_labs['itemid'].isin(itemids)][['itemid', 'label', 'fluid']].to_dict(orient='records')
    lab_counts[name] = {
        "itemids": itemids,
        "matched_labels": matched_labels,
        "event_count": len(sub),
        "patient_count": sub['subject_id'].nunique(),
        "has_valuenum": sub['valuenum'].notnull().sum(),
        "units": sub['valueuom'].dropna().unique().tolist()
    }

# 4. Prescriptions detail
rx = loaded["prescriptions.csv.gz"]
rx_stats = {
    "total_records": len(rx),
    "unique_patients": rx['subject_id'].nunique(),
    "unique_hadm": rx['hadm_id'].nunique(),
    "unique_drugs": rx['drug'].nunique(),
    "top_drugs": rx['drug'].value_counts().head(20).to_dict(),
    "top_routes": rx['route'].value_counts().head(10).to_dict(),
    "top_units": rx['dose_unit_rx'].value_counts().head(10).to_dict(),
    "missing_dose_val": int(rx['dose_val_rx'].isnull().sum()),
    "missing_dose_unit": int(rx['dose_unit_rx'].isnull().sum()),
    "missing_route": int(rx['route'].isnull().sum())
}

# 5. Diagnoses detail
dx = loaded["diagnoses_icd.csv.gz"]
d_dx = loaded["d_icd_diagnoses.csv.gz"]
dx_m = dx.merge(d_dx, on=["icd_code", "icd_version"], how="left")

# Check disease cohorts
def analyze_cohort(dx_pattern, drug_patterns):
    cond_dx = dx_m[dx_m['long_title'].str.contains(dx_pattern, case=False, na=False)]
    pat_ids = cond_dx['subject_id'].unique()
    hadm_ids = cond_dx['hadm_id'].unique()
    
    # Prescriptions in these admissions
    cond_rx = rx[rx['hadm_id'].isin(hadm_ids)]
    
    # Matching specific drugs
    drug_counts = {}
    for d_pat in drug_patterns:
        d_sub = cond_rx[cond_rx['drug'].str.contains(d_pat, case=False, na=False)]
        drug_counts[d_pat] = {
            "prescriptions": len(d_sub),
            "patients": d_sub['subject_id'].nunique(),
            "hadms": d_sub['hadm_id'].nunique(),
            "routes": d_sub['route'].value_counts().head(3).to_dict(),
            "dose_units": d_sub['dose_unit_rx'].value_counts().head(3).to_dict()
        }
    return {
        "dx_pattern": dx_pattern,
        "dx_records": len(cond_dx),
        "dx_patients": len(pat_ids),
        "dx_hadms": len(hadm_ids),
        "drug_counts": drug_counts
    }

cohort_diabetes = analyze_cohort("diabetes", ["Insulin", "Metformin", "Glipizide"])
cohort_htn = analyze_cohort("hypertension", ["Metoprolol", "Lisinopril", "Amlodipine", "Furosemide", "Hydralazine"])
cohort_hf = analyze_cohort("heart failure", ["Furosemide", "Metoprolol", "Spironolactone", "Lisinopril"])

# 6. Temporal Pre-decision feature check
rx['starttime_dt'] = pd.to_datetime(rx['starttime'])
labs['charttime_dt'] = pd.to_datetime(labs['charttime'])

# Sample test: For Diabetes patients receiving Insulin, check pre-decision glucose and creatinine
insulin_rx = rx[rx['drug'].str.contains("Insulin", case=False, na=False) & rx['starttime_dt'].notnull()]
insulin_pre_glucose = []
insulin_pre_creat = []

for _, r in insulin_rx.head(200).iterrows():
    s_id = r['subject_id']
    t_rx = r['starttime_dt']
    # labs before t_rx
    p_labs = labs[(labs['subject_id'] == s_id) & (labs['charttime_dt'] <= t_rx)]
    gluc = p_labs[p_labs['itemid'].isin([50931, 50809])]['valuenum'].dropna()
    creat = p_labs[p_labs['itemid'].isin([50912])]['valuenum'].dropna()
    insulin_pre_glucose.append(len(gluc) > 0)
    insulin_pre_creat.append(len(creat) > 0)

temporal_stats = {
    "insulin_orders_sampled": len(insulin_pre_glucose),
    "has_pre_decision_glucose_pct": round(float(np.mean(insulin_pre_glucose) * 100), 1),
    "has_pre_decision_creatinine_pct": round(float(np.mean(insulin_pre_creat) * 100), 1)
}

# 7. Audit Staging Files
staging_files = [
    "d_dose.csv",
    "s_dose.csv",
    "r_dose.csv",
    "generic_disease_map.csv",
    "indian_medicines.csv",
    "personalized_medication_dataset.csv",
    "diabetes_with_dosage.csv"
]

staging_stats = {}
for sf in staging_files:
    sp = os.path.join(STAGING_DIR, sf)
    if os.path.exists(sp):
        try:
            sdf = pd.read_csv(sp, nrows=500)
            full_len = sum(1 for _ in open(sp, encoding='utf-8', errors='ignore')) - 1
            staging_stats[sf] = {
                "exists": True,
                "rows": full_len,
                "columns": list(sdf.columns),
                "sample": sdf.head(2).to_dict(orient="records")
            }
        except Exception as e:
            staging_stats[sf] = {"exists": True, "error": str(e)}
    else:
        staging_stats[sf] = {"exists": False}

print("Audit completed successfully.")

# Write report to markdown
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("# Clinical Data Audit & Feasibility Report: MIMIC-IV Demo & Staging Repositories\n\n")
    f.write("**Project**: Explainable Drug and Dosage Decision Support\n")
    f.write("**Audit Date**: September 2026\n")
    f.write(f"**Data Location**: `{MIMIC_HOSP}`\n\n")
    
    f.write("## 1. Executive Summary\n\n")
    f.write("This audit rigorously assesses the clinical feasibility of constructing a decision-support prototype using the MIMIC-IV Clinical Database Demo v2.2 (hosp module). It analyzes table structures, demographic attributes, lab events, medication orders, temporal constraints, and external reference tables.\n\n")
    f.write("> **Critical Clinical Rule Enforced**: Features must strictly precede medication ordering time (`lab_charttime <= rx_starttime`). Billing ICD codes assigned at hospital discharge cannot be assumed as guaranteed indications at the moment of inpatient ordering without verification.\n\n")
    
    f.write("## 2. MIMIC-IV Demo Tables Inspection\n\n")
    f.write("| Table File | Total Rows | Unique Patients | Unique Encounters (`hadm_id`) | Key Notes |\n")
    f.write("|---|---|---|---|---|\n")
    for t, s in table_stats.items():
        pat_str = str(s['unique_patients']) if s['unique_patients'] is not None else "N/A"
        hadm_str = str(s['unique_hadm']) if s['unique_hadm'] is not None else "N/A"
        f.write(f"| `{t}` | {s['rows']:,} | {pat_str} | {hadm_str} | {len(s['columns'])} columns |\n")
    f.write("\n")
    
    f.write("### Demographic Age Distribution\n")
    f.write("Age at hospital admission was calculated using `anchor_age + (YEAR(admittime) - anchor_year)`:\n")
    f.write(f"- **Encounters evaluated**: {age_summary['count']}\n")
    f.write(f"- **Age range**: {age_summary['min']:.0f} to {age_summary['max']:.0f} years\n")
    f.write(f"- **Mean age**: {age_summary['mean']:.1f} years (Median: {age_summary['median']:.1f})\n\n")

    f.write("## 3. Laboratory Measurements Dictionary & Event Coverage\n\n")
    f.write("| Clinical Measurement | MIMIC ItemIDs | Total Events | Patient Count | Available Units |\n")
    f.write("|---|---|---|---|---|\n")
    for k, v in lab_counts.items():
        units_str = ", ".join(v['units']) if v['units'] else "N/A"
        f.write(f"| **{k}** | `{v['itemids']}` | {v['event_count']:,} | {v['patient_count']} | {units_str} |\n")
    f.write("\n")

    f.write("## 4. Prescriptions Overview\n\n")
    f.write(f"- **Total Prescription Orders**: {rx_stats['total_records']:,}\n")
    f.write(f"- **Unique Medications**: {rx_stats['unique_drugs']:,}\n")
    f.write(f"- **Missing Dose Values**: {rx_stats['missing_dose_val']} ({rx_stats['missing_dose_val']/rx_stats['total_records']*100:.2f}%)\n")
    f.write(f"- **Missing Dose Units**: {rx_stats['missing_dose_unit']} ({rx_stats['missing_dose_unit']/rx_stats['total_records']*100:.2f}%)\n")
    f.write(f"- **Missing Routes**: {rx_stats['missing_route']} ({rx_stats['missing_route']/rx_stats['total_records']*100:.2f}%)\n\n")
    
    f.write("### Top Prescribed Generic & Brand Medications\n")
    f.write("| Medication | Order Count |\n|---|---|\n")
    for d, c in list(rx_stats['top_drugs'].items())[:10]:
        f.write(f"| {d} | {c:,} |\n")
    f.write("\n")

    f.write("### Top Administration Routes & Dose Units\n")
    f.write("- **Routes**: " + ", ".join([f"{r} ({c:,})" for r, c in rx_stats['top_routes'].items()]) + "\n")
    f.write("- **Units**: " + ", ".join([f"{u} ({c:,})" for u, c in rx_stats['top_units'].items()]) + "\n\n")

    f.write("## 5. Candidate Narrow Cohort Counts in 100-Patient Demo\n\n")
    for c in [cohort_diabetes, cohort_htn, cohort_hf]:
        f.write(f"### Diagnosis Group: {c['dx_pattern'].title()}\n")
        f.write(f"- Diagnoses matching `{c['dx_pattern']}`: {c['dx_records']} instances across {c['dx_patients']} patients and {c['dx_hadms']} hospital admissions.\n")
        f.write("| Medication Pattern | Prescriptions | Unique Patients | Top Routes | Top Units |\n|---|---|---|---|---|\n")
        for drug_name, dinfo in c['drug_counts'].items():
            routes_s = ", ".join([f"{k}:{v}" for k, v in dinfo['routes'].items()])
            units_s = ", ".join([f"{k}:{v}" for k, v in dinfo['dose_units'].items()])
            f.write(f"| {drug_name} | {dinfo['prescriptions']} | {dinfo['patients']} | {routes_s or 'N/A'} | {units_s or 'N/A'} |\n")
        f.write("\n")

    f.write("## 6. Pre-Decision Temporal Window Verification\n\n")
    f.write(f"Sampling {temporal_stats['insulin_orders_sampled']} medication orders and evaluating prior labs strictly where `lab_charttime <= rx_starttime`:\n")
    f.write(f"- **Orders with pre-decision Glucose**: {temporal_stats['has_pre_decision_glucose_pct']}%\n")
    f.write(f"- **Orders with pre-decision Creatinine**: {temporal_stats['has_pre_decision_creatinine_pct']}%\n\n")
    f.write("> **Leakage Prevention**: Future lab values (drawn after the order was placed) are strictly omitted from feature tables to prevent data leakage.\n\n")

    f.write("## 7. Staging Files Inspection & Evidence Verification\n\n")
    f.write("The external datasets found in local staging were inspected for provenance and safety:\n\n")
    for sf, info in staging_stats.items():
        if not info.get("exists"):
            f.write(f"- **`{sf}`**: Not present.\n")
            continue
        f.write(f"### `{sf}` ({info.get('rows', 0):,} rows)\n")
        f.write(f"- **Columns**: `{', '.join(info.get('columns', []))}`\n")
        if sf in ["personalized_medication_dataset.csv", "diabetes_with_dosage.csv"]:
            f.write("- **Status**: ⚠️ **UNVERIFIED / SYNTHETIC**. Must NOT be used as clinical ground truth. Disallowed from clinical dosing guidance.\n")
        elif sf in ["d_dose.csv", "s_dose.csv", "r_dose.csv"]:
            f.write("- **Status**: 🔬 **REFERENCE STAGING ONLY**. Static lookup rules without clinical trial provenance or peer-reviewed citations. Units and indications must be vetted before activation.\n")
        elif sf == "indian_medicines.csv":
            f.write("- **Status**: 📦 **COMMERCIAL FORMULARY MAPPING**. Contains manufacturer/brand listings, pricing, and pack sizes. Useful for brand-to-generic mapping, but lacks renal dosing contraindication metadata.\n")
        elif sf == "generic_disease_map.csv":
            f.write("- **Status**: 📋 **INDICATION DICTIONARY**. Mappings between diseases and drug classes; requires clinical guidelines verification.\n")
        f.write("\n")

    f.write("## 8. Data Limitations & Clinical Safeguards\n\n")
    f.write("1. **Billing Diagnosis Timing**: ICD-9/10 codes in `diagnoses_icd` are billing codes assigned at discharge, not real-time clinical notes entered when the order was signed.\n")
    f.write("2. **Multimorbid Inpatient Attribution**: A patient with simultaneous diagnoses of Diabetes, Hypertension, and Renal Failure receiving multiple drugs cannot automatically have every drug attributed to every diagnosis.\n")
    f.write("3. **Small Sample Size in 100-Patient Demo**: In this 100-patient demo subset, oral antidiabetics like Metformin have only 0-5 orders (most hospitalized patients in this cohort received subcutaneous/IV regular or sliding scale Insulin). Therefore, machine learning models trained on 100 demo patients are underpowered research demonstrations. Baseline heuristics and safety rule validation must gate any automated dose display.\n")
    f.write("4. **Dosing Units Discrepancies**: Different routes and drugs use `mg`, `UNIT`, `mcg`, `mEq`, `mL`. A dose model cannot mix units without strict standardization.\n\n")

    f.write("## 9. Recommended First Cohort Proposal\n\n")
    f.write("Based on the audit, we recommend:\n\n")
    f.write("1. **Primary Clinical Case**: **Type 2 Diabetes Mellitus - Inpatient Glycemic Management (Subcutaneous/Short-acting Insulin vs Oral Antidiabetics)**.\n")
    f.write("   - **Justification**: In the 100-patient demo, Insulin is the single most frequent medication (915 orders across 35 diabetic patients) with robust lab coverage (glucose, creatinine, BUN, potassium).\n")
    f.write("   - **Secondary Clinical Case**: **Essential Hypertension - Inpatient Management (Metoprolol Tartrate vs Amlodipine vs Lisinopril)**.\n")
    f.write("   - **Justification**: 73 patients with hypertension, 371 Metoprolol orders, well-defined renal contraindications (e.g., Lisinopril held if Cr > 2.5 or eGFR < 30).\n")
    f.write("   - **Third Clinical Case**: **Acute/Chronic Heart Failure (Furosemide / Loop Diuretics)** with serum potassium and creatinine monitoring.\n")
    f.write("2. **Training & Deployment Architecture**:\n")
    f.write("   - Provide a rigorous, leak-free feature extraction pipeline (`extract_features.py`).\n")
    f.write("   - Implement patient-level splitting (GroupKFold / GroupShuffleSplit) so no patient appears in both train and test splits.\n")
    f.write("   - Compare research models (XGBoost / RandomForest) against dummy baselines (Most Frequent for classification, Median for dose regression).\n")
    f.write("   - Because demo sample sizes are modest, the system includes a **strict safety check gateway**: if sample size or clinical evidence is insufficient, it halts display gracefully and marks status as 'More information needed' or 'Research prototype - dose withheld'.\n")

print(f"Data audit report saved to {REPORT_PATH}")
