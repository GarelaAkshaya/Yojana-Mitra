from __future__ import annotations

# pylint: disable=no-member
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


class AppConfig(BaseModel):
    name: str = "Yojana Mitra"
    default_language: str = "en"
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "hi", "te"])


class PathsConfig(BaseModel):
    data_dir: Path = Path("data")
    upload_dir: Path = Path("data/uploads")
    processed_dir: Path = Path("data/processed")
    cache_dir: Path = Path("data/cache")
    db_path: Path = Path("data/yojana_mitra.sqlite3")
    faiss_dir: Path = Path("data/faiss_store")
    llm_model_path: Path = Path("models/llm/model.gguf")
    embedding_model_path: Path = Path("models/embeddings/bge-small-en-v1.5")
    ocr_model_dir: Path = Path("models/ocr")
    whisper_model_path: Path = Path("models/whisper/ggml-small.bin")


class RetrievalConfig(BaseModel):
    top_k: int = 5
    min_confidence: float = 0.2


class ChunkingConfig(BaseModel):
    max_chars: int = 900
    overlap_chars: int = 120


class LLMConfig(BaseModel):
    max_tokens: int = 256
    temperature: float = 0.1
    context_window: int = 4096


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)

    def resolve_paths(self) -> Settings:
        for field_name in PathsConfig.model_fields:
            value = getattr(self.paths, field_name)
            if isinstance(value, Path) and not value.is_absolute():
                setattr(self.paths, field_name, PROJECT_ROOT / value)
        data_dir_override = os.getenv("YOJANA_MITRA_DATA_DIR")
        if data_dir_override:
            data_dir = Path(data_dir_override).expanduser()
            if not data_dir.is_absolute():
                data_dir = PROJECT_ROOT / data_dir
            self.paths.data_dir = data_dir
            self.paths.upload_dir = data_dir / "uploads"
            self.paths.processed_dir = data_dir / "processed"
            self.paths.cache_dir = data_dir / "cache"
            self.paths.db_path = data_dir / "yojana_mitra.sqlite3"
            self.paths.faiss_dir = data_dir / "faiss_store"
        return self

    def ensure_directories(self) -> None:
        for path in [
            self.paths.data_dir,
            self.paths.upload_dir,
            self.paths.processed_dir,
            self.paths.cache_dir,
            self.paths.faiss_dir,
            self.paths.llm_model_path.parent,
            self.paths.embedding_model_path.parent,
            self.paths.ocr_model_dir,
            self.paths.whisper_model_path.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=1)
def get_settings(config_path: str | Path | None = None) -> Settings:
    configured_path = config_path or os.getenv("YOJANA_MITRA_CONFIG") or DEFAULT_CONFIG_PATH
    path = Path(configured_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    settings = Settings.model_validate(_load_yaml(path)).resolve_paths()
    settings.ensure_directories()
    return settings
