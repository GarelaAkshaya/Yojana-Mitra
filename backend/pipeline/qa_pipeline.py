from __future__ import annotations

from backend.llm.answer_generator import generate_answer
from backend.core.pydantic_compat import BaseModel
from backend.schemas.scheme import GroundedAnswer
from backend.storage.repository import Repository
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
