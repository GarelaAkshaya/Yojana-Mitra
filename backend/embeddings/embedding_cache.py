from __future__ import annotations

from backend.embeddings.bge_encoder import LocalEncoder
from backend.schemas.scheme import Chunk
from backend.storage.repository import Repository


def embed_and_store(
    chunks: list[Chunk],
    chunk_ids: list[int],
    repo: Repository,
    encoder: LocalEncoder | None = None,
) -> None:
    encoder = encoder or LocalEncoder()
    vectors = encoder.encode([chunk.text for chunk in chunks])
    for chunk_id, vector in zip(chunk_ids, vectors, strict=True):
        repo.save_embedding(chunk_id, vector, encoder.model_name)
