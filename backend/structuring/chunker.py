from __future__ import annotations

import re

from backend.core.config import get_settings
from backend.ingestion.pdf_extractor import RawTextResult
from backend.schemas.scheme import Chunk
from backend.structuring.normalizer import normalize_text


HEADING_PATTERN = re.compile(r"^(eligibility|benefits?|documents?|application|objective|contact|important dates?|last date|how to apply|scheme)", re.I)


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
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    section = ""
    for paragraph in paragraphs:
        first_line = paragraph.splitlines()[0].strip()
        if HEADING_PATTERN.search(first_line):
            section = first_line[:120]
        if len(buffer) + len(paragraph) + 2 > max_chars and buffer:
            chunks.append(Chunk(document_id=document_id, text=buffer.strip(), page_number=page_number, section_title=section))
            buffer = buffer[-overlap:] if overlap > 0 else ""
        buffer = f"{buffer}\n\n{paragraph}".strip()
    if buffer:
        chunks.append(Chunk(document_id=document_id, text=buffer.strip(), page_number=page_number, section_title=section))
    return chunks
