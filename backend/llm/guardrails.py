from __future__ import annotations

from backend.core.config import get_settings
from backend.localization.translator import translate
from backend.schemas.scheme import GroundedAnswer, RetrievedChunk

REFUSAL = "Not enough information in the uploaded document."


def guard_answer(
    answer: str,
    confidence: float,
    chunks: list[RetrievedChunk],
    reasoning: list[str] | None = None,
    language: str = "en",
) -> GroundedAnswer:
    threshold = get_settings().retrieval.min_confidence
    if confidence < threshold or not chunks:
        return GroundedAnswer(
            answer=translate("not_found", language),
            confidence=confidence,
            citations=[],
            reasoning=[],
            refused=True,
        )
    clean = answer.strip() or _extractive_answer("", chunks)
    if clean.lower().startswith("not enough information"):
        return GroundedAnswer(
            answer=translate("not_found", language),
            confidence=confidence,
            citations=chunks,
            reasoning=reasoning or [],
            refused=True,
        )
    if clean.lower().startswith("this question is outside"):
        return GroundedAnswer(
            answer=translate("outside_scope", language),
            confidence=confidence,
            citations=chunks,
            reasoning=reasoning or [],
            refused=True,
        )
    return GroundedAnswer(
        answer=clean,
        confidence=confidence,
        citations=chunks,
        reasoning=reasoning or [],
        refused=False,
    )


def _extractive_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    return chunks[0].text[:500].strip() if chunks else REFUSAL
