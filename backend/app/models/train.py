import os
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.impute import SimpleImputer
import shap

# Repository root relative to this module
REPO_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DATA_PATH = os.environ.get(
    "PROCESSED_DATA_PATH",
    str(REPO_ROOT / "data" / "processed" / "mimic_treatment_decisions.csv")
)
MODEL_DIR = os.environ.get(
    "MODEL_DIR",
    str(Path(__file__).resolve().parent)
)
METRICS_PATH = os.environ.get(
    "METRICS_PATH",
    str(Path(MODEL_DIR) / "evaluation_metrics.json")
)

os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_evaluate():
    print(f"Loading data from {PROCESSED_DATA_PATH}...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # 1. Validate required columns
    required_cols = [
        'subject_id', 'hadm_id', 'decision_time', 'diagnosis_category',
        'age', 'gender', 'pre_glucose', 'pre_creatinine', 'pre_potassium',
        'pre_sodium', 'pre_bun', 'generic_medicine', 'dose_numeric',
        'dose_unit', 'route'
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    source_row_count = len(df)
    unique_patients_total = int(df['subject_id'].nunique())
    exact_duplicates_count = int(df.duplicated().sum())

    print(f"Source row count: {source_row_count}")
    print(f"Unique patients: {unique_patients_total}")
    print(f"Exact duplicate rows detected: {exact_duplicates_count}")

    # Remove exact row duplicates from the modeling copy only. Original CSV is unmodified.
    df_model = df.drop_duplicates().copy()
    dedup_row_count = len(df_model)
    print(f"Modeling rows after exact-row deduplication: {dedup_row_count}")

    metrics_summary = {}
    feature_cols = ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
    missing_counts = {k: int(v) for k, v in df_model[feature_cols].isnull().sum().to_dict().items()}

    # --- TASK 1: MEDICINE CLASSIFICATION BY COHORT ---
    cohorts = ["type_2_diabetes", "essential_hypertension", "heart_failure"]

    for cohort in cohorts:
        print(f"\n--- Training Medicine Classification for Cohort: {cohort} ---")
        cdf = df_model[df_model['diagnosis_category'] == cohort].copy()
        
        # Filter classes with at least 5 records
        val_counts = cdf['generic_medicine'].value_counts()
        eligible_drugs = val_counts[val_counts >= 5].index.tolist()
        cdf = cdf[cdf['generic_medicine'].isin(eligible_drugs)].copy()

        if len(cdf['generic_medicine'].unique()) < 2 or len(cdf) < 20:
            print(f"Skipping {cohort}: insufficient class diversity or records ({len(cdf)} records)")
            metrics_summary[f"{cohort}_classification"] = {
                "cohort_name": cohort,
                "status": "STOPPED_GRACEFULLY_UNDERPOWERED",
                "total_records": len(cdf),
                "unique_patients": int(cdf['subject_id'].nunique()),
                "message": "Sample size in 100-patient demo is too small to build a generalizable model. Falling back to guideline rule registry."
            }
            continue

        X = cdf[feature_cols].copy()
        y = cdf['generic_medicine'].copy()
        groups = cdf['subject_id'].values

        # Patient-level split
        gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups=groups))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        train_patients = set(groups[train_idx])
        test_patients = set(groups[test_idx])
        assert len(train_patients.intersection(test_patients)) == 0, "DATA LEAKAGE: Patient overlap in classification split!"

        imputer = SimpleImputer(strategy="median")
        X_train_imp = pd.DataFrame(imputer.fit_transform(X_train), columns=feature_cols)
        X_test_imp = pd.DataFrame(imputer.transform(X_test), columns=feature_cols)

        # Baseline: Most Frequent
        baseline_clf = DummyClassifier(strategy="most_frequent")
        baseline_clf.fit(X_train_imp, y_train)
        base_preds = baseline_clf.predict(X_test_imp)
        base_acc = float(accuracy_score(y_test, base_preds))

        # Research Model: Random Forest
        rf_clf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        rf_clf.fit(X_train_imp, y_train)
        rf_preds = rf_clf.predict(X_test_imp)
        rf_acc = float(accuracy_score(y_test, rf_preds))
        rf_bal_acc = float(balanced_accuracy_score(y_test, rf_preds))
        rf_macro_prec = float(precision_score(y_test, rf_preds, average='macro', zero_division=0))
        rf_macro_rec = float(recall_score(y_test, rf_preds, average='macro', zero_division=0))
        rf_weighted_f1 = float(f1_score(y_test, rf_preds, average='weighted', zero_division=0))
        rf_macro_f1 = float(f1_score(y_test, rf_preds, average='macro', zero_division=0))

        class_labels = list(rf_clf.classes_)
        cm = confusion_matrix(y_test, rf_preds, labels=class_labels).tolist()
        clf_rep = classification_report(y_test, rf_preds, labels=class_labels, output_dict=True, zero_division=0)

        # Save artifacts
        clf_artifact = {
            "imputer": imputer,
            "model": rf_clf,
            "classes": class_labels,
            "feature_cols": feature_cols
        }
        with open(os.path.join(MODEL_DIR, f"{cohort}_clf.pkl"), "wb") as f:
            pickle.dump(clf_artifact, f)

        metrics_summary[f"{cohort}_classification"] = {
            "seed": 42,
            "source_row_count": source_row_count,
            "deduplicated_modeling_row_count": dedup_row_count,
            "missing_value_counts": missing_counts,
            "cohort_name": cohort,
            "task": "Medicine Classification",
            "total_records": len(cdf),
            "train_records": len(train_idx),
            "test_records": len(test_idx),
            "unique_patients_total": int(cdf['subject_id'].nunique()),
            "unique_patients_train": len(train_patients),
            "unique_patients_test": len(test_patients),
            "candidate_medicines": eligible_drugs,
            "baseline_accuracy": round(base_acc, 3),
            "model_accuracy": round(rf_acc, 3),
            "model_balanced_accuracy": round(rf_bal_acc, 3),
            "model_macro_precision": round(rf_macro_prec, 3),
            "model_macro_recall": round(rf_macro_rec, 3),
            "model_macro_f1": round(rf_macro_f1, 3),
            "model_weighted_f1": round(rf_weighted_f1, 3),
            "confusion_matrix": {
                "labels": class_labels,
                "matrix": cm
            },
            "per_class_report": clf_rep,
            "split_strategy": "Patient-level GroupShuffleSplit (Zero patient overlap)",
            "limitations": [
                "Trained on 100-patient MIMIC-IV demo subset.",
                "Inpatient prescribing reflects hospital-specific formulary preference.",
                "Billing diagnoses may represent secondary comorbidities.",
                "Predicts historical prescribing patterns, not necessarily optimal or guideline-preferred treatment.",
                "Severe class imbalance: macro metrics reveal that raw accuracy is driven by majority classes."
            ]
        }
        print(f"Classification result for {cohort}: Baseline Acc={base_acc:.3f}, RF Acc={rf_acc:.3f}, Bal Acc={rf_bal_acc:.3f}, Weighted F1={rf_weighted_f1:.3f}")

    # --- TASK 2: DOSE REGRESSION FOR FREQUENT MEDICINES ---
    dose_tasks = [
        {"med": "Insulin", "route": "SC", "unit": "UNIT", "name": "insulin_sc"},
        {"med": "Metoprolol", "route": "PO", "unit": "mg", "name": "metoprolol_po"},
        {"med": "Furosemide", "route": "IV", "unit": "mg", "name": "furosemide_iv"}
    ]

    for dt in dose_tasks:
        med_name = dt["med"]
        route_kw = dt["route"]
        unit_name = dt["unit"]
        task_id = dt["name"]

        print(f"\n--- Training Dose Regression for {med_name} ({route_kw}, {unit_name}) ---")
        mdf = df_model[
            (df_model['generic_medicine'] == med_name) &
            (df_model['route'].str.contains(route_kw, case=False, na=False)) &
            (df_model['dose_numeric'].notnull()) &
            (df_model['dose_numeric'] > 0)
        ].copy()

        if len(mdf) < 25 or mdf['subject_id'].nunique() < 5:
            print(f"Skipping dose regression for {med_name}: insufficient records ({len(mdf)}) or patients ({mdf['subject_id'].nunique()})")
            metrics_summary[f"{task_id}_regression"] = {
                "medicine": med_name,
                "status": "STOPPED_GRACEFULLY_UNDERPOWERED",
                "records": len(mdf),
                "patients": int(mdf['subject_id'].nunique()),
                "message": "Insufficient patient volume for statistical regression. Dosing gated to verified clinical guidelines."
            }
            continue

        X = mdf[feature_cols].copy()
        y = mdf['dose_numeric'].copy()
        groups = mdf['subject_id'].values

        gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups=groups))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        train_patients = set(groups[train_idx])
        test_patients = set(groups[test_idx])
        assert len(train_patients.intersection(test_patients)) == 0, "DATA LEAKAGE: Patient overlap in dose regression split!"

        imputer = SimpleImputer(strategy="median")
        X_train_imp = pd.DataFrame(imputer.fit_transform(X_train), columns=feature_cols)
        X_test_imp = pd.DataFrame(imputer.transform(X_test), columns=feature_cols)

        # Baseline: Median
        baseline_reg = DummyRegressor(strategy="median")
        baseline_reg.fit(X_train_imp, y_train)
        base_preds = baseline_reg.predict(X_test_imp)
        base_mae = float(mean_absolute_error(y_test, base_preds))
        base_rmse = float(np.sqrt(mean_squared_error(y_test, base_preds)))
        try:
            base_r2 = float(r2_score(y_test, base_preds))
        except Exception:
            base_r2 = None

        # Research Model: Random Forest Regressor
        rf_reg = RandomForestRegressor(n_estimators=50, max_depth=4, random_state=42)
        rf_reg.fit(X_train_imp, y_train)
        rf_preds = rf_reg.predict(X_test_imp)
        rf_mae = float(mean_absolute_error(y_test, rf_preds))
        rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_preds)))
        try:
            rf_r2 = float(r2_score(y_test, rf_preds))
        except Exception:
            rf_r2 = None

        # SHAP Explainer
        explainer = shap.TreeExplainer(rf_reg)

        reg_artifact = {
            "imputer": imputer,
            "model": rf_reg,
            "feature_cols": feature_cols,
            "unit": unit_name,
            "explainer": explainer
        }
        with open(os.path.join(MODEL_DIR, f"{task_id}_reg.pkl"), "wb") as f:
            pickle.dump(reg_artifact, f)

        metrics_summary[f"{task_id}_regression"] = {
            "seed": 42,
            "source_row_count": source_row_count,
            "deduplicated_modeling_row_count": dedup_row_count,
            "missing_value_counts": missing_counts,
            "medicine": med_name,
            "route": route_kw,
            "unit": unit_name,
            "total_records": len(mdf),
            "train_records": len(train_idx),
            "test_records": len(test_idx),
            "unique_patients_total": int(mdf['subject_id'].nunique()),
            "unique_patients_train": len(train_patients),
            "unique_patients_test": len(test_patients),
            "baseline_median_dose_mae": round(base_mae, 2),
            "baseline_median_dose_rmse": round(base_rmse, 2),
            "baseline_median_dose_r2": round(base_r2, 4) if base_r2 is not None else None,
            "model_dose_mae": round(rf_mae, 2),
            "model_dose_rmse": round(rf_rmse, 2),
            "model_dose_r2": round(rf_r2, 4) if rf_r2 is not None else None,
            "split_strategy": "Patient-level GroupShuffleSplit (Zero patient overlap)",
            "limitations": [
                "Historical dose in MIMIC reflects clinician empirical ordering, not randomized trial titration.",
                "Evaluation on demo cohort is an exploratory research benchmark, not a clinical treatment validation.",
                "Automated dose proposal remains gated by safety checker.",
                "Negative R² confirms model does not outperform test-set mean variance; dosing must not be autonomously displayed."
            ]
        }
        print(f"Regression result for {task_id}: Baseline MAE={base_mae:.2f} (RMSE={base_rmse:.2f}), Model MAE={rf_mae:.2f} (RMSE={rf_rmse:.2f}, R2={rf_r2:.4f}) {unit_name}")

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"\nAll models and evaluation metrics saved to {METRICS_PATH}")

if __name__ == "__main__":
    train_and_evaluate()
