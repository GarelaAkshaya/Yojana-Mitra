"""
Streamlit entrypoint for the application.
Run with: streamlit run frontend/app.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import streamlit as st

from backend.localization.translator import translate
from backend.storage.repository import Repository
from frontend.components.chat_display import ICONS, render_chat_message, render_citations, render_home_feature
from frontend.components.theme_loader import load_theme
from frontend.components.language_buttons import language_buttons
from frontend.services.chat_flow import answer_question, transcribe_audio

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "static" / "images" / "logo.png"
CSS_PATH = APP_DIR / "static" / "css" / "theme.css"

st.set_page_config(
    page_title="Yojana Mitra",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(file_path: str) -> None:
    """Load a local CSS file into the Streamlit app."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def main() -> None:
    load_theme()
    st.session_state.setdefault("language", "en")
    st.session_state.setdefault("home_question_input", "")
    language = st.session_state.get("language", "en")

    st.sidebar.markdown(
        f"""
        <div class="ym-sidebar-brand">
          <div class="ym-sidebar-logo">YM</div>
          <div>
            <h2>{translate("app_title", language)}</h2>
            <p>{translate("offline_secure", language)}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""
        <div class="ym-sidebar-menu">
          <div><span>{ICONS["documents"]}</span>{translate("upload", language)}</div>
          <div><span>▣</span>{translate("processing_title", language)}</div>
          <div><span>{ICONS["chat"]}</span>{translate("chat_tab", language)}</div>
          <div><span>◷</span>{translate("history_title", language)}</div>
          <div><span>⚙</span>{translate("settings_title", language)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="page-hero home-hero">
          <div>
            <p class="eyebrow">Yojana Mitra</p>
            <h1>{translate("welcome_title", language)}</h1>
            <p>{translate("welcome_body", language)}</p>
          </div>
          <div class="hero-badge">{translate("offline_secure", language)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    language_buttons("home_language")

    feature_cols = st.columns(3)
    with feature_cols[0]:
        render_home_feature(ICONS["documents"], translate("document", language), translate("home_upload", language))
    with feature_cols[1]:
        render_home_feature(ICONS["audio"], translate("voice_message", language), translate("type_message", language))
    with feature_cols[2]:
        render_home_feature(ICONS["structured"], translate("structured_data", language), translate("ask_question", language))

    st.markdown(f"<h2 class='ym-section-heading'>{translate('home_upload', language)}</h2>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        translate("choose_files", language),
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="home_upload_files",
    )
    if uploaded_files:
        st.session_state["uploaded_files"] = uploaded_files
        st.success(translate("uploaded", language, count=len(uploaded_files)))
        if st.button(translate("continue_processing", language), key="home_continue_processing"):
            st.switch_page("pages/2_processing.py")

    st.markdown(f"<h2 class='ym-section-heading'>{translate('ask_question', language)}</h2>", unsafe_allow_html=True)

    question_container = st.container()
    voice_container = st.container()

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
        selected_label = st.selectbox(
            translate("document", language),
            list(document_options.keys()),
            key="home_document_select",
        )
        selected_document_id = document_options[selected_label]
    else:
        st.info(translate("upload_first", language))

    with voice_container:
        try:
            audio_value = st.audio_input(
                translate("voice_message", language),
                key="home_voice_input",
            )
        except AttributeError:
            audio_value = None
            st.warning(translate("voice_unavailable", language))

    if audio_value is not None:
        audio_size = getattr(audio_value, "size", None)
        if audio_size is None:
            audio_size = len(audio_value.getvalue())
        audio_id = f"{getattr(audio_value, 'file_id', '')}:{getattr(audio_value, 'name', '')}:{audio_size}"
        if st.session_state.get("home_transcribed_audio_id") != audio_id:
            st.caption(translate("recorded", language))
            try:
                st.session_state["home_question_input"] = transcribe_audio(audio_value, language)
                st.session_state["home_transcribed_audio_id"] = audio_id
                st.session_state["home_auto_submit_voice"] = True
                st.success(translate("transcribed", language))
                st.rerun()
            except Exception as exc:
                st.error(f"{translate('voice_failed', language)}: {exc}")

    with question_container:
        st.text_input(
            translate("type_message", language),
            key="home_question_input",
            placeholder=translate("type_message", language),
        )

    send_requested = st.button(translate("send", language), key="home_send_question")
    send_requested = send_requested or st.session_state.pop("home_auto_submit_voice", False)
    if send_requested:
        prompt = st.session_state.get("home_question_input", "").strip()
        if not prompt:
            st.warning(translate("empty_message", language))
            st.stop()

        result, response = answer_question(prompt, selected_document_id, language)
        citations = result.citations if result else []
        st.session_state.setdefault("messages", []).append({"role": "user", "content": prompt, "citations": []})
        st.session_state["messages"].append({"role": "assistant", "content": response, "citations": citations})
        render_chat_message("user", prompt, language)
        render_chat_message("assistant", response, language)
        render_citations(citations, language)


if __name__ == "__main__":
    main()
