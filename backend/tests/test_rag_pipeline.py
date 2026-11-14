import os
import sys
import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.evidence.retriever import hybrid_retriever

@pytest.fixture
def client():
    return TestClient(app)

def test_rag_hybrid_retrieval_accuracy():
    """Verify hybrid retriever returns relevant guideline chunks with scoring metrics."""
    results = hybrid_retriever.retrieve(
        query="Metformin eGFR renal cutoff contraindication",
        disease_tag="type_2_diabetes",
        top_k=3
    )
    assert len(results) > 0
    top = results[0]
    assert "chunk_id" in top
    assert "hybrid_score" in top
    assert "bm25_score" in top
    assert "dense_score" in top
    assert "text" in top
    # Should match diabetes guideline
    assert any("diabetes" in tag.lower() for tag in top["disease_tags"])

def test_rag_guideline_qa_synthesis():
    """Verify RAG synthesis formats grounded answers with citations and safety warnings."""
    rag_response = hybrid_retriever.rag_answer(
        query="What is the recommended fluid protocol and NSAID hazard in Dengue fever?",
        disease_tag="dengue",
        top_k=2
    )
    assert rag_response["confidence"] > 0
    assert len(rag_response["sources"]) > 0
    answer = rag_response["answer"]
    assert "Evidence-Based Clinical Guidance" in answer
    assert "Verified Retrieval Sources" in answer
    assert "Dengue" in answer or "fluid" in answer.lower()

def test_evidence_search_endpoint(client):
    """Verify GET /evidence/search endpoint."""
    response = client.get("/evidence/search?q=tuberculosis+daily+fdc&top_k=3")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "tuberculosis daily fdc"
    assert "results" in data
    assert len(data["results"]) > 0
    first = data["results"][0]
    assert "hybrid_score" in first
    assert "organization" in first

def test_evidence_query_endpoint(client):
    """Verify POST /evidence/query endpoint for interactive RAG QA."""
    payload = {
        "query": "Can primaquine be safely administered in Plasmodium vivax without G6PD screening?",
        "disease_tag": "malaria",
        "top_k": 2
    }
    response = client.post("/evidence/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_document_ingestion_and_dynamic_retrieval(client):
    """Verify doctor-uploaded guidelines are parsed, chunked, and immediately searchable in FAISS + BM25."""
    doc_payload = {
        "doc_id": "test_aiims_sepsis_2024",
        "title": "AIIMS Protocol for Adult Septic Shock Resuscitation",
        "organization": "All India Institute of Medical Sciences",
        "url": "https://aiims.edu/guidelines/sepsis-2024",
        "disease_tag": "septic_shock",
        "content": "Septic shock initial resuscitation requires 30 mL/kg of IV crystalloid fluid within the first 3 hours.\n\nNorepinephrine is the first-choice vasopressor to target mean arterial pressure (MAP) >= 65 mmHg.\n\nEpinephrine or vasopressin may be added if MAP remains refractory to norepinephrine."
    }
    upload_res = client.post("/documents", json=doc_payload)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["chunks_indexed"] >= 3

    # Now verify it can be retrieved via the RAG search endpoint
    search_res = client.get("/evidence/search?q=norepinephrine+vasopressor+target+map&disease_tag=septic_shock")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["results_count"] > 0
    top_hit = search_data["results"][0]
    assert "AIIMS Protocol" in top_hit["title"] or "septic_shock" in top_hit["disease_tags"]
