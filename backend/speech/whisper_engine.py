from __future__ import annotations

from pathlib import Path

from backend.core.config import get_settings
from backend.localization.text_sanitizer import sanitize_text
from backend.localization.translator import language_code


class WhisperModelUnavailableError(RuntimeError):
    """Raised when the local faster-whisper model cannot be loaded."""


class WhisperEngine:
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path or get_settings().paths.whisper_model_path)
        self._model = None

    def _validate_model_path(self) -> None:
        if not self.model_path.exists():
            raise WhisperModelUnavailableError(
                "Whisper model is not installed. Expected a faster-whisper model directory at "
                f"{self.model_path}. Place the offline model files there, then record again."
            )
        if self.model_path.suffix == ".bin":
            raise WhisperModelUnavailableError(
                "Configured Whisper model is a whisper.cpp .bin file, but this app uses faster-whisper. "
                "Set paths.whisper_model_path to a faster-whisper model directory."
            )
        if self.model_path.is_dir():
            missing_files = [
                file_name for file_name in ("config.json", "model.bin") if not (self.model_path / file_name).exists()
            ]
            if missing_files:
                raise WhisperModelUnavailableError(
                    "Whisper model directory is incomplete. "
                    f"Missing {', '.join(missing_files)} in {self.model_path}. "
                    "Install the faster-whisper model files before using voice input."
                )

    def _load(self):
        if self._model is None:
            self._validate_model_path()
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise WhisperModelUnavailableError(
                    "faster-whisper is not installed. Install requirements.txt, then try voice input again."
                ) from exc
            try:
                self._model = WhisperModel(str(self.model_path), device="cpu", compute_type="int8")
            except Exception as exc:
                raise WhisperModelUnavailableError(
                    f"Whisper model could not be loaded from {self.model_path}: {exc}"
                ) from exc
        return self._model

    def transcribe(self, audio_path: str | Path, language: str | None = None) -> str:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Recorded audio file not found: {audio_path}")
        if audio_path.stat().st_size == 0:
            raise ValueError("Recorded audio file is empty.")
        forced_language = language_code(language) if language else None
        segments, _info = self._load().transcribe(
            str(audio_path),
            language=forced_language,
            task="transcribe",
            condition_on_previous_text=False,
            vad_filter=True,
        )
        return sanitize_text(" ".join(segment.text.strip() for segment in segments if segment.text.strip()))
