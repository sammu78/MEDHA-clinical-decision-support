import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

MODEL_DIR = r"c:\Users\Sameer\OneDrive\Desktop\final\backend\app\models"

class ClinicalPredictor:
    def __init__(self):
        self.clf_models = {}
        self.reg_models = {}
        self.feature_cols = ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
        self._load_artifacts()

    def _load_artifacts(self):
        for cohort in ["type_2_diabetes", "essential_hypertension", "heart_failure"]:
            p = os.path.join(MODEL_DIR, f"{cohort}_clf.pkl")
            if os.path.exists(p):
                try:
                    with open(p, "rb") as f:
                        self.clf_models[cohort] = pickle.load(f)
                except Exception as e:
                    print(f"Error loading {p}: {e}")

        for task_id in ["insulin_sc", "metoprolol_po", "furosemide_iv"]:
            p = os.path.join(MODEL_DIR, f"{task_id}_reg.pkl")
            if os.path.exists(p):
                try:
                    with open(p, "rb") as f:
                        self.reg_models[task_id] = pickle.load(f)
                except Exception as e:
                    print(f"Error loading {p}: {e}")

    def extract_features(self, age: int, labs: Dict[str, Any]) -> pd.DataFrame:
        def get_val(kw):
            for k, v in labs.items():
                if kw in k.lower():
                    # Handle dict or Pydantic object
                    if hasattr(v, 'value'):
                        return v.value
                    elif isinstance(v, dict) and 'value' in v:
                        return v['value']
            return np.nan

        row = {
            'age': float(age),
            'pre_glucose': get_val('glucose'),
            'pre_creatinine': get_val('creatinine'),
            'pre_potassium': get_val('potassium'),
            'pre_sodium': get_val('sodium'),
            'pre_bun': get_val('bun')
        }
        return pd.DataFrame([row], columns=self.feature_cols)

    def predict_candidates(self, cohort_id: str, feat_df: pd.DataFrame) -> List[Tuple[str, float]]:
        if cohort_id not in self.clf_models:
            return []
        artifact = self.clf_models[cohort_id]
        imputer = artifact["imputer"]
        model = artifact["model"]
        classes = artifact["classes"]

        X_imp = pd.DataFrame(imputer.transform(feat_df), columns=self.feature_cols)
        probs = model.predict_proba(X_imp)[0]
        results = sorted(zip(classes, [float(p) for p in probs]), key=lambda x: x[1], reverse=True)
        return results

    def predict_dose_and_shap(
        self,
        task_id: str,
        feat_df: pd.DataFrame
    ) -> Tuple[Optional[float], Optional[str], Optional[Dict[str, float]]]:
        if task_id not in self.reg_models:
            return None, None, None

        artifact = self.reg_models[task_id]
        imputer = artifact["imputer"]
        model = artifact["model"]
        unit = artifact["unit"]
        explainer = artifact.get("explainer")

        X_imp = pd.DataFrame(imputer.transform(feat_df), columns=self.feature_cols)
        pred_dose = float(model.predict(X_imp)[0])

        shap_dict = {}
        if explainer:
            try:
                shap_vals = explainer.shap_values(X_imp)
                # If array
                if isinstance(shap_vals, np.ndarray):
                    vals = shap_vals[0] if len(shap_vals.shape) == 2 else shap_vals
                    for col, sv in zip(self.feature_cols, vals):
                        shap_dict[col] = round(float(sv), 3)
            except Exception as e:
                print(f"SHAP explanation note: {e}")

        return round(pred_dose, 1), unit, shap_dict

    def verify_shap_additivity(
        self,
        task_id: str,
        feat_df: pd.DataFrame,
        tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Verifies mathematical additivity of TreeExplainer:
        prediction == expected_value + sum(shap_values) within numerical tolerance.
        """
        if task_id not in self.reg_models:
            return {"verified": False, "reason": f"Model {task_id} not loaded"}

        artifact = self.reg_models[task_id]
        imputer = artifact["imputer"]
        model = artifact["model"]
        explainer = artifact.get("explainer")

        if not explainer:
            return {"verified": False, "reason": "No explainer artifact available"}

        X_imp = pd.DataFrame(imputer.transform(feat_df), columns=self.feature_cols)
        preds = model.predict(X_imp)
        shap_vals = explainer.shap_values(X_imp)
        ev = float(explainer.expected_value[0]) if hasattr(explainer.expected_value, '__iter__') else float(explainer.expected_value)

        errors = []
        for i in range(len(preds)):
            row_sv = shap_vals[i]
            reconstructed = ev + float(np.sum(row_sv))
            diff = abs(float(preds[i]) - reconstructed)
            errors.append(diff)

        max_err = max(errors) if errors else 0.0
        return {
            "task_id": task_id,
            "samples_tested": len(preds),
            "expected_value": round(ev, 4),
            "max_absolute_reconstruction_error": float(max_err),
            "tolerance": tolerance,
            "additivity_verified": bool(max_err <= tolerance),
            "features_verified": list(self.feature_cols)
        }

# Global predictor singleton
predictor = ClinicalPredictor()
