from __future__ import annotations

import re

from backend.llm.guardrails import guard_answer
from backend.llm.llama_cpp_engine import LlamaCppEngine
from backend.llm.prompt_templates import qa_prompt
from backend.schemas.scheme import GroundedAnswer, RetrievedChunk


def generate_answer(question: str, chunks: list[RetrievedChunk], confidence: float) -> GroundedAnswer:
    engine = LlamaCppEngine()
    answer = engine.generate(qa_prompt(question, chunks)) if engine.available() else ""
    if not answer:
        answer = _fallback_answer(question, chunks)
    reasoning = _reasoning(question, answer, chunks)
    return guard_answer(answer, confidence, chunks, reasoning)


def _fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    lowered = question.lower()
    joined = "\n".join(chunk.text for chunk in chunks)
    if any(token in lowered for token in ["document", "documents", "certificate"]):
        return _lines_after_keywords(joined, ["documents", "required documents"])
    if any(token in lowered for token in ["benefit", "amount", "assistance"]):
        return _lines_after_keywords(joined, ["benefits", "assistance", "subsidy"])
    if any(token in lowered for token in ["eligible", "eligibility", "who can apply", "income", "age"]):
        return _lines_after_keywords(joined, ["eligibility", "eligible", "beneficiaries"])
    if any(token in lowered for token in ["last date", "deadline", "date"]):
        date = re.search(r"\b\d{1,2}[-/ ](?:\d{1,2}|[A-Za-z]{3,9})[-/ ]\d{2,4}\b", joined)
        return date.group(0) if date else _lines_after_keywords(joined, ["last date", "important dates"])
    return chunks[0].text[:450].strip()


def _lines_after_keywords(text: str, keywords: list[str]) -> str:
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    selected: list[str] = []
    capture = False
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in keywords):
            capture = True
            remainder = re.sub(r"^[^:]{2,40}[:\-]\s*", "", line)
            if remainder and remainder != line:
                selected.append(remainder.strip())
            continue
        if capture:
            if re.match(r"^[A-Z][A-Za-z ]{2,35}:?$", line) and selected:
                break
            selected.append(line)
        if len(selected) >= 6:
            break
    return "\n".join(selected).strip() or text[:450].strip()


def _reasoning(question: str, answer: str, chunks: list[RetrievedChunk]) -> list[str]:
    if not chunks:
        return []
    if any(token in question.lower() for token in ["eligible", "income", "age", "can i apply"]):
        return ["Matched the question against retrieved eligibility context.", "Answer is grounded in the cited document chunks."]
    return ["Answer generated from the highest scoring retrieved chunks."]
