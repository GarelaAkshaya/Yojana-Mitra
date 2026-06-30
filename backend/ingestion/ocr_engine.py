from __future__ import annotations

import logging
import os
from pathlib import Path

from backend.core.config import get_settings
from backend.ingestion.pdf_extractor import PageText, RawTextResult
from backend.ingestion.preprocessor import preprocess_image

logger = logging.getLogger(__name__)


class OCREngine:
    def __init__(self, languages: list[str] | None = None) -> None:
        self.languages = languages or ["en"]
        self.model_dir = get_settings().paths.ocr_model_dir
        self._reader = None

    def _load_reader(self):
        if self._reader is None:
            try:
                import easyocr
            except ImportError as exc:
                raise RuntimeError("EasyOCR is required for OCR. Install requirements-full.txt first.") from exc
            self.model_dir.mkdir(parents=True, exist_ok=True)
            allow_downloads = os.getenv("YOJANA_MITRA_ALLOW_MODEL_DOWNLOADS", "").lower() in {"1", "true", "yes"}
            try:
                self._reader = easyocr.Reader(
                    self.languages,
                    gpu=False,
                    verbose=False,
                    model_storage_directory=str(self.model_dir),
                    user_network_directory=str(self.model_dir),
                    download_enabled=allow_downloads,
                )
            except Exception as exc:
                logger.exception("OCR reader could not be initialized from %s", self.model_dir)
                raise RuntimeError(
                    "OCR model files are not available. Install the EasyOCR model files under "
                    f"{self.model_dir} for offline OCR, or set YOJANA_MITRA_ALLOW_MODEL_DOWNLOADS=1 "
                    "during deployment to allow the first-run model download."
                ) from exc
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
                    text = "\n".join(str(row).strip() for row in rows if str(row).strip())
                    pages.append(PageText(page_number=page_index, text=text))
                finally:
                    temp_png.unlink(missing_ok=True)
        full_text = "\n\n".join(page.text for page in pages if page.text)
        return RawTextResult(text=full_text, pages=pages, extraction_method="ocr_pdf")
