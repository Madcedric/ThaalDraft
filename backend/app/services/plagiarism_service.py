import os
import time
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded SentenceTransformer model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"SentenceTransformer not available: {e}")
            _embedding_model = False
    return _embedding_model if _embedding_model is not False else None


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks if chunks else [text[:2000]]


def compute_similarity(text_a: str, text_b: str) -> float:
    model = _get_embedding_model()
    if model:
        try:
            from sentence_transformers import util
            chunks_a = _chunk_text(text_a)
            chunks_b = _chunk_text(text_b)
            emb_a = model.encode(chunks_a, convert_to_tensor=True)
            emb_b = model.encode(chunks_b, convert_to_tensor=True)
            cosine_scores = util.cos_sim(emb_a, emb_b)
            max_score = cosine_scores.max().item()
            return max(0.0, min(1.0, max_score))
        except Exception as e:
            logger.warning(f"Embedding similarity failed, falling back to Jaccard: {e}")

    return _jaccard_similarity(text_a, text_b)


def _jaccard_similarity(text_a: str, text_b: str) -> float:
    k = 5
    def _shingles(text: str) -> set:
        s = set()
        t = " ".join(text.split())
        for i in range(max(0, len(t) - k + 1)):
            s.add(t[i:i+k])
        return s
    sa = _shingles(text_a)
    sb = _shingles(text_b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def check_against_corpus(target_text: str, corpus: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    results = []
    model = _get_embedding_model()

    if model and len(corpus) > 0:
        try:
            from sentence_transformers import util
            target_chunks = _chunk_text(target_text)
            target_emb = model.encode(target_chunks, convert_to_tensor=True)

            for item in corpus:
                other_id = item.get("id")
                other_text = item.get("text", "")
                other_chunks = _chunk_text(other_text)
                other_emb = model.encode(other_chunks, convert_to_tensor=True)
                cosine_scores = util.cos_sim(target_emb, other_emb)
                max_score = cosine_scores.max().item()
                results.append({
                    "document_id": other_id,
                    "score": max(0.0, min(1.0, max_score)),
                    "method": "sentence_transformers",
                })
        except Exception as e:
            logger.warning(f"Embedding similarity failed for corpus: {e}")
            for item in corpus:
                other_id = item.get("id")
                other_text = item.get("text", "")
                score = _jaccard_similarity(target_text, other_text)
                results.append({"document_id": other_id, "score": score, "method": "jaccard"})
    else:
        for item in corpus:
            other_id = item.get("id")
            other_text = item.get("text", "")
            score = _jaccard_similarity(target_text, other_text)
            results.append({"document_id": other_id, "score": score, "method": "jaccard"})

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:top_n]


def create_plagiarism_record(document_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.info("Supabase not configured - plagiarism record not persisted.")
        return {
            "id": f"local-{document_id}",
            "document_id": document_id,
            "report": report,
            "similarity_score": max((r.get("score", 0) for r in report.get("matches", [])), default=0),
        }

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/plagiarism_checks"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    payload = {
        "document_id": document_id,
        "report": report,
        "similarity_score": max((r.get("score", 0) for r in report.get("matches", [])), default=0),
    }
    try:
        res = requests.post(url, json=[payload], headers=headers, timeout=15)
        if res.status_code in (200, 201):
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        logger.warning(f"create_plagiarism_record failed: {res.status_code}")
        return payload
    except Exception as e:
        logger.error(f"create_plagiarism_record exception: {e}")
        return payload


def get_plagiarism_reports_for_document(document_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/plagiarism_checks?document_id=eq.{document_id}&select=*&limit={limit}&order=created_at.desc"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception:
        return []
