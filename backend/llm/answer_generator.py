from __future__ import annotations

import re

from backend.llm.guardrails import guard_answer
from backend.llm.llama_cpp_engine import LlamaCppEngine
from backend.llm.prompt_templates import qa_prompt
from backend.localization.text_sanitizer import sanitize_text
from backend.retrieval.hybrid_search import detect_section_intent
from backend.schemas.scheme import GroundedAnswer, RetrievedChunk


def generate_answer(
    question: str,
    chunks: list[RetrievedChunk],
    confidence: float,
    language: str = "en",
) -> GroundedAnswer:
    engine = LlamaCppEngine()
    question = sanitize_text(question)
    chunks = [_clean_chunk(chunk) for chunk in chunks]
    intent = detect_section_intent(question)

    # No retrieved context
    if not chunks:
        return guard_answer(
            "Not enough information in the uploaded document.",
            confidence,
            [],
            ["No relevant document chunks were retrieved."],
            language=language,
        )

    answer = (
        engine.generate(
            qa_prompt(
                question,
                chunks,
                language=language,
                intent=intent,
            )
        )
        if engine.available()
        else ""
    )

    if not answer:
        answer = _fallback_answer(question, chunks)

    reasoning = _reasoning(question, answer, chunks)
    return guard_answer(answer, confidence, chunks, reasoning, language=language)


def _fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    intent = detect_section_intent(question)
    if intent:
        section_lines = _section_lines(chunks, intent)
        if section_lines:
            return "\n".join(f"- {line}" for line in section_lines[:8])

    question_terms = {
        _term_key(term)
        for term in re.findall(r"[\w\u0900-\u097F\u0C00-\u0C7F]+", question.lower())
        if len(_term_key(term)) > 2
    }
    best_sentence = ""
    best_score = 0
    for chunk in chunks:
        for sentence in re.split(r"(?<=[.!?।॥])\s+|\n+", chunk.text):
            sentence = sentence.strip(" -•\t")
            if len(sentence) < 4:
                continue
            sentence_terms = {
                _term_key(term) for term in re.findall(r"[\w\u0900-\u097F\u0C00-\u0C7F]+", sentence.lower())
            }
            score = len(question_terms & sentence_terms)
            if score > best_score:
                best_sentence = sentence
                best_score = score
    return sanitize_text(best_sentence or chunks[0].text[:500].strip())


def _section_lines(chunks: list[RetrievedChunk], intent: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        if intent and _normalize_section(chunk.section_title) != _normalize_section(intent):
            continue
        for line in chunk.text.splitlines():
            cleaned = sanitize_text(re.sub(r"^\s*(?:[-*•]|\d+[\).])\s*", "", line).strip(" :-\t"))
            if not cleaned or _normalize_section(cleaned) == _normalize_section(intent):
                continue
            key = re.sub(r"\s+", " ", cleaned.lower())
            if key not in seen:
                seen.add(key)
                lines.append(cleaned)
    return lines


def _term_key(term: str) -> str:
    cleaned = re.sub(r"[^\w\u0900-\u097F\u0C00-\u0C7F]", "", term.lower())
    for suffix in ("ibility", "able", "ible", "ity", "ed", "ing", "s"):
        if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 3:
            return cleaned[: -len(suffix)]
    return cleaned


def _normalize_section(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _reasoning(question: str, answer: str, chunks: list[RetrievedChunk]) -> list[str]:
    if not chunks:
        return ["No document context was available."]
    section = detect_section_intent(question)
    if section:
        return [f"Used retrieved context from the {section} section."]
    return ["Used the most relevant retrieved document chunk."]


def _clean_chunk(chunk: RetrievedChunk) -> RetrievedChunk:
    data = chunk.model_dump()
    data["text"] = sanitize_text(data.get("text", ""))
    return RetrievedChunk(**data)
