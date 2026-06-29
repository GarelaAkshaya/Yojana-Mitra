from __future__ import annotations

import re

from backend.schemas.scheme import RetrievedChunk


PLACEHOLDERS = {"", "not specified in document", "not specified"}

SECTION_TO_DETAIL_KEY = {
    "Benefits": "benefits",
    "Eligibility": "eligibility",
    "Required Documents": "documents",
    "Application Process": "application_process",
    "FAQs": "faq",
}

SECTION_EQUIVALENTS = {
    "Benefits": ("benefit", "benefits", "assistance", "financial assistance", "subsidy"),
    "Eligibility": ("eligibility", "eligible", "who can apply", "beneficiaries"),
    "Required Documents": ("required documents", "documents", "documents required", "document required"),
    "Application Process": ("application process", "application", "how to apply", "procedure"),
    "Objective": ("objective", "purpose"),
    "FAQs": ("faq", "faqs", "frequently asked questions"),
}

NEXT_SECTION_RE = re.compile(
    r"^\s*(objective|benefits?|eligibility|eligible|required documents|documents|application process|how to apply|faqs?|frequently asked questions|contact|helpline|important dates?|last date)\s*:?\s*$",
    re.I,
)


def useful_items(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    cleaned: list[str] = []
    for item in items:
        text = str(item).strip(" \t\r\n-•")
        if text.lower() not in PLACEHOLDERS:
            cleaned.append(text)
    return cleaned


def is_useful_text(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS


def items_from_chunks(chunks: list[RetrievedChunk], section_title: str, limit: int = 12) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        if not same_section(chunk.section_title, section_title):
            continue
        for item in _items_from_section_text(chunk.text, section_title):
            key = re.sub(r"\s+", " ", item.lower())
            if key not in seen:
                seen.add(key)
                items.append(item)
            if len(items) >= limit:
                return items
    return items


def section_text_from_chunks(chunks: list[RetrievedChunk], section_title: str, limit: int = 8) -> str:
    items = items_from_chunks(chunks, section_title, limit=limit)
    return "\n".join(f"- {item}" for item in items)


def _items_from_section_text(text: str, section_title: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items: list[str] = []
    capture = False
    for line in lines:
        lowered = line.lower().strip(":-")
        if same_section(lowered, section_title):
            capture = True
            continue
        if capture and NEXT_SECTION_RE.match(line):
            break
        if not capture and same_section(line.split(":", 1)[0], section_title):
            capture = True
            remainder = line.split(":", 1)[1].strip() if ":" in line else ""
            if remainder:
                items.append(_clean_item(remainder))
            continue
        if capture:
            cleaned = _clean_item(line)
            if cleaned:
                items.append(cleaned)
    if not items and lines:
        for line in lines:
            if NEXT_SECTION_RE.match(line):
                continue
            cleaned = _clean_item(line)
            if cleaned:
                items.append(cleaned)
    return [item for item in items if item.lower() not in PLACEHOLDERS]


def _clean_item(line: str) -> str:
    cleaned = re.sub(r"^\s*(?:[-*•]|\d+[\).])\s*", "", line).strip(" :-\t")
    return cleaned if len(cleaned) >= 3 else ""


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def same_section(left: str, right: str) -> bool:
    left_key = _canonical(left)
    right_key = _canonical(right)
    return left_key == right_key


def _canonical(value: str) -> str:
    normalized = _normalize(value)
    for section, aliases in SECTION_EQUIVALENTS.items():
        options = (_normalize(section), *(_normalize(alias) for alias in aliases))
        if normalized in options:
            return _normalize(section)
    return normalized
