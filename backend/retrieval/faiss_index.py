from __future__ import annotations

import json
import math
from pathlib import Path

from backend.core.config import get_settings


class VectorIndex:
    def __init__(self, index_dir: str | Path | None = None) -> None:
        self.index_dir = Path(index_dir or get_settings().paths.faiss_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.vectors_path = self.index_dir / "vectors.json"

    def save_vectors(self, chunk_vectors: dict[int, list[float]]) -> None:
        self.vectors_path.write_text(json.dumps(chunk_vectors), encoding="utf-8")

    def load_vectors(self) -> dict[int, list[float]]:
        if not self.vectors_path.exists():
            return {}
        data = json.loads(self.vectors_path.read_text(encoding="utf-8"))
        return {int(key): value for key, value in data.items()}

    def search(self, query_vector: list[float], top_k: int = 5) -> list[tuple[int, float]]:
        vectors = self.load_vectors()
        if not vectors:
            return []
        query_norm = _norm(query_vector)
        scores: list[tuple[int, float]] = []
        for chunk_id, vector in vectors.items():
            denom = query_norm * _norm(vector)
            score = float(_dot(query_vector, vector) / denom) if denom else 0.0
            scores.append((chunk_id, score))
        return sorted(scores, key=lambda item: item[1], reverse=True)[:top_k]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


def _norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector)) or 1.0
