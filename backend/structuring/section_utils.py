from __future__ import annotations

import re

from backend.schemas.scheme import RetrievedChunk

PLACEHOLDERS = {
    "",
    "not specified in document",
    "not specified",
    "दस्तावेज़ में निर्दिष्ट नहीं",
    "పత్రంలో పేర్కొనలేదు",
}

SECTION_TO_DETAIL_KEY = {
    "Benefits": "benefits",
    "Eligibility": "eligibility",
    "Required Documents": "documents",
    "Application Process": "application_process",
    "FAQs": "faq",
}

SECTION_EQUIVALENTS = {
    "Benefits": (
        "benefit",
        "benefits",
        "assistance",
        "financial assistance",
        "subsidy",
        "लाभ",
        "लाब",
        "सहायता",
        "ప్రయోజనాలు",
        "లాభాలు",
        "సహాయం",
    ),
    "Eligibility": (
        "eligibility",
        "eligible",
        "who can apply",
        "beneficiaries",
        "पात्रता",
        "योग्यता",
        "అర్హత",
        "అర్హులు",
    ),
    "Required Documents": (
        "required documents",
        "documents",
        "documents required",
        "document required",
        "आवश्यक दस्तावेज",
        "दस्तावेज",
        "అవసరమైన పత్రాలు",
        "పత్రాలు",
    ),
    "Application Process": (
        "application process",
        "application",
        "how to apply",
        "procedure",
        "आवेदन प्रक्रिया",
        "कैसे आवेदन",
        "దరఖాస్తు ప్రక్రియ",
        "ఎలా దరఖాస్తు",
    ),
    "Objective": ("objective", "purpose", "उद्देश्य", "లక్ష్యం", "ఉద్దేశ్యం"),
    "FAQs": (
        "faq",
        "faqs",
        "frequently asked questions",
        "प्रश्न",
        "సवाल",
        "ప్రశ్నలు",
        "తరచుగా అడిగే ప్రశ్నలు",
    ),
}

NEXT_SECTION_RE = re.compile(
    (
        r"^\s*("
        r"objective|benefits?|eligibility|eligible|required documents|"
        r"documents|application process|how to apply|faqs?|"
        r"frequently asked questions|contact|helpline|important dates?|"
        r"last date|उद्देश्य|लाभ|लाब|पात्रता|योग्यता|"
        r"आवश्यक दस्तावेज|दस्तावेज|आवेदन प्रक्रिया|संपर्क|"
        r"లక్ష్యం|ఉద్దేశ్యం|ప్రయోజనాలు|లాభాలు|అర్హత|"
        r"అవసరమైన పత్రాలు|పత్రాలు|దరఖాస్తు ప్రక్రియ|సంప్రదింపు"
        r")\s*:?\s*$"
    ),
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
        if same_section(chunk.section_title, section_title):
            candidates = _items_from_section_text(chunk.text, section_title)
        elif not chunk.section_title:
            candidates = _items_from_section_text(chunk.text, section_title, allow_fallback=False)
        else:
            continue
        for item in candidates:
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


def _items_from_section_text(text: str, section_title: str, allow_fallback: bool = True) -> list[str]:
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
    if allow_fallback and not items and lines:
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
    return re.sub(r"[^\w\u0900-\u097F\u0C00-\u0C7F]+", "", value.lower())


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
