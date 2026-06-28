"""
Processing page: shows progress/status while uploaded files are processed.
"""

from pathlib import Path

import streamlit as st

from backend.core.config import get_settings
from backend.localization.translator import translate
from backend.pipeline.ingestion_pipeline import run_ingestion_pipeline

language = st.session_state.get("language", "English")

st.title(translate("processing_title", language))

uploaded_files = st.session_state.get("uploaded_files")

if not uploaded_files:
    st.warning(translate("no_files_found", language))
    if st.button(translate("go_upload", language)):
        st.switch_page("pages/1_upload.py")
else:
    st.write(translate("processing_files", language, count=len(uploaded_files)))

    progress_bar = st.progress(0)
    status_text = st.empty()
    settings = get_settings()
    pending_dir = settings.paths.cache_dir / "streamlit_uploads"
    pending_dir.mkdir(parents=True, exist_ok=True)
    processed_documents = st.session_state.setdefault("processed_documents", [])
    processed_keys = st.session_state.setdefault("processed_upload_keys", set())

    for i, file in enumerate(uploaded_files):
        upload_key = f"{file.name}:{file.size}"
        status_text.text(translate("processing_file", language, name=file.name))
        if upload_key not in processed_keys:
            target_path = pending_dir / Path(file.name).name
            target_path.write_bytes(file.getvalue())
            try:
                result = run_ingestion_pipeline(target_path)
            except Exception as exc:
                st.error(f"{translate('process_failed', language, name=file.name)}: {exc}")
                st.stop()
            processed_documents.append(result.model_dump())
            processed_keys.add(upload_key)
        progress_bar.progress((i + 1) / len(uploaded_files))

    st.session_state["processing_done"] = True
    st.success(translate("processing_complete", language))

    if st.button(translate("continue_chat", language)):
        st.switch_page("pages/3_chat.py")
