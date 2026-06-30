from __future__ import annotations

import hashlib
import math
from pathlib import Path

from backend.core.config import get_settings


class LocalEncoder:
    def __init__(self, model_path: str | Path | None = None) -> None:
        settings = get_settings()
        self.model_path = Path(model_path or settings.paths.embedding_model_path)
        self.model_name = self.model_path.name
        self._model = None
        self.dimension = 384

    def _load_model(self):
        if self._model is None and self.model_path.exists():
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(
                    str(self.model_path), local_files_only=True
                )
                self.dimension = int(self._model.get_sentence_embedding_dimension())
            except Exception:
                self._model = False
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if model:
            vectors = model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            return vectors.astype(float).tolist()
        return [self._hash_embedding(text) for text in texts]

    def _hash_embedding(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            sign = 1 if digest[4] % 2 == 0 else -1
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
