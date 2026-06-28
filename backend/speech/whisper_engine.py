from __future__ import annotations

from pathlib import Path

from backend.core.config import get_settings


class WhisperEngine:
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path or get_settings().paths.whisper_model_path)
        self._model = None

    def _load(self):
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Whisper model not found: {self.model_path}")
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("faster-whisper is required for voice input") from exc
            self._model = WhisperModel(str(self.model_path), device="cpu", compute_type="int8")
        return self._model

    def transcribe(self, audio_path: str | Path, language: str | None = None) -> str:
        segments, _info = self._load().transcribe(str(audio_path), language=language)
        return " ".join(segment.text.strip() for segment in segments if segment.text.strip())
