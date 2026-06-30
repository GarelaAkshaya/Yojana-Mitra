from pathlib import Path
from typing import Any, cast

import pytest

from backend.localization.text_sanitizer import sanitize_text
from backend.speech.whisper_engine import WhisperEngine, WhisperModelUnavailableError


def test_missing_whisper_model_has_actionable_error(tmp_path: Path):
    engine = WhisperEngine(tmp_path / "missing-model")

    with pytest.raises(WhisperModelUnavailableError, match="Whisper model is not installed"):
        engine._load()


def test_incomplete_whisper_model_directory_has_actionable_error(tmp_path: Path):
    model_dir = tmp_path / "faster-whisper-small"
    model_dir.mkdir()

    engine = WhisperEngine(model_dir)

    with pytest.raises(WhisperModelUnavailableError, match="Whisper model directory is incomplete"):
        engine._load()


def test_whisper_cpp_bin_path_has_actionable_error(tmp_path: Path):
    model_path = tmp_path / "ggml-small.bin"
    model_path.write_bytes(b"model")

    engine = WhisperEngine(model_path)

    with pytest.raises(WhisperModelUnavailableError, match="whisper.cpp .bin file"):
        engine._load()


def test_transcribe_forces_selected_telugu_language(tmp_path: Path):
    audio_path = tmp_path / "voice.wav"
    audio_path.write_bytes(b"audio")
    captured = {}

    class Segment:
        text = "తెలుగు ప్రశ్న"

    class Model:
        def transcribe(self, path: str, **kwargs):
            captured.update(kwargs)
            return [Segment()], object()

    engine = WhisperEngine(tmp_path)
    engine._model = cast(Any, Model())

    transcript = engine.transcribe(audio_path, language="Telugu")

    assert transcript == "తెలుగు ప్రశ్న"
    assert captured["language"] == "te"
    assert captured["task"] == "transcribe"
    assert captured["condition_on_previous_text"] is False


def test_sanitize_text_removes_corrupted_unicode():
    assert sanitize_text("లాభాలు � ԱՂՄ ࿌") == "లాభాలు"
