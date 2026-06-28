"""
Chat page: conversational interface with the assistant.
"""

from pathlib import Path

import streamlit as st

from backend.core.config import get_settings
from backend.localization.translator import language_code, translate
from backend.pipeline.qa_pipeline import run_qa_pipeline
from backend.speech.whisper_engine import WhisperEngine
from backend.storage.repository import Repository


def transcribe_audio(audio_value, language: str) -> str:
    settings = get_settings()
    voice_dir = settings.paths.cache_dir / "voice_inputs"
    voice_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(getattr(audio_value, "name", "voice.wav")).suffix or ".wav"
    audio_path = voice_dir / f"chat_voice_{len(st.session_state['messages'])}{suffix}"
    audio_path.write_bytes(audio_value.getvalue())
    return WhisperEngine().transcribe(audio_path, language=language_code(language))


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
            return f"{translate('processing_failed', language)}: {exc}"


language = st.session_state.get("language", "English")

st.title(translate("chat_title", language))

if "messages" not in st.session_state:
    st.session_state["messages"] = []

processed_documents = st.session_state.get("processed_documents", [])
document_options = {
    f"{doc['scheme']['scheme_name']} ({doc['document_id']})": doc["document_id"]
    for doc in processed_documents
}

if not document_options:
    document_options = {
        f"{scheme['scheme_name']} ({scheme['document_id']})": scheme["document_id"]
        for scheme in Repository().list_schemes()
    }

selected_document_id = None
if document_options:
    selected_label = st.selectbox(translate("document", language), list(document_options.keys()))
    selected_document_id = document_options[selected_label]
else:
    st.warning(translate("upload_first", language))

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

text_column, voice_column, send_column = st.columns([5, 3, 1])
with text_column:
    typed_prompt = st.text_input(
        translate("type_message", language),
        key="chat_text_input",
        label_visibility="collapsed",
        placeholder=translate("type_message", language),
    )
with voice_column:
    try:
        audio_value = st.audio_input(
            translate("voice_message", language),
            key="chat_voice_input",
            label_visibility="collapsed",
        )
    except AttributeError:
        audio_value = None
        st.warning(translate("voice_unavailable", language))
with send_column:
    send_clicked = st.button(translate("send", language), use_container_width=True)

if audio_value is not None:
    st.caption(translate("recorded", language))

if send_clicked:
    prompt = typed_prompt.strip()

    if not prompt and audio_value is not None:
        try:
            prompt = transcribe_audio(audio_value, language).strip()
        except Exception as exc:
            st.error(f"{translate('voice_failed', language)}: {exc}")
            st.stop()

    if not prompt:
        st.warning(translate("empty_message", language))
        st.stop()

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = answer_prompt(prompt, selected_document_id, language)

    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    st.rerun()
