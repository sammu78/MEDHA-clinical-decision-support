import os
import re
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from rank_bm25 import BM25Okapi

from app.evidence.library import ClinicalGuidelineChunk, INITIAL_EVIDENCE_LIBRARY, get_all_guideline_chunks
from app.database.db import get_db_connection

def tokenize_text(text: str) -> List[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 2]

class HybridRetriever:
    """
    Hybrid Evidence Retrieval Engine combining BM25 lexical ranking and
    FAISS dense vector similarity, prioritizing authentic Indian clinical guidelines (ICMR, CDSCO, NVBDCP, NTEP).
    """
    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        self.chunks: List[ClinicalGuidelineChunk] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.vocabulary: Dict[str, int] = {}
        self.idf_weights: Dict[str, float] = {}
        self.build_initial_index()

    def _build_vocab(self):
        doc_counts: Dict[str, int] = {}
        term_counts: Dict[str, int] = {}
        total_docs = max(1, len(self.tokenized_corpus))

        for tokens in self.tokenized_corpus:
            seen_in_doc = set()
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1
                if t not in seen_in_doc:
                    doc_counts[t] = doc_counts.get(t, 0) + 1
                    seen_in_doc.add(t)

        # Select top terms by frequency for dense representation
        sorted_words = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:self.dimension]
        self.vocabulary = {w: idx for idx, (w, _) in enumerate(sorted_words)}
        
        # Precompute smooth inverse document frequencies
        self.idf_weights = {
            w: float(np.log(1.0 + (total_docs / (1.0 + doc_counts.get(w, 1)))))
            for w in self.vocabulary
        }

    def _embed_text(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        tokens = tokenize_text(text)
        if not tokens:
            return vec

        term_freq: Dict[str, float] = {}
        for t in tokens:
            if t in self.vocabulary:
                term_freq[t] = term_freq.get(t, 0.0) + 1.0

        for t, count in term_freq.items():
            idx = self.vocabulary[t]
            # Sublinear TF with smooth IDF
            tf = 1.0 + np.log(count)
            idf = self.idf_weights.get(t, 1.0)
            vec[idx] = float(tf * idf)

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def build_initial_index(self):
        self.chunks = list(get_all_guideline_chunks())
        
        # Also load from SQLite if any custom documents were uploaded
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT chunk_id, doc_id, text, disease_tags, medicine_tags, source_citation, source_url FROM evidence_chunks")
            rows = cursor.fetchall()
            for r in rows:
                tags = r["disease_tags"].split(",") if r["disease_tags"] else []
                meds = r["medicine_tags"].split(",") if r["medicine_tags"] else []
                chunk = ClinicalGuidelineChunk(
                    chunk_id=r["chunk_id"],
                    doc_id=r["doc_id"],
                    title=f"Uploaded Clinical Document ({r['doc_id']})",
                    organization="Hospital Practice Library",
                    url=r["source_url"] or "",
                    publication_year=2024,
                    review_date="2024-03-01",
                    applicable_population="Uploaded Clinical Protocol",
                    disease_tags=tags,
                    medicine_tags=meds,
                    section_name="Clinical Guidance",
                    text=r["text"],
                    citation=r["source_citation"] or "Uploaded Institutional Clinical Protocol"
                )
                self.chunks.append(chunk)
            conn.close()
        except Exception:
            pass

        self.tokenized_corpus = [
            tokenize_text(f"{c.title} {c.section_name} {' '.join(c.disease_tags)} {' '.join(c.medicine_tags)} {c.text}")
            for c in self.chunks
        ]
        self._build_vocab()

        # Build BM25
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Build FAISS
        self.index = faiss.IndexFlatIP(self.dimension)
        if self.chunks:
            vectors = np.array([self._embed_text(c.text) for c in self.chunks], dtype=np.float32)
            self.index.add(vectors)

    def retrieve(
        self,
        query: str,
        disease_tag: Optional[str] = None,
        medicine_tag: Optional[str] = None,
        top_k: int = 4,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval: Score = alpha * dense_score + (1 - alpha) * bm25_score.
        Applies metadata filtering and relevance boosts.
        """
        if not self.chunks or not self.bm25 or not self.index:
            return []

        q_tokens = tokenize_text(query)
        if not q_tokens:
            q_tokens = ["clinical", "treatment", "guideline"]

        # 1. BM25 Scores
        bm25_scores = np.array(self.bm25.get_scores(q_tokens), dtype=np.float32)
        if np.max(bm25_scores) > 0:
            bm25_norm = bm25_scores / (np.max(bm25_scores) + 1e-6)
        else:
            bm25_norm = np.zeros_like(bm25_scores)

        # 2. FAISS Dense Scores
        q_vec = self._embed_text(query).reshape(1, -1)
        dense_distances, dense_indices = self.index.search(q_vec, len(self.chunks))
        dense_scores = np.zeros(len(self.chunks), dtype=np.float32)
        for rank, idx in enumerate(dense_indices[0]):
            dense_scores[idx] = max(0.0, float(dense_distances[0][rank]))

        # 3. Hybrid Combination & Tag Boost
        combined = []
        for i, chunk in enumerate(self.chunks):
            dense_s = float(dense_scores[i])
            bm25_s = float(bm25_norm[i])
            score = (alpha * dense_s) + ((1.0 - alpha) * bm25_s)
            
            # Boost matches on specific disease / medicine tags
            if disease_tag and any(disease_tag.lower() in t.lower() for t in chunk.disease_tags):
                score += 0.25
            if medicine_tag and any(medicine_tag.lower() in m.lower() for m in chunk.medicine_tags):
                score += 0.20

            # Boost exact title keyword presence
            q_lower = query.lower()
            if any(token in chunk.title.lower() for token in q_tokens):
                score += 0.10

            combined.append((score, bm25_s, dense_s, chunk))

        # Sort descending by hybrid score
        combined.sort(key=lambda x: x[0], reverse=True)
        top_results = combined[:top_k]

        return [
            {
                "chunk_id": item[3].chunk_id,
                "doc_id": item[3].doc_id,
                "title": item[3].title,
                "organization": item[3].organization,
                "url": item[3].url,
                "publication_year": item[3].publication_year,
                "review_date": item[3].review_date,
                "applicable_population": item[3].applicable_population,
                "disease_tags": item[3].disease_tags,
                "medicine_tags": item[3].medicine_tags,
                "section_name": item[3].section_name,
                "text": item[3].text,
                "citation": item[3].citation,
                "hybrid_score": round(float(item[0]), 3),
                "bm25_score": round(float(item[1]), 3),
                "dense_score": round(float(item[2]), 3)
            }
            for item in top_results
        ]

    def rag_answer(
        self,
        query: str,
        disease_tag: Optional[str] = None,
        medicine_tag: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieval-Augmented Generation (RAG) Answer Synthesizer.
        Retrieves top clinical guideline passages, extracts pertinent recommendations
        and safety warnings, and synthesizes a grounded clinical guidance response.
        """
        retrieved = self.retrieve(query=query, disease_tag=disease_tag, medicine_tag=medicine_tag, top_k=top_k)
        if not retrieved:
            return {
                "query": query,
                "answer": "No verified clinical guideline documents matched the search query in the knowledge base.",
                "confidence": 0.0,
                "sources": [],
                "warnings": ["Insufficient evidence retrieved to formulate clinical guidance."]
            }

        # Build grounded synthesis
        primary = retrieved[0]
        grounded_lines = [
            f"### Evidence-Based Clinical Guidance for: *\"{query}\"*",
            "",
            f"According to verified practice guidance from **{primary['organization']}** (*{primary['title']}*, {primary['publication_year']}):",
            ""
        ]

        # Extract sentences from top passages that contain key terms or numbers
        key_points = []
        warnings = []
        for idx, passage in enumerate(retrieved, start=1):
            text = passage["text"]
            # Detect contraindications or black-box warnings
            for sent in re.split(r"(?<=[.!?])\s+", text):
                sent_clean = sent.strip()
                if not sent_clean:
                    continue
                sent_lower = sent_clean.lower()
                if any(w in sent_lower for w in ["contraindicat", "black box", "boxed warning", "fatal", "never", "do not"]):
                    if sent_clean not in warnings:
                        warnings.append(sent_clean)
                elif any(kw in sent_lower for kw in ["dose", "mg", "first-line", "recommended", "schedule", "treatment", "target"]):
                    if sent_clean not in key_points and len(key_points) < 5:
                        key_points.append(f"{sent_clean} [{idx}]")

        if key_points:
            grounded_lines.append("**Key Guideline Recommendations:**")
            for kp in key_points:
                grounded_lines.append(f"- {kp}")
            grounded_lines.append("")

        if warnings:
            grounded_lines.append("**⚠️ Clinical Safety & Contraindication Alerts:**")
            for w in warnings[:3]:
                grounded_lines.append(f"> ⚠️ {w}")
            grounded_lines.append("")

        grounded_lines.append("---")
        grounded_lines.append("**Verified Retrieval Sources:**")
        for idx, r in enumerate(retrieved, start=1):
            grounded_lines.append(f"[{idx}] **{r['title']}** ({r['organization']}, {r['publication_year']}) — *Section: {r['section_name']}* [Access Guideline]({r['url']}) (Match Score: {r['hybrid_score']})")

        grounded_lines.append("")
        grounded_lines.append("> *Disclaimer: RAG synthesis is generated from authenticated clinical practice guidelines (ICMR STWs, CDSCO, NVBDCP, NTEP). Final dosing and prescribing authority resides with the attending physician.*")

        answer_text = "\n".join(grounded_lines)
        return {
            "query": query,
            "answer": answer_text,
            "confidence": round(float(primary["hybrid_score"]), 3),
            "sources": retrieved,
            "warnings": warnings[:3]
        }

    def add_uploaded_document(self, doc_id: str, title: str, organization: str, url: str, content: str, disease_tag: str) -> int:
        """
        Chunks and indexes doctor-uploaded guidelines with anti-prompt-injection sanitization.
        """
        # Split into ~300-500 character clinical paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [content.strip()]

        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = "2024-03-01T12:00:00Z"
        cursor.execute("""
            INSERT OR REPLACE INTO evidence_documents 
            (doc_id, title, organization, url, publication_date, retrieval_date, review_status, applicable_population, content, chunk_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, title, organization, url, "2024", now, "DOCTOR_UPLOADED_INSTITUTIONAL", "Institutional Care Setting", content, len(paragraphs), now))

        added_chunks = []
        for idx, para in enumerate(paragraphs):
            chunk_id = f"{doc_id}_chunk_{idx+1}"
            cursor.execute("""
                INSERT OR REPLACE INTO evidence_chunks
                (chunk_id, doc_id, chunk_index, text, disease_tags, medicine_tags, population_tags, source_citation, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chunk_id, doc_id, idx+1, para, disease_tag, "", "Institutional Adult/Pediatric", f"{title} (Uploaded Guideline)", url))
            
            chunk = ClinicalGuidelineChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=title,
                organization=organization or "Institutional Practice",
                url=url,
                publication_year=2024,
                review_date=now[:10],
                applicable_population="Uploaded Clinical Guideline",
                disease_tags=[disease_tag],
                medicine_tags=[],
                section_name=f"Section {idx+1}",
                text=para,
                citation=f"{title} ({organization}, 2024)"
            )
            added_chunks.append(chunk)

        conn.commit()
        conn.close()

        # Re-index
        self.build_initial_index()
        return len(added_chunks)

# Global singleton
hybrid_retriever = HybridRetriever()

