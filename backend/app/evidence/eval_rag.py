"""
Quantitative RAG Retrieval Evaluation Engine for MEDHA / AushadhiDose.
Evaluates BM25-only, Vector-only, and Hybrid (BM25+FAISS) retrieval architectures
against a clinically vetted benchmark using IR metrics (Recall@k, Precision@k, MRR, nDCG@k).
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

# Ensure backend directory is in sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.evidence.retriever import HybridRetriever

BENCHMARK_PATH = Path(__file__).resolve().parent / "rag_benchmark.json"
REPORTS_DIR = REPO_ROOT / "reports"
OUTPUT_METRICS_PATH = REPORTS_DIR / "rag_benchmark_results.json"

def calculate_dcg(relevance_scores: List[float], k: int) -> float:
    dcg = 0.0
    for i in range(min(k, len(relevance_scores))):
        rel = relevance_scores[i]
        dcg += (2.0 ** rel - 1.0) / np.log2(i + 2)
    return dcg

def calculate_ndcg(retrieved_chunk_ids: List[str], gold_relevance: Dict[str, int], k: int) -> float:
    if not gold_relevance:
        return 0.0
    actual_rels = [gold_relevance.get(cid, 0) for cid in retrieved_chunk_ids[:k]]
    actual_dcg = calculate_dcg(actual_rels, k)
    ideal_rels = sorted(gold_relevance.values(), reverse=True)[:k]
    ideal_dcg = calculate_dcg(ideal_rels, k)
    if ideal_dcg <= 0.0:
        return 0.0
    return actual_dcg / ideal_dcg

def evaluate_retrieval_system(
    benchmark_data: Dict[str, Any],
    retriever: HybridRetriever,
    alpha: float,
    config_name: str
) -> Dict[str, Any]:
    queries = benchmark_data.get("queries", [])
    num_queries = len(queries)
    if num_queries == 0:
        return {"error": "No queries found in benchmark"}

    recalls_at_1 = []
    recalls_at_3 = []
    recalls_at_5 = []
    precisions_at_1 = []
    precisions_at_3 = []
    precisions_at_5 = []
    mrrs = []
    ndcgs_at_3 = []
    ndcgs_at_5 = []
    latencies_ms = []
    failures = 0

    per_query_details = []

    for q in queries:
        qid = q["query_id"]
        qtext = q["query_text"]
        gold_chunks = set(q["gold_chunk_ids"])
        gold_relevance = q.get("relevance_grades", {cid: 2 for cid in gold_chunks})

        t0 = time.perf_counter()
        results = retriever.retrieve(query=qtext, top_k=5, alpha=alpha)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

        retrieved_ids = [r["chunk_id"] for r in results]
        if not retrieved_ids:
            failures += 1

        # Calculate Recall@k and Precision@k
        hits_1 = len(gold_chunks.intersection(set(retrieved_ids[:1])))
        hits_3 = len(gold_chunks.intersection(set(retrieved_ids[:3])))
        hits_5 = len(gold_chunks.intersection(set(retrieved_ids[:5])))

        rec_1 = hits_1 / len(gold_chunks) if gold_chunks else 0.0
        rec_3 = hits_3 / len(gold_chunks) if gold_chunks else 0.0
        rec_5 = hits_5 / len(gold_chunks) if gold_chunks else 0.0

        prec_1 = hits_1 / 1.0
        prec_3 = hits_3 / 3.0
        prec_5 = hits_5 / 5.0

        # Calculate MRR
        mrr = 0.0
        for rank_idx, cid in enumerate(retrieved_ids):
            if cid in gold_chunks:
                mrr = 1.0 / (rank_idx + 1)
                break

        # Calculate nDCG@k
        ndcg_3 = calculate_ndcg(retrieved_ids, gold_relevance, k=3)
        ndcg_5 = calculate_ndcg(retrieved_ids, gold_relevance, k=5)

        recalls_at_1.append(rec_1)
        recalls_at_3.append(rec_3)
        recalls_at_5.append(rec_5)
        precisions_at_1.append(prec_1)
        precisions_at_3.append(prec_3)
        precisions_at_5.append(prec_5)
        mrrs.append(mrr)
        ndcgs_at_3.append(ndcg_3)
        ndcgs_at_5.append(ndcg_5)

        per_query_details.append({
            "query_id": qid,
            "retrieved_chunk_ids": retrieved_ids,
            "gold_chunk_ids": list(gold_chunks),
            "mrr": round(mrr, 4),
            "recall_at_3": round(rec_3, 4),
            "precision_at_3": round(prec_3, 4),
            "ndcg_at_3": round(ndcg_3, 4)
        })

    return {
        "configuration": config_name,
        "alpha_dense_weight": alpha,
        "queries_evaluated": num_queries,
        "failure_count": failures,
        "failure_rate": round(failures / num_queries, 4),
        "mean_recall_at_1": round(float(np.mean(recalls_at_1)), 4),
        "mean_recall_at_3": round(float(np.mean(recalls_at_3)), 4),
        "mean_recall_at_5": round(float(np.mean(recalls_at_5)), 4),
        "mean_precision_at_1": round(float(np.mean(precisions_at_1)), 4),
        "mean_precision_at_3": round(float(np.mean(precisions_at_3)), 4),
        "mean_precision_at_5": round(float(np.mean(precisions_at_5)), 4),
        "mean_mrr": round(float(np.mean(mrrs)), 4),
        "mean_ndcg_at_3": round(float(np.mean(ndcgs_at_3)), 4),
        "mean_ndcg_at_5": round(float(np.mean(ndcgs_at_5)), 4),
        "latency_stats_ms": {
            "median": round(float(np.median(latencies_ms)), 2),
            "mean": round(float(np.mean(latencies_ms)), 2),
            "p95": round(float(np.percentile(latencies_ms, 95)), 2)
        },
        "query_details": per_query_details
    }

def run_rag_benchmark_suite() -> Dict[str, Any]:
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    retriever = HybridRetriever(dimension=256)

    print("Running RAG Retrieval Benchmark across 3 configurations...")
    # 1. BM25 Only (alpha = 0.0)
    bm25_res = evaluate_retrieval_system(benchmark_data, retriever, alpha=0.0, config_name="BM25_Lexical_Only")
    print(f"BM25 Only: Recall@3={bm25_res['mean_recall_at_3']}, MRR={bm25_res['mean_mrr']}, nDCG@3={bm25_res['mean_ndcg_at_3']}")

    # 2. Vector Only (alpha = 1.0)
    vector_res = evaluate_retrieval_system(benchmark_data, retriever, alpha=1.0, config_name="Vector_Dense_Only")
    print(f"Vector Only: Recall@3={vector_res['mean_recall_at_3']}, MRR={vector_res['mean_mrr']}, nDCG@3={vector_res['mean_ndcg_at_3']}")

    # 3. Hybrid (alpha = 0.5)
    hybrid_res = evaluate_retrieval_system(benchmark_data, retriever, alpha=0.5, config_name="Hybrid_BM25_Dense")
    print(f"Hybrid: Recall@3={hybrid_res['mean_recall_at_3']}, MRR={hybrid_res['mean_mrr']}, nDCG@3={hybrid_res['mean_ndcg_at_3']}")

    summary_results = {
        "benchmark_meta": {
            "version": benchmark_data.get("benchmark_version"),
            "query_count": len(benchmark_data.get("queries", [])),
            "date": time.strftime("%Y-%m-%d %H:%M:%S UTC")
        },
        "configurations": {
            "BM25_Lexical_Only": bm25_res,
            "Vector_Dense_Only": vector_res,
            "Hybrid_BM25_Dense": hybrid_res
        }
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(OUTPUT_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)

    print(f"All RAG benchmark evaluation artifacts saved to: {OUTPUT_METRICS_PATH}")
    return summary_results

if __name__ == "__main__":
    run_rag_benchmark_suite()
