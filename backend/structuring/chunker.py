from __future__ import annotations

import re

from backend.core.config import get_settings
from backend.ingestion.pdf_extractor import RawTextResult
from backend.schemas.scheme import Chunk
from backend.structuring.normalizer import normalize_text


SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "Objective": ("objective", "purpose", "about the scheme"),
    "Benefits": ("benefit", "benefits", "assistance", "financial assistance", "subsidy"),
    "Eligibility": ("eligibility", "eligible", "who can apply", "beneficiaries", "eligibility criteria"),
    "Required Documents": ("documents", "document required", "documents required", "required documents"),
    "Application Process": ("application", "application process", "how to apply", "procedure", "apply online"),
    "Important Dates": ("important dates", "last date", "deadline"),
    "FAQs": ("faq", "faqs", "frequently asked questions"),
    "Contact Information": ("contact", "helpline", "contact information"),
}

HEADING_PATTERN = re.compile(r"^\s*(?:\d+[\).]\s*)?([A-Za-z][A-Za-z /&-]{2,80})\s*:?\s*$")


def chunk_text(raw: RawTextResult, document_id: int) -> list[Chunk]:
    settings = get_settings()
    chunks: list[Chunk] = []
    for page in raw.pages or []:
        page_text = normalize_text(page.text)
        if not page_text:
            continue
        chunks.extend(_chunk_page(page_text, document_id, page.page_number, settings.chunking.max_chars, settings.chunking.overlap_chars))
    if not chunks and raw.text:
        chunks.extend(_chunk_page(normalize_text(raw.text), document_id, 1, settings.chunking.max_chars, settings.chunking.overlap_chars))
    for index, chunk in enumerate(chunks):
        chunk.chunk_index = index
    return chunks


def _chunk_page(text: str, document_id: int, page_number: int, max_chars: int, overlap: int) -> list[Chunk]:
    paragraphs = _section_paragraphs(text)
    chunks: list[Chunk] = []
    buffer = ""
    section = ""
    for paragraph in paragraphs:
        first_line = paragraph.splitlines()[0].strip()
        detected_section = _section_title(first_line)
        if detected_section:
            if buffer:
                chunks.append(Chunk(document_id=document_id, text=buffer.strip(), page_number=page_number, section_title=section))
                buffer = ""
            section = detected_section
            paragraph = _ensure_section_heading(paragraph, section)
        if len(buffer) + len(paragraph) + 2 > max_chars and buffer:
            chunks.append(Chunk(document_id=document_id, text=buffer.strip(), page_number=page_number, section_title=section))
            buffer = _overlap_tail(buffer, overlap, section)
        buffer = f"{buffer}\n\n{paragraph}".strip()
    if buffer:
        chunks.append(Chunk(document_id=document_id, text=buffer.strip(), page_number=page_number, section_title=section))
    return chunks


def _section_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append("\n".join(current).strip())
                current = []
            continue
        if _section_title(stripped) and current:
            paragraphs.append("\n".join(current).strip())
            current = [stripped]
            continue
        current.append(stripped)
    if current:
        paragraphs.append("\n".join(current).strip())
    return [paragraph for paragraph in paragraphs if paragraph]


def _section_title(line: str) -> str:
    compact = line.strip().strip(":-").lower()
    if len(compact) > 90:
        return ""
    heading_match = HEADING_PATTERN.match(line)
    if not heading_match and ":" in line:
        heading_match = HEADING_PATTERN.match(line.split(":", 1)[0].strip())
    if not heading_match:
        return ""
    for section, aliases in SECTION_ALIASES.items():
        if any(compact == alias or compact.startswith(f"{alias}:") for alias in aliases):
            return section
    return ""


def _ensure_section_heading(paragraph: str, section: str) -> str:
    lines = paragraph.splitlines()
    if not lines:
        return section
    first = lines[0].strip()
    if first.lower().strip(":-") == section.lower():
        return paragraph
    remainder = re.sub(r"^[^:]{2,90}:\s*", "", paragraph, count=1).strip()
    return f"{section}\n{remainder}" if remainder and remainder != paragraph else f"{section}\n" + "\n".join(lines[1:]).strip()


def _overlap_tail(text: str, overlap: int, section: str) -> str:
    if overlap <= 0:
        return ""
    tail = text[-overlap:].strip()
    if not tail:
        return ""
    return f"{section}\n{tail}" if section and not tail.lower().startswith(section.lower()) else tail
