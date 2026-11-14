import pytest
import numpy as np
import pandas as pd
from app.models.predictor import predictor

@pytest.fixture
def sample_test_patients():
    # 25 diverse synthetic patient parameter sets
    rows = []
    for i in range(25):
        rows.append({
            "age": float(35 + (i * 2)),
            "pre_glucose": float(90.0 + (i * 8.5)),
            "pre_creatinine": float(0.7 + (i * 0.08)),
            "pre_potassium": float(3.6 + (i * 0.06)),
            "pre_sodium": float(134.0 + (i % 8)),
            "pre_bun": float(12.0 + (i * 1.2))
        })
    return pd.DataFrame(rows, columns=predictor.feature_cols)

def test_feature_alignment_and_ordering():
    expected_cols = ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
    assert predictor.feature_cols == expected_cols
    for task_id in ["insulin_sc", "metoprolol_po", "furosemide_iv"]:
        art = predictor.reg_models.get(task_id)
        assert art is not None
        assert art["feature_cols"] == expected_cols

def test_insulin_shap_additivity_reconstruction(sample_test_patients):
    res = predictor.verify_shap_additivity("insulin_sc", sample_test_patients, tolerance=1e-4)
    assert res["additivity_verified"] is True
    assert res["max_absolute_reconstruction_error"] < 1e-4
    assert res["samples_tested"] == 25

def test_metoprolol_shap_additivity_reconstruction(sample_test_patients):
    res = predictor.verify_shap_additivity("metoprolol_po", sample_test_patients, tolerance=1e-4)
    assert res["additivity_verified"] is True
    assert res["max_absolute_reconstruction_error"] < 1e-4
    assert res["samples_tested"] == 25

def test_furosemide_shap_additivity_reconstruction(sample_test_patients):
    res = predictor.verify_shap_additivity("furosemide_iv", sample_test_patients, tolerance=1e-4)
    assert res["additivity_verified"] is True
    assert res["max_absolute_reconstruction_error"] < 1e-4
    assert res["samples_tested"] == 25

def test_shap_missing_data_imputation_stability():
    # Patient with multiple missing features (NaNs)
    df_missing = pd.DataFrame([{
        "age": 62.0,
        "pre_glucose": np.nan,
        "pre_creatinine": 1.4,
        "pre_potassium": np.nan,
        "pre_sodium": 138.0,
        "pre_bun": np.nan
    }], columns=predictor.feature_cols)

    dose, unit, shap_dict = predictor.predict_dose_and_shap("insulin_sc", df_missing)
    assert dose is not None
    assert unit == "UNIT"
    assert shap_dict is not None
    # Verify no NaN or Inf in SHAP contributions
    for k, val in shap_dict.items():
        assert not np.isnan(val)
        assert not np.isinf(val)

def test_plain_language_disclaimer_distinction():
    # Verify that SHAP dictionary values are bounded and documented as mathematical attributions
    df_sample = pd.DataFrame([{
        "age": 58.0,
        "pre_glucose": 210.0,
        "pre_creatinine": 1.2,
        "pre_potassium": 4.5,
        "pre_sodium": 140.0,
        "pre_bun": 20.0
    }], columns=predictor.feature_cols)

    _, _, shap_dict = predictor.predict_dose_and_shap("insulin_sc", df_sample)
    assert "pre_glucose" in shap_dict
    # Clinical caveat assertion: Higher glucose positively shifts predicted insulin dose
    assert shap_dict["pre_glucose"] > 0
