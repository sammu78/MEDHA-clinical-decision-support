import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.database.schema import DDL_STATEMENTS, SCHEMA_VERSION

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DB_DIR, "clinical_decision_support.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        doctor_id TEXT NOT NULL,
        title TEXT NOT NULL,
        diagnosis_id TEXT,
        diagnosis_name TEXT,
        patient_data TEXT NOT NULL,
        patient_version INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        approved_by_doctor INTEGER NOT NULL DEFAULT 0,
        approved_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 2. Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        extracted_entities TEXT,
        structured_cards TEXT,
        citations TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
    );
    """)

    # 3. Assessments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        assessment_id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        patient_version INTEGER NOT NULL,
        status TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        approved_by_doctor INTEGER NOT NULL DEFAULT 0,
        approved_at TEXT,
        doctor_notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
    );
    """)

    # 4. Evidence documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence_documents (
        doc_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        organization TEXT NOT NULL,
        url TEXT NOT NULL,
        publication_date TEXT,
        retrieval_date TEXT NOT NULL,
        review_status TEXT NOT NULL,
        applicable_population TEXT,
        content TEXT NOT NULL,
        chunk_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    # 5. Evidence chunks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence_chunks (
        chunk_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        disease_tags TEXT,
        medicine_tags TEXT,
        population_tags TEXT,
        source_citation TEXT NOT NULL,
        source_url TEXT NOT NULL,
        FOREIGN KEY (doc_id) REFERENCES evidence_documents(doc_id) ON DELETE CASCADE
    );
    """)

    # 6. Indian medicines table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indian_medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        generic_ingredients TEXT NOT NULL,
        composition_raw TEXT,
        uses TEXT,
        side_effects TEXT,
        image_url TEXT,
        formulation TEXT,
        route TEXT,
        strength TEXT,
        units TEXT,
        release_type TEXT,
        is_combination INTEGER DEFAULT 0,
        source TEXT DEFAULT 'CDSCO/JanAushadhi/1mg Staging',
        verified_date TEXT
    );
    """)

    # 7. Safety decision records audit table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safety_decision_records (
        record_id TEXT PRIMARY KEY,
        assessment_id TEXT,
        case_id TEXT,
        rule_id TEXT NOT NULL,
        rule_version TEXT NOT NULL,
        check_name TEXT NOT NULL,
        status TEXT NOT NULL,
        severity TEXT NOT NULL,
        findings TEXT NOT NULL,
        can_authorize_dose INTEGER NOT NULL,
        source_reference TEXT,
        evaluated_at TEXT NOT NULL
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_safety_records_case ON safety_decision_records(case_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_safety_records_rule ON safety_decision_records(rule_id);")

    # 8. Fact-Dimension Schema initialization
    for stmt in DDL_STATEMENTS:
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"Schema statement warning: {e}")

    conn.commit()
    conn.close()

# Auto-initialize on module load
init_db()
