import os
import gzip
import json
import pandas as pd
import numpy as np

MIMIC_HOSP_DIR = r"c:\Users\Sameer\OneDrive\Desktop\final\mimic-iv-clinical-database-demo-2.2\hosp"
PROJECT_DIR = r"c:\Users\Sameer\OneDrive\Desktop\final"

def inspect_table(filename, max_rows=None):
    path = os.path.join(MIMIC_HOSP_DIR, filename)
    if not os.path.exists(path):
        return {"exists": False, "filename": filename}
    
    df = pd.read_csv(path, compression='gzip', nrows=max_rows)
    # Total row count
    # for compressed files, read full if reasonable size
    full_df = pd.read_csv(path, compression='gzip')
    total_rows = len(full_df)
    unique_patients = full_df['subject_id'].nunique() if 'subject_id' in full_df.columns else None
    
    null_counts = full_df.isnull().sum().to_dict()
    cols = list(full_df.columns)
    dtypes = {c: str(full_df[c].dtype) for c in cols}
    
    result = {
        "exists": True,
        "filename": filename,
        "total_rows": total_rows,
        "unique_patients": unique_patients,
        "columns": cols,
        "dtypes": dtypes,
        "null_counts": null_counts,
        "sample": full_df.head(3).to_dict(orient="records")
    }
    return result, full_df

print("Starting audit script...")
tables_to_check = [
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

audit_results = {}
dfs = {}
for t in tables_to_check:
    res, df = inspect_table(t)
    audit_results[t] = res
    dfs[t] = df
    print(f"Loaded {t}: {res['total_rows']} rows, {res['unique_patients']} patients")

# 1. Patients and Admissions Analysis: Age calculation
patients = dfs["patients.csv.gz"]
admissions = dfs["admissions.csv.gz"]
adm_pat = admissions.merge(patients, on="subject_id", how="left")
# MIMIC-IV calculates age: anchor_age + (admittime.year - anchor_year)
adm_pat['admittime_dt'] = pd.to_datetime(adm_pat['admittime'])
adm_pat['adm_year'] = adm_pat['admittime_dt'].dt.year
adm_pat['calc_age'] = adm_pat['anchor_age'] + (adm_pat['adm_year'] - adm_pat['anchor_year'])

print("Age calculation summary:")
print(adm_pat[['anchor_age', 'anchor_year', 'adm_year', 'calc_age']].describe())

# 2. Lab items dictionary - Identify glucose, creatinine, etc.
d_labitems = dfs["d_labitems.csv.gz"]
labevents = dfs["labevents.csv.gz"]
relevant_labs = d_labitems[d_labitems['label'].str.contains('glucose|creatinine|potassium|sodium|hemoglobin|urea|hba1c|alt|ast|egfr', case=False, na=False)]
print("\nRelevant lab items in d_labitems:")
for _, row in relevant_labs.iterrows():
    # count how many occurrences in labevents
    count = (labevents['itemid'] == row['itemid']).sum()
    print(f"  itemid={row['itemid']}, label='{row['label']}', fluid='{row['fluid']}', category='{row['category']}', events_count={count}")

# 3. Prescriptions analysis: medicines, routes, units
rx = dfs["prescriptions.csv.gz"]
print("\nPrescriptions overview:")
print(f"Total prescriptions: {len(rx)}")
print(f"Unique drugs: {rx['drug'].nunique()}")
print(f"Unique routes: {rx['route'].nunique()}")
print(f"Dose units: {rx['dose_unit_rx'].value_counts().head(10).to_dict()}")
print(f"Top 15 drugs:\n{rx['drug'].value_counts().head(15)}")
print(f"Top routes:\n{rx['route'].value_counts().head(10)}")

# 4. Diagnoses analysis
dx = dfs["diagnoses_icd.csv.gz"]
d_dx = dfs["d_icd_diagnoses.csv.gz"]
dx_joined = dx.merge(d_dx, on=["icd_code", "icd_version"], how="left")
print(f"\nUnique ICD codes: {dx['icd_code'].nunique()}")
print("Top 15 diagnoses:\n", dx_joined['long_title'].value_counts().head(15))

# Check specific conditions: Type 2 Diabetes, Hypertension, Heart Failure, Hyperlipidemia, Asthma/COPD, Bacterial infection
t2d_icd = dx_joined[dx_joined['long_title'].str.contains('diabetes', case=False, na=False)]
print(f"\nDiabetes diagnoses count: {len(t2d_icd)}, unique patients: {t2d_icd['subject_id'].nunique()}")

htn_icd = dx_joined[dx_joined['long_title'].str.contains('hypertension|hypertensive', case=False, na=False)]
print(f"Hypertension diagnoses count: {len(htn_icd)}, unique patients: {htn_icd['subject_id'].nunique()}")

hf_icd = dx_joined[dx_joined['long_title'].str.contains('heart failure', case=False, na=False)]
print(f"Heart failure count: {len(hf_icd)}, unique patients: {hf_icd['subject_id'].nunique()}")

# 5. Temporal join: Can pre-decision lab features be matched before prescription starttime?
rx['starttime_dt'] = pd.to_datetime(rx['starttime'])
labevents['charttime_dt'] = pd.to_datetime(labevents['charttime'])

# Check for diabetes patients: Metformin, Insulin, Glipizide
diab_patients = t2d_icd['subject_id'].unique()
diab_rx = rx[rx['subject_id'].isin(diab_patients)]
print("\nPrescriptions among diabetes patients:")
print(diab_rx['drug'].value_counts().head(20))

# Save summary json for writing report
summary_path = os.path.join(PROJECT_DIR, "reports", "audit_data_raw.json")
os.makedirs(os.path.dirname(summary_path), exist_ok=True)

# Serialize summary
serializable_audit = {}
for k, v in audit_results.items():
    serializable_audit[k] = {
        "filename": v["filename"],
        "total_rows": v["total_rows"],
        "unique_patients": v["unique_patients"],
        "columns": v["columns"],
        "null_counts": v["null_counts"]
    }

with open(summary_path, "w") as f:
    json.dump({
        "tables": serializable_audit,
        "age_stats": {
            "mean": float(adm_pat['calc_age'].mean()),
            "min": float(adm_pat['calc_age'].min()),
            "max": float(adm_pat['calc_age'].max()),
            "median": float(adm_pat['calc_age'].median())
        },
        "top_drugs": rx['drug'].value_counts().head(25).to_dict(),
        "top_routes": rx['route'].value_counts().head(15).to_dict(),
        "dose_units": rx['dose_unit_rx'].value_counts().head(15).to_dict(),
        "top_diagnoses": dx_joined['long_title'].value_counts().head(25).to_dict()
    }, f, indent=2)

print("\nSaved raw audit data to:", summary_path)
