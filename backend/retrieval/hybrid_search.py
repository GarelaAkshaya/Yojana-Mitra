from __future__ import annotations

import re

from backend.embeddings.bge_encoder import LocalEncoder
from backend.retrieval.faiss_index import VectorIndex
from backend.schemas.scheme import RetrievedChunk
from backend.storage.repository import Repository

SECTION_QUERY_ALIASES: dict[str, tuple[str, ...]] = {
    "Eligibility": (
        "eligib",
        "eligible",
        "who can apply",
        "beneficiar",
        "income",
        "age",
        "पात्र",
        "योग्यता",
        "अर्ह",
        "అర్హ",
        "అర్హత",
    ),
    "Benefits": (
        "benefit",
        "amount",
        "assistance",
        "subsidy",
        "support",
        "लाभ",
        "लाब",
        "सहायता",
        "ప్రయోజ",
        "లాభ",
        "సహాయం",
    ),
    "Required Documents": (
        "document",
        "certificate",
        "proof",
        "papers",
        "दस्तावेज",
        "प्रमाण",
        "పత్ర",
        "సర్టిఫికెట్",
    ),
    "Application Process": (
        "apply",
        "application",
        "procedure",
        "registration",
        "submit",
        "आवेदन",
        "कैसे",
        "దరఖాస్తు",
        "ఎలా",
    ),
    "Objective": ("objective", "purpose", "aim", "उद्देश्य", "లక్ష్యం", "ఉద్దేశ"),
    "Important Dates": (
        "last date",
        "deadline",
        "important date",
        "अंतिम",
        "तारीख",
        "చివరి",
        "తేదీ",
    ),
    "FAQs": ("faq", "frequently asked", "question", "सवाल", "प्रश्न", "ప్రశ్న"),
    "Contact Information": (
        "contact",
        "helpline",
        "phone",
        "email",
        "website",
        "संपर्क",
        "हेल्पलाइन",
        "సంప్రద",
        "హెల్ప్",
    ),
}


def rebuild_vector_index(repo: Repository | None = None, encoder: LocalEncoder | None = None) -> int:
    repo = repo or Repository()
    encoder = encoder or LocalEncoder()
    chunks = repo.get_chunks()
    vectors = encoder.encode([chunk.text for chunk in chunks]) if chunks else []
    VectorIndex().save_vectors(
        {int(chunk.id): vector for chunk, vector in zip(chunks, vectors, strict=True) if chunk.id}
    )
    for chunk, vector in zip(chunks, vectors, strict=True):
        if chunk.id:
            repo.save_embedding(chunk.id, vector, encoder.model_name)
    return len(chunks)


def hybrid_search(
    query: str,
    document_id: int | None = None,
    top_k: int = 5,
    repo: Repository | None = None,
) -> list[RetrievedChunk]:
    repo = repo or Repository()
    target_section = detect_section_intent(query)
    keyword_results = repo.search_fts(query, limit=top_k * 2, document_id=document_id)
    all_chunks = {chunk.id: chunk for chunk in repo.get_chunks(document_id=document_id) if chunk.id is not None}

    query_vector = LocalEncoder().encode([query])[0]
    vector_hits = VectorIndex().search(query_vector, top_k=top_k * 2)

    fused: dict[int, float] = {}
    for rank, chunk in enumerate(keyword_results):
        if chunk.id is not None:
            fused[chunk.id] = fused.get(chunk.id, 0.0) + _section_weight(chunk, target_section) * (1.0 / (rank + 1))
    for rank, (chunk_id, score) in enumerate(vector_hits):
        if chunk_id in all_chunks:
            vector_chunk = all_chunks[chunk_id]
            fused[chunk_id] = fused.get(chunk_id, 0.0) + _section_weight(vector_chunk, target_section) * (
                max(score, 0.0) + 0.25 / (rank + 1)
            )

    if not fused:
        query_terms = {_term_key(term) for term in query.split() if len(_term_key(term)) > 2}
        for chunk_id, chunk in all_chunks.items():
            text_terms = {_term_key(term) for term in chunk.text.split()}
            overlap = len(query_terms & text_terms)
            if overlap:
                fused[chunk_id] = min(
                    _section_weight(chunk, target_section) * (0.2 + overlap / max(len(query_terms), 1)),
                    1.0,
                )

    results: list[RetrievedChunk] = []
    ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)
    if target_section:
        matching = [
            (chunk_id, score)
            for chunk_id, score in ranked
            if _same_section(all_chunks[chunk_id].section_title, target_section)
        ]
        ranked = matching or ranked
    for chunk_id, score in ranked[:top_k]:
        result_chunk = all_chunks.get(chunk_id)

        if result_chunk is not None:
            result_chunk.score = min(float(score), 1.0)
            results.append(result_chunk)

    return results


def _term_key(term: str) -> str:
    cleaned = re.sub(r"[^\w]", "", term.lower())
    if cleaned.startswith("eligib") or cleaned.startswith("eligible"):
        return "elig"
    for suffix in ("ibility", "able", "ible", "ity", "ed", "ing", "s"):
        if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 3:
            return cleaned[: -len(suffix)]
    return cleaned


def detect_section_intent(query: str) -> str:
    lowered = query.lower()
    for section, aliases in SECTION_QUERY_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return section
    return ""


def _section_weight(chunk: RetrievedChunk, target_section: str) -> float:
    section = chunk.section_title or ""
    if not target_section:
        return 0.35 if _same_section(section, "FAQs") else 1.0
    if _same_section(section, target_section):
        return 2.5
    if _same_section(section, "FAQs") and not _same_section(target_section, "FAQs"):
        return 0.05
    return 0.35 if section else 1.0


def _same_section(left: str, right: str) -> bool:
    return _normalize_section(left) == _normalize_section(right)


def _normalize_section(section: str) -> str:
    return re.sub(r"[^\w\u0900-\u097F\u0C00-\u0C7F]+", "", section.lower())
