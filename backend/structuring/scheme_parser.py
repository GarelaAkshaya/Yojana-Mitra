from __future__ import annotations

import re

from backend.schemas.scheme import ContactInfo, Scheme
from backend.structuring.normalizer import normalize_text, split_list_block


SECTION_ALIASES = {
    "eligibility": ["eligibility", "eligible", "who can apply", "beneficiaries"],
    "benefits": ["benefits", "assistance", "financial assistance", "subsidy"],
    "documents": ["documents", "required documents", "documents required"],
    "application_process": ["application process", "how to apply", "procedure"],
    "important_dates": ["important dates", "last date", "deadline"],
    "objective": ["objective", "purpose"],
    "faq": ["faq", "faqs", "frequently asked questions"],
    "contact": ["contact", "helpline"],
}


def extract_scheme_fields(text: str) -> Scheme:
    normalized = normalize_text(text)
    sections = _sections(normalized)
    scheme_name = _first_match(normalized, [r"scheme name\s*[:\-]\s*(.+)", r"^(.{5,90}Yojana.{0,80})$"])
    department = _first_match(normalized, [r"department\s*[:\-]\s*(.+)", r"ministry\s*[:\-]\s*(.+)"])
    state = _first_match(normalized, [r"state\s*[:\-]\s*(.+)", r"government of\s+([A-Za-z ]+)"])
    contact = ContactInfo(
        phone=_first_match(normalized, [r"(\+?\d[\d\-\s]{7,}\d)"], default=""),
        email=_first_match(normalized, [r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"], default=""),
        website=_first_match(normalized, [r"(https?://\S+|www\.\S+)"], default=""),
    )
    summary = _summary(normalized)
    confidence = 0.35 + 0.1 * sum(
        bool(value)
        for value in [
            sections.get("eligibility"),
            sections.get("benefits"),
            sections.get("documents"),
            scheme_name,
            department,
        ]
    )
    return Scheme(
        scheme_name=scheme_name or _title_from_text(normalized),
        department=department or "Not specified in document",
        state=state or "Not specified in document",
        category=_infer_category(normalized),
        objective=_single_section(sections, "objective"),
        eligibility=split_list_block(_single_section(sections, "eligibility")),
        benefits=split_list_block(_single_section(sections, "benefits")),
        documents=split_list_block(_single_section(sections, "documents")),
        important_dates=split_list_block(_single_section(sections, "important_dates")),
        application_process=split_list_block(_single_section(sections, "application_process")),
        faq=split_list_block(_single_section(sections, "faq")),
        contact=contact,
        summary=summary,
        confidence=min(confidence, 0.95),
        raw={"extraction_mode": "rule_based"},
    )


def _sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    current_key = ""
    collected: dict[str, list[str]] = {}
    for line in lines:
        stripped = line.strip()
        matched = _section_key(stripped)
        if matched:
            current_key = matched
            collected.setdefault(current_key, [])
            remainder = re.sub(r"^[^:]{2,40}[:\-]\s*", "", stripped)
            if remainder and remainder != stripped:
                collected[current_key].append(remainder)
            continue
        if current_key:
            collected[current_key].append(stripped)
    return {key: "\n".join(value).strip() for key, value in collected.items()}


def _section_key(line: str) -> str:
    lowered = line.lower().strip(" :-")
    for key, aliases in SECTION_ALIASES.items():
        if any(lowered.startswith(alias) for alias in aliases):
            return key
    return ""


def _single_section(sections: dict[str, str], key: str) -> str:
    return sections.get(key, "").strip() or "Not specified in document"


def _first_match(text: str, patterns: list[str], default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.M)
        if match:
            return match.group(1).strip(" .:-")
    return default


def _title_from_text(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if 5 <= len(line) <= 120:
            return line
    return "Not specified in document"


def _summary(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentence.strip() for sentence in sentences[:2] if sentence.strip())
    return summary[:500] if summary else "Not specified in document"


def _infer_category(text: str) -> str:
    lowered = text.lower()
    mapping = {
        "education": ["student", "scholarship", "school", "college"],
        "agriculture": ["farmer", "crop", "agriculture"],
        "health": ["health", "hospital", "medical"],
        "employment": ["employment", "skill", "training"],
        "housing": ["house", "housing", "home"],
    }
    for category, keywords in mapping.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "Not specified in document"
