from __future__ import annotations

from backend.llm.answer_generator import generate_answer
from backend.core.pydantic_compat import BaseModel
from backend.localization.translator import localize_items, translate
from backend.retrieval.hybrid_search import detect_section_intent
from backend.schemas.scheme import GroundedAnswer, RetrievedChunk
from backend.storage.repository import Repository
from backend.structuring.section_utils import SECTION_TO_DETAIL_KEY, useful_items
from backend.retrieval.retriever import retrieve_context


class QAResult(BaseModel):
    answer: str
    confidence: float
    citations: list[dict]
    reasoning: list[str]
    refused: bool = False


def run_qa_pipeline(question: str, document_id: int | None = None, language: str = "en", repo: Repository | None = None) -> QAResult:
    repo = repo or Repository()
    cached = repo.get_cached_response(document_id, question, language)
    if cached:
        return QAResult.model_validate(cached)

    structured = _structured_section_answer(question, document_id, repo, language)
    if structured:
        repo.set_cached_response(document_id, question, structured.model_dump(), language)
        return structured

    chunks, confidence = retrieve_context(question, document_id=document_id, repo=repo)
    grounded: GroundedAnswer = generate_answer(question, chunks, confidence, language=language)
    repo.log_query(document_id, question, grounded, language)
    result = QAResult(
        answer=grounded.answer,
        confidence=grounded.confidence,
        citations=[chunk.model_dump() for chunk in grounded.citations],
        reasoning=grounded.reasoning,
        refused=grounded.refused,
    )
    repo.set_cached_response(document_id, question, result.model_dump(), language)
    return result


def _structured_section_answer(question: str, document_id: int | None, repo: Repository, language: str = "en") -> QAResult | None:
    if document_id is None:
        return None
    intent = detect_section_intent(question)
    key = SECTION_TO_DETAIL_KEY.get(intent)
    if not key:
        return None
    details = repo.get_scheme_details(document_id)
    if not details:
        return None
    items = localize_items(useful_items(details.get(key, [])), language)
    if not items:
        return None
    chunks = [
        chunk
        for chunk in repo.get_chunks(document_id)
        if _same_section(chunk.section_title, intent)
    ]
    citations = [_citation(chunk) for chunk in chunks[:3]]
    answer = "\n".join(f"- {item}" for item in items[:10])
    return QAResult(
        answer=answer,
        confidence=1.0,
        citations=citations,
        reasoning=[translate("structured_data", language)],
        refused=False,
    )


def _citation(chunk: RetrievedChunk) -> dict:
    return chunk.model_dump()


def _same_section(left: str, right: str) -> bool:
    return "".join(ch for ch in left.lower() if ch.isalnum()) == "".join(ch for ch in right.lower() if ch.isalnum())
