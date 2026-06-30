from __future__ import annotations

import json
import re
from typing import Any

from backend.llm.llama_cpp_engine import LlamaCppEngine
from backend.llm.prompt_templates import scheme_extraction_prompt
from backend.schemas.scheme import Scheme
from backend.structuring.schema_validator import validate_scheme
from backend.structuring.scheme_parser import extract_scheme_fields


def extract_structured_scheme(text: str) -> Scheme:
    engine = LlamaCppEngine()
    if engine.available():
        payload = _extract_json(engine.generate(scheme_extraction_prompt(text)))
        if payload:
            return validate_scheme(_scheme_from_payload(payload, extract_scheme_fields(text)))
    return validate_scheme(extract_scheme_fields(text))


def _extract_json(output: str) -> dict[str, Any]:
    if not output:
        return {}
    match = re.search(r"\{.*\}", output, flags=re.S)
    if not match:
        return {}
    try:
        loaded = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _scheme_from_payload(payload: dict[str, Any], fallback: Scheme) -> Scheme:
    required_documents = payload.get("required_documents", payload.get("documents", []))
    return Scheme(
        scheme_name=_text(payload.get("scheme_name")) or fallback.scheme_name,
        department=fallback.department,
        state=fallback.state,
        category=_text(payload.get("category")) or fallback.category,
        objective=_text(payload.get("objective")) or fallback.objective,
        benefits=_items(payload.get("benefits")) or fallback.benefits,
        eligibility=_items(payload.get("eligibility")) or fallback.eligibility,
        documents=_items(required_documents) or fallback.documents,
        important_dates=fallback.important_dates,
        application_process=_items(payload.get("application_process")) or fallback.application_process,
        faq=_items(payload.get("faq")) or fallback.faq,
        contact=fallback.contact,
        summary=fallback.summary,
        confidence=max(fallback.confidence, 0.75),
        raw={"extraction_mode": "local_slm", "slm_payload": payload},
    )


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _items(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []
