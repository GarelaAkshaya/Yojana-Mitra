from pathlib import Path

import pytest

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
