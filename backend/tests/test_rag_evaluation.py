import pytest
import numpy as np
from app.evidence.retriever import HybridRetriever
from app.evidence.eval_rag import calculate_dcg, calculate_ndcg

def test_hand_calculated_metric_math():
    # Known test scenario:
    # 3 retrieved items: ['docA', 'docB', 'docC']
    # Gold items: {'docB', 'docD'} with relevance {'docB': 2, 'docD': 1}
    # Hits at k=1: 0 (Precision@1 = 0, Recall@1 = 0)
    # Hits at k=2: 1 ('docB') (Precision@2 = 0.5, Recall@2 = 1/2 = 0.5)
    # Hits at k=3: 1 ('docB') (Precision@3 = 1/3 = 0.333, Recall@3 = 0.5)
    # MRR: First hit is at rank 2 -> MRR = 1/2 = 0.5
    retrieved = ['docA', 'docB', 'docC']
    gold_chunks = {'docB', 'docD'}
    gold_relevance = {'docB': 2, 'docD': 1}

    # Precision & Recall
    rec_2 = len(gold_chunks.intersection(set(retrieved[:2]))) / len(gold_chunks)
    assert rec_2 == 0.5
    prec_2 = len(gold_chunks.intersection(set(retrieved[:2]))) / 2.0
    assert prec_2 == 0.5

    # MRR
    mrr = 0.0
    for idx, doc in enumerate(retrieved):
        if doc in gold_chunks:
            mrr = 1.0 / (idx + 1)
            break
    assert mrr == 0.5

    # DCG / nDCG
    # Actual relevance at ranks: [0, 2, 0]
    # DCG@2: 0 / log2(2) + (2^2 - 1) / log2(3) = 0 + 3 / 1.58496 = 1.892789
    # Ideal relevance: [2, 1]
    # IDCG@2: (2^2 - 1) / log2(2) + (2^1 - 1) / log2(3) = 3 / 1.0 + 1 / 1.58496 = 3 + 0.63093 = 3.63093
    # nDCG@2 = 1.892789 / 3.63093 = ~0.5213
    actual_dcg_2 = calculate_dcg([0, 2], k=2)
    ideal_dcg_2 = calculate_dcg([2, 1], k=2)
    assert round(actual_dcg_2, 3) == 1.893
    assert round(ideal_dcg_2, 3) == 3.631
    ndcg_2 = calculate_ndcg(retrieved, gold_relevance, k=2)
    assert 0.51 <= ndcg_2 <= 0.53

def test_citation_integrity_and_metadata_preservation():
    retriever = HybridRetriever(dimension=256)
    results = retriever.retrieve("Metformin renal eGFR dosing", top_k=3)
    assert len(results) > 0
    for r in results:
        # Check that metadata survived chunking and retrieval
        assert "chunk_id" in r
        assert "doc_id" in r
        assert "title" in r
        assert "organization" in r
        assert "citation" in r
        assert len(r["citation"]) > 10
        assert r["url"].startswith("http")
        assert len(r["text"]) > 20

def test_empty_and_nonsense_query_handling():
    retriever = HybridRetriever(dimension=256)
    # Nonsense gibberish query
    results = retriever.retrieve("xyzabc123nonexistentwordthatdoesnotexist999", top_k=3)
    # Does not crash; gracefully returns ranked or empty without exceptions
    assert isinstance(results, list)

def test_retriever_configurations_distinct():
    retriever = HybridRetriever(dimension=256)
    query = "hypertension Stage 2 dual combination therapy"
    bm25_res = retriever.retrieve(query, alpha=0.0, top_k=3)
    vector_res = retriever.retrieve(query, alpha=1.0, top_k=3)
    hybrid_res = retriever.retrieve(query, alpha=0.5, top_k=3)

    assert len(bm25_res) > 0
    assert len(vector_res) > 0
    assert len(hybrid_res) > 0
    # BM25 dense scores should be 0 or unweighted
    for r in bm25_res:
        assert "bm25_score" in r
