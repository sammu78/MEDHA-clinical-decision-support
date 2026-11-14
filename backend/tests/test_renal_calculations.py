import math
import pytest
from app.safety.checker import calculate_egfr_ckd_epi_2021, calculate_crcl_cockcroft_gault

# 1. CKD-EPI 2021: Male reference calculation
def test_ckd_epi_male_reference():
    # 55 yo male, Scr 1.0 mg/dL: kappa=0.9, alpha=-0.302, Scr/kappa = 1.1111 > 1
    # val = 142 * (1.1111^-1.200) * (0.9938^55) * 1.0 = ~89.1 mL/min/1.73m2
    egfr = calculate_egfr_ckd_epi_2021(creatinine_mg_dl=1.0, age=55, gender="M")
    assert egfr is not None
    assert 88.0 <= egfr <= 91.0

# 2. CKD-EPI 2021: Male high creatinine (severe renal impairment)
def test_ckd_epi_male_high_creatinine():
    # 60 yo male, Scr 3.5 mg/dL
    egfr = calculate_egfr_ckd_epi_2021(creatinine_mg_dl=3.5, age=60, gender="M")
    assert egfr is not None
    assert 15.0 <= egfr <= 22.0

# 3. CKD-EPI 2021: Female reference calculation
def test_ckd_epi_female_reference():
    # 55 yo female, Scr 0.8 mg/dL: kappa=0.7, alpha=-0.241, Scr/kappa = 1.1428 > 1
    egfr = calculate_egfr_ckd_epi_2021(creatinine_mg_dl=0.8, age=55, gender="F")
    assert egfr is not None
    assert 85.0 <= egfr <= 92.0

# 4. CKD-EPI 2021: Female low creatinine (Scr <= kappa)
def test_ckd_epi_female_low_creatinine():
    # 30 yo female, Scr 0.6 mg/dL: Scr/0.7 < 1 -> uses alpha = -0.241
    egfr = calculate_egfr_ckd_epi_2021(creatinine_mg_dl=0.6, age=30, gender="F")
    assert egfr is not None
    assert egfr > 110.0

# 5. CKD-EPI 2021: Female gender string variations
def test_ckd_epi_female_string_normalization():
    egfr_f = calculate_egfr_ckd_epi_2021(1.0, 50, "F")
    egfr_female = calculate_egfr_ckd_epi_2021(1.0, 50, "FEMALE")
    egfr_lower = calculate_egfr_ckd_epi_2021(1.0, 50, "female")
    assert egfr_f == egfr_female == egfr_lower
    assert egfr_f is not None

# 6. CKD-EPI 2021: Default or unknown gender behaves as male multiplier (1.0)
def test_ckd_epi_unknown_gender():
    egfr_none = calculate_egfr_ckd_epi_2021(1.0, 50, None)
    egfr_m = calculate_egfr_ckd_epi_2021(1.0, 50, "M")
    assert egfr_none == egfr_m

# 7. CKD-EPI 2021: Invalid/boundary age inputs
def test_ckd_epi_invalid_age():
    assert calculate_egfr_ckd_epi_2021(1.0, 0, "M") is None
    assert calculate_egfr_ckd_epi_2021(1.0, -10, "M") is None
    assert calculate_egfr_ckd_epi_2021(1.0, 150, "M") is None
    assert calculate_egfr_ckd_epi_2021(1.0, None, "M") is None

# 8. CKD-EPI 2021: Invalid/boundary creatinine inputs
def test_ckd_epi_invalid_creatinine():
    assert calculate_egfr_ckd_epi_2021(0.0, 50, "M") is None
    assert calculate_egfr_ckd_epi_2021(-1.5, 50, "M") is None
    assert calculate_egfr_ckd_epi_2021(None, 50, "M") is None

# 9. CKD-EPI 2021: Non-finite inputs (NaN, Inf)
def test_ckd_epi_non_finite_inputs():
    assert calculate_egfr_ckd_epi_2021(float("nan"), 50, "M") is None
    assert calculate_egfr_ckd_epi_2021(1.0, float("nan"), "M") is None
    assert calculate_egfr_ckd_epi_2021(float("inf"), 50, "M") is None
    assert calculate_egfr_ckd_epi_2021(1.0, float("inf"), "M") is None

# 10. Cockcroft-Gault: Male reference calculation
def test_crcl_male_reference():
    # 60 yo male, 72 kg, Scr 1.0 mg/dL:
    # CrCl = [(140 - 60) * 72] / (72 * 1.0) = 80.0 mL/min
    crcl = calculate_crcl_cockcroft_gault(creatinine_mg_dl=1.0, age=60, weight_kg=72.0, gender="M")
    assert crcl == 80.0

# 11. Cockcroft-Gault: Female reference calculation
def test_crcl_female_reference():
    # 60 yo female, 72 kg, Scr 1.0 mg/dL:
    # CrCl = 80.0 * 0.85 = 68.0 mL/min
    crcl = calculate_crcl_cockcroft_gault(creatinine_mg_dl=1.0, age=60, weight_kg=72.0, gender="F")
    assert crcl == 68.0

# 12. Cockcroft-Gault: Female gender string normalization
def test_crcl_female_normalization():
    crcl_f = calculate_crcl_cockcroft_gault(1.2, 65, 60.0, "F")
    crcl_female = calculate_crcl_cockcroft_gault(1.2, 65, 60.0, "FEMALE")
    crcl_word = calculate_crcl_cockcroft_gault(1.2, 65, 60.0, "female")
    assert crcl_f == crcl_female == crcl_word
    assert crcl_f is not None

# 13. Cockcroft-Gault: Invalid weight
def test_crcl_invalid_weight():
    assert calculate_crcl_cockcroft_gault(1.0, 50, 0.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 50, -5.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 50, None, "M") is None

# 14. Cockcroft-Gault: Invalid age
def test_crcl_invalid_age():
    assert calculate_crcl_cockcroft_gault(1.0, 0, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, -1, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 140, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, None, 70.0, "M") is None

# 15. Cockcroft-Gault: Invalid creatinine
def test_crcl_invalid_creatinine():
    assert calculate_crcl_cockcroft_gault(0.0, 50, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(-1.0, 50, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(None, 50, 70.0, "M") is None

# 16. Cockcroft-Gault: Non-finite inputs
def test_crcl_non_finite_inputs():
    assert calculate_crcl_cockcroft_gault(float("nan"), 50, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, float("nan"), 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 50, float("nan"), "M") is None
    assert calculate_crcl_cockcroft_gault(float("inf"), 50, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, float("inf"), 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 50, float("inf"), "M") is None

# 17. Non-numeric string inputs return None safely
def test_string_type_errors_return_none():
    assert calculate_egfr_ckd_epi_2021("invalid", 50, "M") is None
    assert calculate_crcl_cockcroft_gault("invalid", 50, 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, "fifty", 70.0, "M") is None
    assert calculate_crcl_cockcroft_gault(1.0, 50, "seventy", "M") is None

# 18. Cockcroft-Gault elderly boundary
def test_crcl_elderly_boundary():
    crcl = calculate_crcl_cockcroft_gault(1.0, 90, 60.0, "M")
    assert crcl is not None
    # [(140 - 90) * 60] / 72 = 3000 / 72 = 41.7
    assert crcl == 41.7

# 19. Clinical distinction: eGFR and CrCl are distinct measures and non-interchangeable
def test_egfr_crcl_distinct_measures():
    # 80 yo female, 45 kg, Scr 1.2 mg/dL
    egfr = calculate_egfr_ckd_epi_2021(1.2, 80, "F")
    crcl = calculate_crcl_cockcroft_gault(1.2, 80, 45.0, "F")
    assert egfr is not None
    assert crcl is not None
    # CrCl in small elderly females is significantly lower than indexed eGFR
    assert egfr != crcl
    assert crcl < egfr
