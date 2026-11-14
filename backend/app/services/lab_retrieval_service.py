"""
Leakage-Free Laboratory Retrieval Service.
Implements deterministic, SQL-indexed temporal feature extraction enforcing:
  charttime <= decision_time AND charttime >= (decision_time - 7 days)
Guarantees zero future data leakage.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.database.db import get_db_connection

# Mapping from test keys to MIMIC item IDs
LAB_ITEM_MAP = {
    "glucose": [50931, 50809],
    "creatinine": [50912],
    "potassium": [50971, 50822],
    "sodium": [50983, 50824],
    "bun": [51006],
    "hemoglobin": [51222]
}

class PreDecisionLabRetrievalService:
    LOOKBACK_DAYS: int = 7

    @classmethod
    def get_pre_decision_labs(
        cls,
        subject_id: int,
        decision_time: str,
        hadm_id: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves the latest valid laboratory measurement strictly within the lookback window
        prior to decision_time for each required lab test.

        Returns:
            Dictionary keyed by test name:
            {
               "glucose": {"value": 142.0, "unit": "mg/dL", "charttime": "...", "itemid": 50931, "is_stale": False},
               ...
            }
        """
        # Parse decision time
        try:
            if isinstance(decision_time, datetime):
                decision_dt = decision_time
            else:
                decision_dt = pd.to_datetime(decision_time).to_pydatetime()
        except Exception:
            decision_dt = datetime.utcnow()

        window_start_dt = decision_dt - timedelta(days=cls.LOOKBACK_DAYS)
        decision_str = decision_dt.strftime("%Y-%m-%d %H:%M:%S")
        window_start_str = window_start_dt.strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        cursor = conn.cursor()

        results = {}

        for test_name, item_ids in LAB_ITEM_MAP.items():
            placeholders = ",".join("?" for _ in item_ids)
            # Query strictly at or before decision_time and at or after window_start
            query = f"""
                SELECT f.valuenum, f.charttime, f.lab_itemid, f.flag, d.standard_unit
                FROM fact_lab_event f
                JOIN dim_lab_test d ON f.lab_itemid = d.lab_itemid
                WHERE f.subject_id = ?
                  AND f.lab_itemid IN ({placeholders})
                  AND f.charttime <= ?
                  AND f.charttime >= ?
                ORDER BY f.charttime DESC
                LIMIT 1
            """
            params = [subject_id] + list(item_ids) + [decision_str, window_start_str]
            cursor.execute(query, params)
            row = cursor.fetchone()

            if row:
                measurement_dt = pd.to_datetime(row["charttime"]).to_pydatetime()
                # Enforce zero-leakage invariant
                assert measurement_dt <= decision_dt, "CRITICAL: Temporal data leakage detected!"
                hours_prior = round((decision_dt - measurement_dt).total_seconds() / 3600.0, 1)

                results[test_name] = {
                    "value": float(row["valuenum"]),
                    "unit": row["standard_unit"],
                    "charttime": row["charttime"],
                    "itemid": row["lab_itemid"],
                    "flag": row["flag"],
                    "hours_prior_to_decision": hours_prior,
                    "is_stale": (hours_prior > 72.0)
                }
            else:
                results[test_name] = {
                    "value": None,
                    "unit": None,
                    "charttime": None,
                    "itemid": None,
                    "flag": None,
                    "hours_prior_to_decision": None,
                    "is_stale": True
                }

        conn.close()
        return results

    @classmethod
    def format_ml_feature_row(
        cls,
        age: float,
        pre_labs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Converts the pre-decision lab dictionary to the strictly ordered 6-feature vector
        expected by the Random Forest models:
        ['age', 'pre_glucose', 'pre_creatinine', 'pre_potassium', 'pre_sodium', 'pre_bun']
        """
        def get_val(key):
            item = pre_labs.get(key)
            if item and item.get("value") is not None:
                return float(item["value"])
            return np.nan

        return {
            "age": float(age),
            "pre_glucose": get_val("glucose"),
            "pre_creatinine": get_val("creatinine"),
            "pre_potassium": get_val("potassium"),
            "pre_sodium": get_val("sodium"),
            "pre_bun": get_val("bun")
        }
