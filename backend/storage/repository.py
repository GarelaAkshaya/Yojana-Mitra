from __future__ import annotations

import json
import re
from hashlib import sha256
from typing import Any

from backend.schemas.scheme import Chunk, DocumentRecord, GroundedAnswer, RetrievedChunk, Scheme
from backend.storage.db_manager import DatabaseManager
from backend.structuring.section_utils import SECTION_TO_DETAIL_KEY, is_useful_text, items_from_chunks, useful_items


class Repository:
    def __init__(self, db: DatabaseManager | None = None) -> None:
        self.db = db or DatabaseManager()
        self.db.run_migrations()

    def create_document(self, record: DocumentRecord) -> int:
        with self.db.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM documents WHERE checksum = ?", (record.checksum,)
            ).fetchone()
            if existing:
                return int(existing["id"])
            cur = conn.execute(
                """
                INSERT INTO documents(filename, file_path, file_type, checksum, status, language)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.filename,
                    record.file_path,
                    record.file_type,
                    record.checksum,
                    record.status,
                    record.language,
                ),
            )
            return int(cur.lastrowid)

    def update_document_status(self, document_id: int, status: str, error: str | None = None) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, error, document_id),
            )

    def update_document_language(self, document_id: int, language: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET language = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (language, document_id),
            )

    def save_scheme(self, document_id: int, scheme: Scheme) -> int:
        payload = {
            "eligibility_json": json.dumps(scheme.eligibility, ensure_ascii=False),
            "benefits_json": json.dumps(scheme.benefits, ensure_ascii=False),
            "documents_json": json.dumps(scheme.documents, ensure_ascii=False),
            "important_dates_json": json.dumps(scheme.important_dates, ensure_ascii=False),
            "application_process_json": json.dumps(scheme.application_process, ensure_ascii=False),
            "contact_json": scheme.contact.model_dump_json(),
            "raw_json": json.dumps(scheme.raw, ensure_ascii=False),
        }
        with self.db.connect() as conn:
            conn.execute("DELETE FROM schemes WHERE document_id = ?", (document_id,))
            cur = conn.execute(
                """
                INSERT INTO schemes(
                    document_id, scheme_name, department, state, category, objective,
                    eligibility_json, benefits_json, documents_json, important_dates_json,
                    application_process_json, contact_json, summary, confidence, raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    scheme.scheme_name,
                    scheme.department,
                    scheme.state,
                    scheme.category,
                    scheme.objective,
                    payload["eligibility_json"],
                    payload["benefits_json"],
                    payload["documents_json"],
                    payload["important_dates_json"],
                    payload["application_process_json"],
                    payload["contact_json"],
                    scheme.summary,
                    scheme.confidence,
                    payload["raw_json"],
                ),
            )
            scheme_id = int(cur.lastrowid)
            self._insert_section_items(conn, "benefits", scheme_id, scheme.benefits)
            self._insert_section_items(conn, "eligibility", scheme_id, scheme.eligibility)
            self._insert_section_items(conn, "required_documents", scheme_id, scheme.documents)
            self._insert_section_items(conn, "application_process", scheme_id, scheme.application_process)
            self._insert_section_items(conn, "faqs", scheme_id, scheme.faq)
            return scheme_id

    @staticmethod
    def _insert_section_items(conn: Any, table: str, scheme_id: int, items: list[str]) -> None:
        for index, item in enumerate(items):
            conn.execute(
                f"INSERT INTO {table}(scheme_id, item_order, text) VALUES (?, ?, ?)",
                (scheme_id, index, item),
            )

    def insert_chunks(self, chunks: list[Chunk]) -> list[int]:
        ids: list[int] = []
        with self.db.connect() as conn:
            if chunks:
                conn.execute("DELETE FROM chunks WHERE document_id = ?", (chunks[0].document_id,))
            for chunk in chunks:
                cur = conn.execute(
                    """
                    INSERT INTO chunks(document_id, chunk_index, page_number, section_title, text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        chunk.document_id,
                        chunk.chunk_index,
                        chunk.page_number,
                        chunk.section_title,
                        chunk.text,
                    ),
                )
                ids.append(int(cur.lastrowid))
        return ids

    def save_embedding(self, chunk_id: int, vector: list[float], model_name: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO embeddings(chunk_id, model_name, dimension, vector_json)
                VALUES (?, ?, ?, ?)
                """,
                (chunk_id, model_name, len(vector), json.dumps(vector)),
            )

    def get_chunks(self, document_id: int | None = None) -> list[RetrievedChunk]:
        sql = """
            SELECT c.*, d.filename AS document_name, COALESCE(s.scheme_name, '') AS scheme_name
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            LEFT JOIN schemes s ON s.document_id = c.document_id
        """
        params: tuple[Any, ...] = ()
        if document_id is not None:
            sql += " WHERE c.document_id = ?"
            params = (document_id,)
        sql += " ORDER BY c.document_id, c.chunk_index"
        with self.db.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [RetrievedChunk(**dict(row)) for row in rows]

    def search_fts(self, query: str, limit: int = 5, document_id: int | None = None) -> list[RetrievedChunk]:
        tokens = re.findall(r"[\w]+", query.lower())
        clean_query = " OR ".join(tokens) or query
        sql = """
            SELECT c.*, d.filename AS document_name, COALESCE(s.scheme_name, '') AS scheme_name,
                   bm25(chunks_fts) * -1 AS score
            FROM chunks_fts
            JOIN chunks c ON c.id = chunks_fts.rowid
            JOIN documents d ON d.id = c.document_id
            LEFT JOIN schemes s ON s.document_id = c.document_id
            WHERE chunks_fts MATCH ?
        """
        params: list[Any] = [clean_query]
        if document_id is not None:
            sql += " AND c.document_id = ?"
            params.append(document_id)
        sql += " ORDER BY score DESC LIMIT ?"
        params.append(limit)
        try:
            with self.db.connect() as conn:
                rows = conn.execute(sql, params).fetchall()
            return [RetrievedChunk(**dict(row)) for row in rows]
        except Exception:
            return []

    def get_scheme_details(self, document_id: int) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            scheme = conn.execute(
                """
                SELECT s.*, d.filename, d.file_path
                FROM schemes s JOIN documents d ON d.id = s.document_id
                WHERE s.document_id = ?
                """,
                (document_id,),
            ).fetchone()
            if not scheme:
                return None
            details = dict(scheme)
            section_tables = {
                "benefits": "benefits",
                "eligibility": "eligibility",
                "documents": "required_documents",
                "application_process": "application_process",
                "faq": "faqs",
            }
            for key, table in section_tables.items():
                rows = conn.execute(
                    f"SELECT text FROM {table} WHERE scheme_id = ? ORDER BY item_order, id",
                    (details["id"],),
                ).fetchall()
                if rows:
                    details[key] = useful_items([row["text"] for row in rows])
                else:
                    json_key = "documents_json" if key == "documents" else f"{key}_json"
                    details[key] = useful_items(json.loads(details.get(json_key, "[]")) if json_key in details else [])
        chunks = self.get_chunks(document_id)
        for section_title, key in SECTION_TO_DETAIL_KEY.items():
            if not details.get(key):
                details[key] = items_from_chunks(chunks, section_title)
        if not is_useful_text(details.get("objective")):
            objective_items = items_from_chunks(chunks, "Objective", limit=4)
            details["objective"] = " ".join(objective_items) if objective_items else details.get("objective", "")
        return details

    def list_schemes(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*, d.filename, d.file_path
                FROM schemes s JOIN documents d ON d.id = s.document_id
                ORDER BY s.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def log_query(self, document_id: int | None, question: str, result: GroundedAnswer, language: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO query_logs(document_id, question, answer, confidence, retrieved_chunk_ids_json, language)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    question,
                    result.answer,
                    result.confidence,
                    json.dumps([chunk.id for chunk in result.citations]),
                    language,
                ),
            )

    def get_cached_response(
        self,
        document_id: int | None,
        question: str,
        language: str = "en",
    ) -> dict[str, Any] | None:
        key = self.cache_key(document_id, question, language)
        with self.db.connect() as conn:
            row = conn.execute("SELECT response_json FROM response_cache WHERE cache_key = ?", (key,)).fetchone()
        return json.loads(row["response_json"]) if row else None

    def set_cached_response(
        self,
        document_id: int | None,
        question: str,
        response: dict[str, Any],
        language: str = "en",
    ) -> None:
        key = self.cache_key(document_id, question, language)
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO response_cache(cache_key, document_id, question, response_json)
                VALUES (?, ?, ?, ?)
                """,
                (key, document_id, question, json.dumps(response, ensure_ascii=False)),
            )

    @staticmethod
    def cache_key(document_id: int | None, question: str, language: str = "en") -> str:
        normalized = " ".join(question.lower().split())
        return sha256(f"qa-v2:{document_id or 'all'}:{language}:{normalized}".encode("utf-8")).hexdigest()
