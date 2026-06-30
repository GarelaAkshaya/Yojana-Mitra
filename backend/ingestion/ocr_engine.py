from __future__ import annotations

from pathlib import Path

from backend.ingestion.pdf_extractor import PageText, RawTextResult
from backend.ingestion.preprocessor import preprocess_image


class OCREngine:
    def __init__(self, languages: list[str] | None = None) -> None:
        self.languages = languages or ["en"]
        self._reader = None

    def _load_reader(self):
        if self._reader is None:
            try:
                import easyocr
            except ImportError as exc:
                raise RuntimeError(
                    "EasyOCR is required for OCR. Install requirements.txt first."
                ) from exc
            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
        return self._reader

    def extract_image(self, path: str | Path) -> RawTextResult:
        image_path = preprocess_image(path)
        reader = self._load_reader()
        rows = reader.readtext(image_path, detail=0, paragraph=True)
        text = "\n".join(str(row).strip() for row in rows if str(row).strip())
        return RawTextResult(
            text=text,
            pages=[PageText(page_number=1, text=text)],
            extraction_method="ocr_image",
        )

    def extract_pdf_pages(self, path: str | Path) -> RawTextResult:
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("PyMuPDF is required to OCR scanned PDFs") from exc

        reader = self._load_reader()
        pages: list[PageText] = []
        with fitz.open(path) as doc:
            for page_index, page in enumerate(doc, start=1):
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                temp_png = Path(path).with_suffix(f".page-{page_index}.png")
                pix.save(temp_png)
                try:
                    rows = reader.readtext(str(temp_png), detail=0, paragraph=True)
                    text = "\n".join(
                        str(row).strip() for row in rows if str(row).strip()
                    )
                    pages.append(PageText(page_number=page_index, text=text))
                finally:
                    temp_png.unlink(missing_ok=True)
        full_text = "\n\n".join(page.text for page in pages if page.text)
        return RawTextResult(text=full_text, pages=pages, extraction_method="ocr_pdf")
