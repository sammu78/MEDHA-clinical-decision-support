"""
Fact-Dimension Relational Schema for MEDHA / AushadhiDose CDSS.
Unifies patient cohorts, pre-decision clinical measurements, commercial formulations,
and evidence-based dosing rules into a standardized Star/Snowflake schema.
"""

SCHEMA_VERSION = "2.2.0"

DDL_STATEMENTS = [
    # ---------------------------------------------------------
    # DIMENSION 1: dim_patient
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS dim_patient (
        patient_id TEXT PRIMARY KEY,
        subject_id INTEGER NOT NULL UNIQUE,
        anchor_age INTEGER,
        gender TEXT,
        anchor_year INTEGER,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_dim_patient_subject ON dim_patient(subject_id);",

    # ---------------------------------------------------------
    # DIMENSION 2: dim_disease
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS dim_disease (
        disease_id TEXT PRIMARY KEY,
        icd10_code TEXT,
        disease_name TEXT NOT NULL,
        category TEXT NOT NULL,
        icmr_guideline_ref TEXT,
        is_supported_in_cdss INTEGER NOT NULL DEFAULT 1
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_dim_disease_cat ON dim_disease(category);",

    # ---------------------------------------------------------
    # DIMENSION 3: dim_medicine
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS dim_medicine (
        medicine_id TEXT PRIMARY KEY,
        generic_name TEXT NOT NULL UNIQUE,
        drug_class TEXT,
        primary_route TEXT,
        atc_code TEXT,
        is_high_alert INTEGER NOT NULL DEFAULT 0
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_dim_medicine_name ON dim_medicine(generic_name);",

    # ---------------------------------------------------------
    # DIMENSION 4: dim_commercial_product (Indian Brands & Packaging)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS dim_commercial_product (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id TEXT,
        brand_name TEXT NOT NULL,
        composition_raw TEXT,
        formulation TEXT,
        route TEXT,
        strength TEXT,
        units TEXT,
        manufacturer TEXT,
        is_combination INTEGER DEFAULT 0,
        verified_source TEXT DEFAULT 'CDSCO/JanAushadhi/1mg Staging',
        verified_date TEXT,
        FOREIGN KEY (medicine_id) REFERENCES dim_medicine(medicine_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_dim_comm_brand ON dim_commercial_product(brand_name);",
    "CREATE INDEX IF NOT EXISTS idx_dim_comm_med ON dim_commercial_product(medicine_id);",

    # ---------------------------------------------------------
    # DIMENSION 5: dim_lab_test
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS dim_lab_test (
        lab_itemid INTEGER PRIMARY KEY,
        lab_name TEXT NOT NULL,
        loinc_code TEXT,
        standard_unit TEXT NOT NULL,
        normal_min REAL,
        normal_max REAL,
        critical_low REAL,
        critical_high REAL
    );
    """,

    # ---------------------------------------------------------
    # FACT 1: fact_treatment_decision (Prescriptions & ML Records)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS fact_treatment_decision (
        decision_id TEXT PRIMARY KEY,
        subject_id INTEGER NOT NULL,
        hadm_id INTEGER,
        medicine_id TEXT NOT NULL,
        disease_id TEXT NOT NULL,
        decision_time TEXT NOT NULL,
        dose_numeric REAL,
        dose_unit TEXT,
        route TEXT,
        pre_glucose REAL,
        pre_creatinine REAL,
        pre_potassium REAL,
        pre_sodium REAL,
        pre_bun REAL,
        FOREIGN KEY (medicine_id) REFERENCES dim_medicine(medicine_id),
        FOREIGN KEY (disease_id) REFERENCES dim_disease(disease_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_fact_tx_subject ON fact_treatment_decision(subject_id);",
    "CREATE INDEX IF NOT EXISTS idx_fact_tx_disease ON fact_treatment_decision(disease_id);",
    "CREATE INDEX IF NOT EXISTS idx_fact_tx_med ON fact_treatment_decision(medicine_id);",
    "CREATE INDEX IF NOT EXISTS idx_fact_tx_time ON fact_treatment_decision(decision_time);",

    # ---------------------------------------------------------
    # FACT 2: fact_lab_event (Time-Series Laboratory Events)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS fact_lab_event (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        hadm_id INTEGER,
        lab_itemid INTEGER NOT NULL,
        charttime TEXT NOT NULL,
        valuenum REAL NOT NULL,
        flag TEXT,
        FOREIGN KEY (lab_itemid) REFERENCES dim_lab_test(lab_itemid)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_fact_lab_sub_time ON fact_lab_event(subject_id, charttime);",
    "CREATE INDEX IF NOT EXISTS idx_fact_lab_item ON fact_lab_event(lab_itemid);",

    # ---------------------------------------------------------
    # FACT 3: fact_dosing_rule (Guideline Rules & Renal Gates)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS fact_dosing_rule (
        rule_id TEXT PRIMARY KEY,
        medicine_id TEXT NOT NULL,
        disease_id TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        min_age_y REAL,
        max_age_y REAL,
        min_crcl REAL,
        max_crcl REAL,
        min_egfr REAL,
        max_egfr REAL,
        max_dose_mg REAL,
        severity TEXT NOT NULL DEFAULT 'warning',
        action TEXT NOT NULL DEFAULT 'ADJUST_DOSE',
        rationale TEXT NOT NULL,
        evidence_source TEXT NOT NULL,
        review_date TEXT,
        FOREIGN KEY (medicine_id) REFERENCES dim_medicine(medicine_id),
        FOREIGN KEY (disease_id) REFERENCES dim_disease(disease_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_fact_rule_med_dis ON fact_dosing_rule(medicine_id, disease_id);",

    # ---------------------------------------------------------
    # SUPPORTING TABLE: import_batches (Audit and Provenance)
    # ---------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS import_batches (
        batch_id TEXT PRIMARY KEY,
        source_file TEXT NOT NULL,
        records_read INTEGER NOT NULL,
        records_imported INTEGER NOT NULL,
        records_rejected INTEGER NOT NULL,
        status TEXT NOT NULL,
        reconciliation_report TEXT,
        imported_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
    );
    """,

    # ---------------------------------------------------------
    # VIEWS: Analytical Convenience
    # ---------------------------------------------------------
    """
    CREATE VIEW IF NOT EXISTS v_treatment_summary AS
    SELECT 
        d.disease_name,
        m.generic_name,
        COUNT(f.decision_id) AS total_orders,
        ROUND(AVG(f.dose_numeric), 2) AS mean_dose,
        ROUND(MIN(f.dose_numeric), 2) AS min_dose,
        ROUND(MAX(f.dose_numeric), 2) AS max_dose,
        f.dose_unit,
        f.route
    FROM fact_treatment_decision f
    JOIN dim_disease d ON f.disease_id = d.disease_id
    JOIN dim_medicine m ON f.medicine_id = m.medicine_id
    WHERE f.dose_numeric IS NOT NULL AND f.dose_numeric > 0
    GROUP BY d.disease_name, m.generic_name, f.dose_unit, f.route;
    """
]
