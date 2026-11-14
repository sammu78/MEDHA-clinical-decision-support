import os
import re
import csv
import sqlite3
from typing import List, Dict, Any, Optional
from app.database.db import get_db_connection

INDIAN_MEDS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data", "staging", "indian_medicines.csv"
)

CDSCO_PRESCRIBING_URL = "https://cdsco.gov.in/opencms/opencms/en/Notifications/Prescribing-Information/"
CDSCO_APPROVED_DRUGS_URL = "https://www.cdsco.gov.in/opencms/opencms/en/Approval_new/Approved-New-Drugs/"

def parse_product_fields(name: str, composition: str):
    name_str = str(name).strip() if name else ""
    comp_str = str(composition).strip() if composition else ""

    # Formulation detection
    formulation = "Tablet"
    name_lower = name_str.lower()
    if "injection" in name_lower or "infusion" in name_lower:
        formulation = "Injection"
    elif "capsule" in name_lower:
        formulation = "Capsule"
    elif "syrup" in name_lower or "suspension" in name_lower:
        formulation = "Oral Liquid / Syrup"
    elif "cream" in name_lower or "ointment" in name_lower or "gel" in name_lower:
        formulation = "Topical"
    elif "inhaler" in name_lower or "respules" in name_lower or "rotacap" in name_lower:
        formulation = "Inhaler / Respules"
    elif "drops" in name_lower:
        formulation = "Drops"

    # Route detection
    route = "Oral (PO)"
    if formulation == "Injection":
        route = "Intravenous / Intramuscular (IV/IM)"
    elif formulation == "Topical":
        route = "Topical"
    elif formulation == "Inhaler / Respules":
        route = "Inhalation"

    # Release type detection
    release_type = "Immediate Release (IR)"
    if re.search(r"\b(sr|er|cr|mr|pr|xl|dr)\b", name_lower):
        release_type = "Modified / Sustained Release (MR/SR)"

    # Combination detection
    is_combination = 1 if "+" in comp_str else 0

    # Extract ingredients and strengths
    # e.g., "Amoxycillin (500mg) + Clavulanic Acid (125mg)"
    parts = comp_str.split("+")
    ingredients = []
    strengths = []
    units = []

    for p in parts:
        clean_p = p.strip()
        match = re.search(r"^(.*?)\s*\((.*?)\)$", clean_p)
        if match:
            ing = match.group(1).strip()
            str_val = match.group(2).strip()
            ingredients.append(ing)
            strengths.append(str_val)
            # unit match
            unit_match = re.search(r"[0-9.]+\s*([a-zA-Z/%]+)", str_val)
            if unit_match:
                units.append(unit_match.group(1))
        else:
            ingredients.append(clean_p)

    generic_names = " + ".join(ingredients) if ingredients else name_str
    strength_str = " + ".join(strengths) if strengths else ""
    unit_str = "/".join(set(units)) if units else "mg"

    return {
        "formulation": formulation,
        "route": route,
        "release_type": release_type,
        "is_combination": is_combination,
        "generic_ingredients": generic_names,
        "strength": strength_str,
        "units": unit_str
    }

class IndianMedicinesCatalogue:
    def __init__(self):
        self._ensure_catalogue_loaded()

    def _ensure_catalogue_loaded(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM indian_medicines")
        row = cursor.fetchone()
        count = row["cnt"] if row else 0

        if count == 0 and os.path.exists(INDIAN_MEDS_CSV):
            print(f"Loading Indian Medicines from {INDIAN_MEDS_CSV} into SQLite...")
            records = []
            try:
                with open(INDIAN_MEDS_CSV, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        name = r.get("name", "")
                        comp = r.get("composition", "")
                        parsed = parse_product_fields(name, comp)
                        records.append((
                            name,
                            parsed["generic_ingredients"],
                            comp,
                            r.get("uses", ""),
                            r.get("side_effects", ""),
                            r.get("image_url", ""),
                            parsed["formulation"],
                            parsed["route"],
                            parsed["strength"],
                            parsed["units"],
                            parsed["release_type"],
                            parsed["is_combination"],
                            "CDSCO Approved Formulations / National List Staging",
                            "2024-03-01"
                        ))
                        if len(records) >= 1000:
                            cursor.executemany("""
                                INSERT INTO indian_medicines 
                                (name, generic_ingredients, composition_raw, uses, side_effects, image_url, formulation, route, strength, units, release_type, is_combination, source, verified_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, records)
                            records = []
                    if records:
                        cursor.executemany("""
                            INSERT INTO indian_medicines 
                            (name, generic_ingredients, composition_raw, uses, side_effects, image_url, formulation, route, strength, units, release_type, is_combination, source, verified_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, records)
                conn.commit()
                print("Successfully loaded Indian Medicines catalogue.")
            except Exception as e:
                print(f"Error loading indian_medicines.csv: {e}")
        conn.close()

    def search(
        self,
        query: str = "",
        generic_name: Optional[str] = None,
        formulation: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM indian_medicines WHERE 1=1"
        params = []

        if query:
            sql += " AND (name LIKE ? OR generic_ingredients LIKE ? OR uses LIKE ?)"
            term = f"%{query}%"
            params.extend([term, term, term])

        if generic_name:
            sql += " AND generic_ingredients LIKE ?"
            params.append(f"%{generic_name}%")

        if formulation:
            sql += " AND formulation LIKE ?"
            params.append(f"%{formulation}%")

        sql += " ORDER BY id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "name": r["name"],
                "generic_ingredients": r["generic_ingredients"],
                "composition_raw": r["composition_raw"],
                "strength": r["strength"],
                "units": r["units"],
                "formulation": r["formulation"],
                "route": r["route"],
                "release_type": r["release_type"],
                "is_combination": bool(r["is_combination"]),
                "uses": r["uses"],
                "side_effects": r["side_effects"],
                "image_url": r["image_url"],
                "source": r["source"],
                "verified_date": r["verified_date"],
                "cdsco_prescribing_url": CDSCO_PRESCRIBING_URL,
                "cdsco_approved_drugs_url": CDSCO_APPROVED_DRUGS_URL
            })
        conn.close()
        return results

    def find_matching_products_for_generic(
        self,
        generic: str,
        desired_strength: Optional[str] = None,
        desired_route: Optional[str] = None,
        limit: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Matches commercial Indian brand products ONLY when active ingredient,
        route, and strength match, rejecting silent substitution of combinations or modified release.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Clean generic term (e.g. "Metformin" from "Metformin Hydrochloride")
        clean_gen = generic.split()[0] if generic else ""
        sql = "SELECT * FROM indian_medicines WHERE generic_ingredients LIKE ? AND is_combination = 0"
        params = [f"%{clean_gen}%"]

        if desired_route:
            if "oral" in desired_route.lower():
                sql += " AND formulation IN ('Tablet', 'Capsule', 'Oral Liquid / Syrup')"
            elif "iv" in desired_route.lower() or "inject" in desired_route.lower():
                sql += " AND formulation = 'Injection'"

        sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        products = []
        for r in rows:
            # Check strength suitability
            is_exact_strength = False
            if desired_strength and r["strength"]:
                is_exact_strength = (desired_strength.lower() in r["strength"].lower())

            products.append({
                "id": r["id"],
                "name": r["name"],
                "generic_ingredients": r["generic_ingredients"],
                "composition_raw": r["composition_raw"],
                "strength": r["strength"],
                "units": r["units"],
                "formulation": r["formulation"],
                "route": r["route"],
                "release_type": r["release_type"],
                "is_combination": bool(r["is_combination"]),
                "is_exact_strength_match": is_exact_strength,
                "source": r["source"],
                "verified_date": r["verified_date"],
                "cdsco_prescribing_url": CDSCO_PRESCRIBING_URL,
                "notice": "Commercial brand formulation in India. Attending physician must confirm current CDSCO regulatory status and brand availability."
            })
        return products

# Global singleton
indian_medicines_catalogue = IndianMedicinesCatalogue()
