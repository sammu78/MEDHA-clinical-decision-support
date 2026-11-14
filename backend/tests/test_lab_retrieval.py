import pytest
from datetime import datetime
from app.services.lab_retrieval_service import PreDecisionLabRetrievalService
from app.database.db import get_db_connection

def test_leakage_free_lab_retrieval():
    # Pick a subject known to have lab events
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject_id, charttime FROM fact_lab_event LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "fact_lab_event should not be empty"
    subject_id = row["subject_id"]
    test_time = row["charttime"]

    # Decision time set exactly at test_time
    labs = PreDecisionLabRetrievalService.get_pre_decision_labs(subject_id, test_time)
    assert isinstance(labs, dict)
    assert "glucose" in labs
    assert "creatinine" in labs
    assert "potassium" in labs
    assert "sodium" in labs
    assert "bun" in labs

    # Test ML feature vector formatting
    feat_row = PreDecisionLabRetrievalService.format_ml_feature_row(65.0, labs)
    expected_order = ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
    assert list(feat_row.keys()) == expected_order
    assert feat_row['age'] == 65.0
