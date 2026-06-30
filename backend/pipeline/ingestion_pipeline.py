from __future__ import annotations

from pathlib import Path

from backend.core.pydantic_compat import BaseModel
from backend.embeddings.embedding_cache import embed_and_store
from backend.ingestion.file_loader import load_file
from backend.ingestion.language_detector import detect_language
from backend.ingestion.ocr_engine import OCREngine
from backend.ingestion.pdf_extractor import RawTextResult, extract_pdf_text
from backend.retrieval.hybrid_search import rebuild_vector_index
from backend.schemas.scheme import Scheme
from backend.storage.repository import Repository
from backend.structuring.chunker import chunk_text
from backend.structuring.slm_extractor import extract_structured_scheme


class IngestionResult(BaseModel):
    document_id: int
    status: str
    scheme: Scheme
    pages_extracted: int
    chunks_created: int
    extraction_method: str
    structured_extracted: bool = False
    sqlite_saved: bool = False
    vector_index_ready: bool = False


def run_ingestion_pipeline(file_path: str | Path, repo: Repository | None = None) -> IngestionResult:
    repo = repo or Repository()
    record = load_file(file_path)
    document_id = repo.create_document(record)
    try:
        raw = _extract_text(record.file_path, record.file_type)
        language = detect_language(raw.text)
        repo.update_document_status(document_id, "processing")
        repo.update_document_language(document_id, language)
        chunks = chunk_text(raw, document_id)
        chunk_ids = repo.insert_chunks(chunks)
        scheme = extract_structured_scheme(raw.text)
        repo.save_scheme(document_id, scheme)
        embed_and_store(chunks, chunk_ids, repo)
        rebuild_vector_index(repo)
        repo.update_document_status(document_id, "processed")
        return IngestionResult(
            document_id=document_id,
            status="processed",
            scheme=scheme,
            pages_extracted=len(raw.pages) or (1 if raw.text else 0),
            chunks_created=len(chunks),
            extraction_method=raw.extraction_method,
            structured_extracted=True,
            sqlite_saved=True,
            vector_index_ready=True,
        )
    except Exception as exc:
        repo.update_document_status(document_id, "failed", str(exc))
        raise


def _extract_text(file_path: str, file_type: str) -> RawTextResult:
    if file_type == "pdf":
        native = extract_pdf_text(file_path)
        if native.extraction_method == "native_pdf":
            return native
        return OCREngine().extract_pdf_pages(file_path)
    return OCREngine().extract_image(file_path)
