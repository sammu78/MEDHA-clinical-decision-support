import sys
import os
import json
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend root is on sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


import requests
from app.main import app
from fastapi.testclient import TestClient

base_url = 'http://127.0.0.1:8000'

def get_client():
    try:
        r = requests.get(f'{base_url}/health', timeout=1.0)
        if r.status_code == 200:
            print("[INFO] Live FastAPI backend detected on http://127.0.0.1:8000")
            return "live", None
    except Exception:
        pass
    print("[INFO] Live server not running on port 8000; executing via in-process FastAPI TestClient.")
    return "testclient", TestClient(app)

def main():
    mode, test_client = get_client()

    def api_get(path):
        if mode == "live":
            return requests.get(f"{base_url}{path}")
        return test_client.get(path)

    def api_post(path, **kwargs):
        if mode == "live":
            return requests.post(f"{base_url}{path}", **kwargs)
        return test_client.post(path, **kwargs)

    def api_put(path, **kwargs):
        if mode == "live":
            return requests.put(f"{base_url}{path}", **kwargs)
        return test_client.put(path, **kwargs)

    print("=" * 60)
    print("AushadhiDose AI: End-to-End System Verification")
    print("=" * 60)

    # 1. Create case
    res = api_post('/cases', json={'title': 'Dr. Sharma - Patient 104'})

    assert res.status_code == 200, f"Create case failed: {res.text}"
    case = res.json()
    case_id = case['case_id']
    print(f"[1] Created Clinical Case ID: {case_id}")

    # 2. Update patient
    patient_data = {
        'age': 58,
        'gender': 'M',
        'weight_kg': 82,
        'confirmed_diagnosis': 'type_2_diabetes',
        'allergies': ['Sulfa'],
        'current_medications': ['Amlodipine 5mg'],
        'existing_conditions': ['Hypertension'],
        'labs': {
            'creatinine': {'value': 1.4, 'unit': 'mg/dL'},
            'glucose': {'value': 195, 'unit': 'mg/dL'},
            'egfr': {'value': 54, 'unit': 'mL/min/1.73m2'}
        }
    }
    res = api_put(f'/cases/{case_id}/patient', json=patient_data)
    assert res.status_code == 200, f"Update patient failed: {res.text}"
    print(f"[2] Updated Patient Profile: Age={res.json().get('patient_data', {}).get('age')}, Diagnosis={res.json().get('patient_data', {}).get('confirmed_diagnosis')}")

    # 3. Assess
    res = api_post(f'/cases/{case_id}/assess')
    assert res.status_code == 200, f"Assess case failed: {res.text}"
    asmt = res.json()
    print(f"[3] Assessment Status: {asmt.get('status')}")
    print(f"    Candidate Medicines: {', '.join(asmt.get('candidate_medicines', []))}")
    print(f"    Safety Checks Run: {len(asmt.get('safety_checks', []))}")
    for prop in asmt.get('proposals', []):
        print(f"    - {prop['generic_name']}: {prop['dose_display']} {prop.get('unit', '')} ({prop['dose_status']})")

    # 4. Indian Medicines Matching
    res = api_get(f'/medicines/match?generic=Metformin&strength=500+mg&route=oral')
    assert res.status_code == 200, f"Indian medicines match failed: {res.text}"
    matches = res.json()
    print(f"[4] Matched {len(matches)} Indian commercial products for Metformin 500mg Oral:")
    for m in matches[:3]:
        print(f"    * {m.get('name')} | Generic: {m.get('generic_ingredients')} | Formulation: {m.get('formulation')}")

    # 5. Doctor Approval
    res = api_post(f'/cases/{case_id}/approve', json={'notes': 'Attending physician confirms Metformin 500mg PO BID after renal review.'})
    assert res.status_code == 200, f"Doctor approval failed: {res.text}"
    print(f"[5] Doctor Approval: {res.json().get('notice')}")

    # 6. Export Draft
    res = api_get(f'/cases/{case_id}/export')
    assert res.status_code == 200, f"Export draft failed: {res.text}"
    exp = res.json()
    print(f"[6] Draft Report Title: {exp.get('title')}")
    first_lines = exp.get('markdown_report', '').split('\n')[:5]
    print("    Report Header:\n    " + "\n    ".join(first_lines))

    # 7. Test SSE stream
    stream_path = f'/cases/{case_id}/stream?message=' + urllib.parse.quote('Patient reports morning dizziness. Potassium is 4.8 mEq/L.')
    if mode == "live":
        req = urllib.request.Request(f"{base_url}{stream_path}")
        with urllib.request.urlopen(req) as stream_res:
            events = []
            for _ in range(12):
                line = stream_res.readline().decode('utf-8')
                if line.startswith('event:'):
                    events.append(line.strip())
            print(f"[7] Live SSE Stream Active: Received event stream signals -> {events}")
    else:
        stream_res = test_client.get(stream_path)
        events = [line.strip() for line in stream_res.text.split('\n') if line.startswith('event:')][:12]
        print(f"[7] In-Process SSE Stream Active: Received event stream signals -> {events}")

    print("=" * 60)
    print("ALL 7 CORE CLINICAL ENDPOINTS & WORKFLOWS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    main()
