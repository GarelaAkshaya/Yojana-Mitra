from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import streamlit as st

from backend.core.config import get_settings
from backend.localization.text_sanitizer import sanitize_text
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
    selected_language = language_code(language)
    try:
        transcript = (
            WhisperEngine().transcribe(audio_path, language=selected_language).strip()
        )
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
    return sanitize_text(transcript)


def answer_question(prompt: str, selected_document_id: int | None, language: str):
    selected_language = language_code(language)
    clean_prompt = sanitize_text(prompt)
    if selected_document_id is None:
        return None, translate("need_document", selected_language)

    with st.spinner(translate("searching", selected_language)):
        try:
            result = run_qa_pipeline(
                clean_prompt,
                document_id=selected_document_id,
                language=selected_language,
            )
            result.answer = sanitize_text(
                result.answer or translate("not_found", selected_language)
            )
            return result, result.answer
        except Exception as exc:
            logger.exception("Question answering failed")
            return None, f"{translate('processing_failed', selected_language)}: {exc}"


def answer_prompt(prompt: str, selected_document_id: int | None, language: str) -> str:
    result, response = answer_question(prompt, selected_document_id, language)
    if result and result.citations:
        sources = ", ".join(
            f"{citation.get('document_name', 'document')} {translate('page', language_code(language))} {citation.get('page_number', 1)}"
            for citation in result.citations[:3]
        )
        return f"{response}\n\n{translate('sources', language)}: {sources}"
    return response
