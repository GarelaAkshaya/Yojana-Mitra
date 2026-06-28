from __future__ import annotations

import json

from backend.embeddings.bge_encoder import LocalEncoder
from backend.retrieval.faiss_index import VectorIndex
from backend.schemas.scheme import RetrievedChunk
from backend.storage.repository import Repository


def rebuild_vector_index(repo: Repository | None = None, encoder: LocalEncoder | None = None) -> int:
    repo = repo or Repository()
    encoder = encoder or LocalEncoder()
    chunks = repo.get_chunks()
    vectors = encoder.encode([chunk.text for chunk in chunks]) if chunks else []
    VectorIndex().save_vectors({int(chunk.id): vector for chunk, vector in zip(chunks, vectors, strict=True) if chunk.id})
    for chunk, vector in zip(chunks, vectors, strict=True):
        if chunk.id:
            repo.save_embedding(chunk.id, vector, encoder.model_name)
    return len(chunks)


def hybrid_search(query: str, document_id: int | None = None, top_k: int = 5, repo: Repository | None = None) -> list[RetrievedChunk]:
    repo = repo or Repository()
    keyword_results = repo.search_fts(query, limit=top_k * 2, document_id=document_id)
    all_chunks = {chunk.id: chunk for chunk in repo.get_chunks(document_id=document_id) if chunk.id is not None}

    query_vector = LocalEncoder().encode([query])[0]
    vector_hits = VectorIndex().search(query_vector, top_k=top_k * 2)

    fused: dict[int, float] = {}
    for rank, chunk in enumerate(keyword_results):
        if chunk.id is not None:
            fused[chunk.id] = fused.get(chunk.id, 0.0) + 1.0 / (rank + 1)
    for rank, (chunk_id, score) in enumerate(vector_hits):
        if chunk_id in all_chunks:
            fused[chunk_id] = fused.get(chunk_id, 0.0) + max(score, 0.0) + 0.25 / (rank + 1)

    if not fused:
        query_terms = {_term_key(term) for term in query.split() if len(_term_key(term)) > 2}
        for chunk_id, chunk in all_chunks.items():
            text_terms = {_term_key(term) for term in chunk.text.split()}
            overlap = len(query_terms & text_terms)
            if overlap:
                fused[chunk_id] = min(0.2 + overlap / max(len(query_terms), 1), 1.0)

    results: list[RetrievedChunk] = []
    for chunk_id, score in sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]:
        chunk = all_chunks.get(chunk_id)
        if chunk:
            chunk.score = min(float(score), 1.0)
            results.append(chunk)
    return results


def _term_key(term: str) -> str:
    cleaned = term.strip(".,?!:;()[]{}").lower()
    if cleaned.startswith("eligib") or cleaned.startswith("eligible"):
        return "elig"
    for suffix in ("ibility", "able", "ible", "ity", "ed", "ing", "s"):
        if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 3:
            return cleaned[: -len(suffix)]
    return cleaned
