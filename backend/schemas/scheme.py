from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.core.pydantic_compat import BaseModel, Field


class ContactInfo(BaseModel):
    phone: str = ""
    email: str = ""
    address: str = ""
    website: str = ""


class Scheme(BaseModel):
    schema_version: str = "1.0"
    scheme_name: str = "Not specified in document"
    department: str = "Not specified in document"
    state: str = "Not specified in document"
    category: str = "Not specified in document"
    objective: str = "Not specified in document"
    eligibility: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    important_dates: list[str] = Field(default_factory=list)
    application_process: list[str] = Field(default_factory=list)
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = "Not specified in document"
    confidence: float = 0.0
    raw: dict[str, Any] = Field(default_factory=dict)


class DocumentRecord(BaseModel):
    id: int | None = None
    filename: str
    file_path: str
    file_type: str
    checksum: str
    status: str = "uploaded"
    language: str = "unknown"
    created_at: datetime | None = None


class Chunk(BaseModel):
    id: int | None = None
    document_id: int
    text: str
    page_number: int = 1
    section_title: str = ""
    chunk_index: int = 0


class RetrievedChunk(Chunk):
    score: float = 0.0
    document_name: str = ""
    scheme_name: str = ""


class GroundedAnswer(BaseModel):
    answer: str
    confidence: float
    citations: list[RetrievedChunk] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)
    refused: bool = False
