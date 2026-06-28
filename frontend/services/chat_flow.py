from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import streamlit as st

from backend.core.config import get_settings
from backend.localization.translator import language_code, translate
from backend.pipeline.qa_pipeline import run_qa_pipeline
from backend.speech.whisper_engine import WhisperEngine, WhisperModelUnavailableError

logger = logging.getLogger(__name__)


def save_audio_input(audio_value) -> Path:
    settings = get_settings()
    voice_dir = settings.paths.cache_dir / "voice_inputs"
    voice_dir.mkdir(parents=True, exist_ok=True)

    audio_bytes = audio_value.getvalue()
    if not audio_bytes:
        raise ValueError("Recorded audio was empty. Please record your question again.")

    suffix = Path(getattr(audio_value, "name", "voice.wav")).suffix or ".wav"
    audio_path = voice_dir / f"voice_{uuid4().hex}{suffix}"
    audio_path.write_bytes(audio_bytes)
    return audio_path


def transcribe_audio(audio_value, language: str) -> str:
    audio_path = save_audio_input(audio_value)
    try:
        transcript = WhisperEngine().transcribe(audio_path, language=language_code(language)).strip()
    except WhisperModelUnavailableError:
        logger.exception("Voice transcription model is unavailable for %s", audio_path)
        raise
    except Exception as exc:
        logger.exception("Voice transcription failed for %s", audio_path)
        raise RuntimeError(
            f"The recording was saved, but transcription failed: {exc}. Please check the audio file and try again."
        ) from exc

    if not transcript:
        raise ValueError("No speech was detected in the recording. Please try again.")
    return transcript


def answer_prompt(prompt: str, selected_document_id: int | None, language: str) -> str:
    if selected_document_id is None:
        return translate("need_document", language)

    with st.spinner(translate("searching", language)):
        try:
            result = run_qa_pipeline(prompt, document_id=selected_document_id, language=language_code(language))
            response = result.answer or translate("not_found", language)
            if result.citations:
                sources = ", ".join(
                    f"{citation.get('document_name', 'document')} page {citation.get('page_number', 1)}"
                    for citation in result.citations[:3]
                )
                response = f"{response}\n\n{translate('sources', language)}: {sources}"
            return response
        except Exception as exc:
            logger.exception("Question answering failed")
            return f"{translate('processing_failed', language)}: {exc}"
