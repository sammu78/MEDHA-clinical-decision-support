import os
import re
import pandas as pd
import numpy as np

from pathlib import Path

# Repository root relative to this module
REPO_ROOT = Path(__file__).resolve().parents[3]

MIMIC_HOSP = os.environ.get(
    "MIMIC_HOSP_DIR",
    str(REPO_ROOT / "mimic-iv-clinical-database-demo-2.2" / "hosp")
)
OUTPUT_PROCESSED = os.environ.get(
    "PROCESSED_DATA_PATH",
    str(REPO_ROOT / "data" / "processed" / "mimic_treatment_decisions.csv")
)

def parse_numeric_dose(val):
    if pd.isnull(val):
        return np.nan
    s = str(val).strip().replace(',', '')
    # Handle ranges like 5-10 or 10-20 by taking the midpoint or lower
    if '-' in s:
        parts = s.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2.0
        except Exception:
            pass
    # Regex match first float
    match = re.search(r"[-+]?\d*\.\d+|\d+", s)
    if match:
        try:
            return float(match.group(0))
        except Exception:
            return np.nan
    return np.nan

def clean_generic_name(drug_str):
    if pd.isnull(drug_str):
        return "UNKNOWN"
    d = str(drug_str).lower()
    if "insulin" in d:
        return "Insulin"
    elif "metformin" in d:
        return "Metformin"
    elif "glipizide" in d:
        return "Glipizide"
    elif "metoprolol" in d:
        return "Metoprolol"
    elif "lisinopril" in d:
        return "Lisinopril"
    elif "amlodipine" in d:
        return "Amlodipine"
    elif "furosemide" in d:
        return "Furosemide"
    elif "spironolactone" in d:
        return "Spironolactone"
    elif "hydralazine" in d:
        return "Hydralazine"
    return "Other"

def extract_treatment_decisions():
    print("Loading MIMIC-IV demo raw files for data preparation...")
    os.makedirs(os.path.dirname(OUTPUT_PROCESSED), exist_ok=True)
    
    # 1. Patients & Admissions
    patients = pd.read_csv(os.path.join(MIMIC_HOSP, "patients.csv.gz"), compression='gzip')
    admissions = pd.read_csv(os.path.join(MIMIC_HOSP, "admissions.csv.gz"), compression='gzip')
    adm_pat = admissions.merge(patients, on="subject_id", how="inner")
    adm_pat['admittime_dt'] = pd.to_datetime(adm_pat['admittime'])
    adm_pat['adm_year'] = adm_pat['admittime_dt'].dt.year
    adm_pat['encounter_age'] = adm_pat['anchor_age'] + (adm_pat['adm_year'] - adm_pat['anchor_year'])
    adm_dict = adm_pat.set_index('hadm_id').to_dict(orient='index')

    # 2. Diagnoses
    dx = pd.read_csv(os.path.join(MIMIC_HOSP, "diagnoses_icd.csv.gz"), compression='gzip')
    d_dx = pd.read_csv(os.path.join(MIMIC_HOSP, "d_icd_diagnoses.csv.gz"), compression='gzip')
    dx_m = dx.merge(d_dx, on=["icd_code", "icd_version"], how="left")
    
    hadm_to_dx = {}
    for hadm, group in dx_m.groupby('hadm_id'):
        titles = " ".join(group['long_title'].dropna().tolist()).lower()
        icds = " ".join(group['icd_code'].dropna().tolist()).lower()
        
        cats = []
        if "diabetes" in titles or "250" in icds or "e11" in icds:
            cats.append("type_2_diabetes")
        if "hypertension" in titles or "401" in icds or "i10" in icds:
            cats.append("essential_hypertension")
        if "heart failure" in titles or "428" in icds or "i50" in icds:
            cats.append("heart_failure")
        hadm_to_dx[hadm] = cats

    # 3. Lab events
    labs = pd.read_csv(os.path.join(MIMIC_HOSP, "labevents.csv.gz"), compression='gzip')
    labs['charttime_dt'] = pd.to_datetime(labs['charttime'])
    labs_valid = labs[labs['valuenum'].notnull() & labs['charttime_dt'].notnull()]
    
    # Map itemids to standard lab types
    # 50931, 50809 -> glucose; 50912 -> creatinine; 50971, 50822 -> potassium; 50983, 50824 -> sodium; 51006 -> bun
    lab_map = {
        50931: "glucose", 50809: "glucose",
        50912: "creatinine",
        50971: "potassium", 50822: "potassium",
        50983: "sodium", 50824: "sodium",
        51006: "bun"
    }
    labs_valid = labs_valid[labs_valid['itemid'].isin(lab_map.keys())].copy()
    labs_valid['lab_type'] = labs_valid['itemid'].map(lab_map)
    # Sort for fast temporal lookup
    labs_valid = labs_valid.sort_values(['subject_id', 'charttime_dt'])
    
    # Group labs by subject_id for quick search
    labs_by_subject = {}
    for sub_id, group in labs_valid.groupby('subject_id'):
        labs_by_subject[sub_id] = group

    # 4. Prescriptions
    rx = pd.read_csv(os.path.join(MIMIC_HOSP, "prescriptions.csv.gz"), compression='gzip')
    rx['starttime_dt'] = pd.to_datetime(rx['starttime'])
    rx['generic_clean'] = rx['drug'].apply(clean_generic_name)
    
    # Target candidate medications for research cohorts
    target_drugs = [
        "Insulin", "Metformin", "Glipizide",
        "Metoprolol", "Lisinopril", "Amlodipine", "Hydralazine",
        "Furosemide", "Spironolactone"
    ]
    rx_target = rx[rx['generic_clean'].isin(target_drugs) & rx['starttime_dt'].notnull()].copy()
    rx_target['dose_numeric'] = rx_target['dose_val_rx'].apply(parse_numeric_dose)

    print(f"Target prescriptions identified: {len(rx_target)}")

    records = []
    for idx, row in rx_target.iterrows():
        hadm = row['hadm_id']
        sub_id = row['subject_id']
        t_rx = row['starttime_dt']
        
        adm_info = adm_dict.get(hadm, {})
        age = adm_info.get('encounter_age', np.nan)
        gender = adm_info.get('gender', 'Unknown')
        
        matched_cats = hadm_to_dx.get(hadm, [])
        if not matched_cats:
            continue
        
        # Look up pre-decision labs strictly before t_rx
        pre_labs = {"glucose": np.nan, "creatinine": np.nan, "potassium": np.nan, "sodium": np.nan, "bun": np.nan}
        if sub_id in labs_by_subject:
            p_df = labs_by_subject[sub_id]
            # Prior labs within 7 days prior to order
            prior_window = p_df[(p_df['charttime_dt'] <= t_rx) & (p_df['charttime_dt'] >= t_rx - pd.Timedelta(days=7))]
            for l_type in ["glucose", "creatinine", "potassium", "sodium", "bun"]:
                matched_l = prior_window[prior_window['lab_type'] == l_type]
                if len(matched_l) > 0:
                    # Most recent prior value
                    pre_labs[l_type] = matched_l.iloc[-1]['valuenum']

        # Determine best diagnosis category based on drug and matched categories
        generic = row['generic_clean']
        primary_cat = matched_cats[0]
        if generic in ["Insulin", "Metformin", "Glipizide"] and "type_2_diabetes" in matched_cats:
            primary_cat = "type_2_diabetes"
        elif generic in ["Metoprolol", "Lisinopril", "Amlodipine", "Hydralazine"] and "essential_hypertension" in matched_cats:
            primary_cat = "essential_hypertension"
        elif generic in ["Furosemide", "Spironolactone"] and "heart_failure" in matched_cats:
            primary_cat = "heart_failure"

        records.append({
            "subject_id": sub_id,
            "hadm_id": hadm,
            "decision_time": str(t_rx),
            "diagnosis_category": primary_cat,
            "age": age,
            "gender": gender,
            "pre_glucose": pre_labs["glucose"],
            "pre_creatinine": pre_labs["creatinine"],
            "pre_potassium": pre_labs["potassium"],
            "pre_sodium": pre_labs["sodium"],
            "pre_bun": pre_labs["bun"],
            "generic_medicine": generic,
            "dose_numeric": row['dose_numeric'],
            "dose_unit": row['dose_unit_rx'],
            "route": row['route']
        })

    df_out = pd.DataFrame(records)
    df_out.to_csv(OUTPUT_PROCESSED, index=False)
    print(f"Extraction complete! Saved {len(df_out)} treatment decision records to {OUTPUT_PROCESSED}")
    print(f"Unique patients: {df_out['subject_id'].nunique()}")
    print("Distribution by diagnosis category:\n", df_out['diagnosis_category'].value_counts())
    print("Distribution by medicine:\n", df_out['generic_medicine'].value_counts())
    return df_out

if __name__ == "__main__":
    extract_treatment_decisions()
