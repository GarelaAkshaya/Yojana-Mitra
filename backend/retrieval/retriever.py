from __future__ import annotations

from backend.core.config import get_settings
from backend.retrieval.hybrid_search import hybrid_search
from backend.schemas.scheme import RetrievedChunk
from backend.storage.repository import Repository


def retrieve_context(
    question: str,
    document_id: int | None = None,
    top_k: int | None = None,
    repo: Repository | None = None,
) -> tuple[list[RetrievedChunk], float]:
    settings = get_settings()
    chunks = hybrid_search(question, document_id=document_id, top_k=top_k or settings.retrieval.top_k, repo=repo)
    confidence = max((chunk.score for chunk in chunks), default=0.0)
    return chunks, confidence
