from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class RawTextResult:
    text: str
    pages: list[PageText]
    extraction_method: str


def extract_pdf_text(path: str | Path, min_text_chars: int = 80) -> RawTextResult:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF extraction") from exc

    pages: list[PageText] = []
    with fitz.open(path) as doc:
        for page_index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            pages.append(PageText(page_number=page_index, text=text))

    full_text = "\n\n".join(page.text for page in pages if page.text)
    method = "native_pdf" if len(full_text) >= min_text_chars else "requires_ocr"
    return RawTextResult(text=full_text, pages=pages, extraction_method=method)
