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
from backend.structuring.scheme_parser import extract_scheme_fields
from backend.structuring.schema_validator import validate_scheme


class IngestionResult(BaseModel):
    document_id: int
    status: str
    scheme: Scheme
    chunks_created: int
    extraction_method: str


def run_ingestion_pipeline(file_path: str | Path, repo: Repository | None = None) -> IngestionResult:
    repo = repo or Repository()
    record = load_file(file_path)
    document_id = repo.create_document(record)
    try:
        raw = _extract_text(record.file_path, record.file_type)
        language = detect_language(raw.text)
        repo.update_document_status(document_id, "processing")
        chunks = chunk_text(raw, document_id)
        chunk_ids = repo.insert_chunks(chunks)
        scheme = validate_scheme(extract_scheme_fields(raw.text))
        repo.save_scheme(document_id, scheme)
        embed_and_store(chunks, chunk_ids, repo)
        rebuild_vector_index(repo)
        repo.update_document_status(document_id, "processed")
        return IngestionResult(
            document_id=document_id,
            status="processed",
            scheme=scheme,
            chunks_created=len(chunks),
            extraction_method=raw.extraction_method,
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
