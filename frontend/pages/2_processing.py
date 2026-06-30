"""
Processing page: shows progress/status while uploaded files are processed.
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402
from backend.core.config import get_settings  # noqa: E402
from backend.localization.translator import translate  # noqa: E402
from backend.pipeline.ingestion_pipeline import run_ingestion_pipeline  # noqa: E402
from frontend.bootstrap import bootstrap_project  # noqa: E402, F401
from frontend.components.theme_loader import load_theme  # noqa: E402

bootstrap_project()

logger = logging.getLogger(__name__)

load_theme()
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
            except Exception:
                logger.exception("Document processing failed for %s", file.name)
                st.error(
                    f"{translate('process_failed', language, name=file.name)}. {translate('check_logs', language)}"
                )
                st.stop()
            processed_documents.append(result.model_dump())
            processed_keys.add(upload_key)
        progress_bar.progress((i + 1) / len(uploaded_files))

    st.session_state["processing_done"] = True
    st.success("Document Processed")

    for document in processed_documents[-len(uploaded_files) :]:
        with st.container(border=True):
            st.subheader(document["scheme"]["scheme_name"])
            st.write(f"Pages Extracted: {document.get('pages_extracted', 0)}")
            st.write(f"Chunks Created: {document.get('chunks_created', 0)}")
            st.write(
                "Structured Information Extracted ✓"
                if document.get("structured_extracted")
                else "Structured Information Extracted"
            )
            st.write("SQLite Saved ✓" if document.get("sqlite_saved") else "SQLite Saved")
            st.write("Vector Index Ready ✓" if document.get("vector_index_ready") else "Vector Index Ready")

    if st.button(translate("continue_chat", language)):
        st.switch_page("pages/3_chat.py")
