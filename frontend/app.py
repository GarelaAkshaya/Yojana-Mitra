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
from frontend.components.language_buttons import language_buttons
from frontend.services.chat_flow import answer_prompt, transcribe_audio

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
    load_css(str(CSS_PATH))
    st.session_state.setdefault("language", "en")
    st.session_state.setdefault("home_question_input", "")
    language = st.session_state.get("language", "en")

    st.sidebar.image(str(LOGO_PATH), width=120)
    st.sidebar.title(translate("navigation", language))
    st.sidebar.markdown(
        """
        Use the pages in the sidebar to:
        - **Upload** your files
        - **Process** your data
        - **Chat** with the assistant
        - View **History**
        - Manage **Settings**
        """
    )

    st.image(str(LOGO_PATH), width=130)
    st.title(translate("welcome_title", language))
    st.write(translate("welcome_body", language))
    language_buttons("home_language")

    st.divider()

    st.subheader(translate("home_upload", language))
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

    st.subheader(translate("ask_question", language))

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

        response = answer_prompt(prompt, selected_document_id, language)
        st.session_state.setdefault("messages", []).append({"role": "user", "content": prompt})
        st.session_state["messages"].append({"role": "assistant", "content": response})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)


if __name__ == "__main__":
    main()
