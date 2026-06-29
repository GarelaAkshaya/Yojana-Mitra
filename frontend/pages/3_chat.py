"""
Chat page: conversational interface with the assistant.
"""

from html import escape

import streamlit as st

from backend.localization.translator import translate
from backend.storage.repository import Repository
from backend.structuring.section_utils import useful_items
from frontend.components.theme_loader import load_theme
from frontend.services.chat_flow import answer_prompt, transcribe_audio


def _render_items(title: str, items: list[str], icon: str, empty_text: str) -> None:
    items = useful_items(items)
    st.markdown(f"<div class='section-card'><div class='section-title'><span>{escape(icon)}</span>{escape(title)}</div>", unsafe_allow_html=True)
    if not items:
        st.markdown(f"<p class='muted'>{escape(empty_text)}</p></div>", unsafe_allow_html=True)
        return
    for item in items:
        st.markdown(f"<div class='section-item'>{escape(item)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


load_theme()
language = st.session_state.get("language", "en")
repo = Repository()

st.markdown(
    f"""
    <div class="page-hero">
      <div>
        <p class="eyebrow">Yojana Mitra</p>
        <h1>{escape(translate("chat_title", language))}</h1>
      </div>
      <div class="hero-badge">{escape(translate("offline_secure", language))}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if st.session_state.pop("clear_chat_text_input", False):
    st.session_state["chat_text_input"] = ""
st.session_state.setdefault("chat_text_input", "")

processed_documents = st.session_state.get("processed_documents", [])
document_options = {
    f"{doc['scheme']['scheme_name']} ({doc['document_id']})": doc["document_id"]
    for doc in processed_documents
}

if not document_options:
    document_options = {
        f"{scheme['scheme_name']} ({scheme['document_id']})": scheme["document_id"]
        for scheme in repo.list_schemes()
    }

selected_document_id = None
if document_options:
    labels = list(document_options.keys())
    previous_id = st.session_state.get("selected_document_id")
    default_index = 0
    if previous_id in document_options.values():
        default_index = list(document_options.values()).index(previous_id)
    selected_label = st.selectbox(translate("document", language), labels, index=default_index, key="chat_document_select")
    selected_document_id = document_options[selected_label]
    st.session_state["selected_document_id"] = selected_document_id
else:
    st.warning(translate("upload_first", language))

chat_tab, structured_tab = st.tabs([translate("chat_tab", language), translate("structured_data", language)])

with chat_tab:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question_container = st.container()
    voice_container = st.container()

    with voice_container:
        try:
            audio_value = st.audio_input(
                translate("voice_message", language),
                key="chat_voice_input",
            )
        except AttributeError:
            audio_value = None
            st.warning(translate("voice_unavailable", language))

    if audio_value is not None:
        audio_size = getattr(audio_value, "size", None)
        if audio_size is None:
            audio_size = len(audio_value.getvalue())
        audio_id = f"{getattr(audio_value, 'file_id', '')}:{getattr(audio_value, 'name', '')}:{audio_size}"
        if st.session_state.get("chat_transcribed_audio_id") != audio_id:
            st.caption(translate("recorded", language))
            try:
                st.session_state["chat_text_input"] = transcribe_audio(audio_value, language)
                st.session_state["chat_transcribed_audio_id"] = audio_id
                st.session_state["chat_auto_submit_voice"] = True
                st.success(translate("transcribed", language))
                st.rerun()
            except Exception as exc:
                st.error(f"{translate('voice_failed', language)}: {exc}")

    with question_container:
        text_column, send_column = st.columns([6, 1])
        with text_column:
            st.text_input(
                translate("type_message", language),
                key="chat_text_input",
                label_visibility="collapsed",
                placeholder=translate("type_message", language),
            )
        with send_column:
            send_clicked = st.button(translate("send", language), use_container_width=True)

    send_requested = send_clicked or st.session_state.pop("chat_auto_submit_voice", False)
    if send_requested:
        prompt = st.session_state.get("chat_text_input", "").strip()

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

        st.session_state["clear_chat_text_input"] = True
        st.rerun()

with structured_tab:
    if not selected_document_id:
        st.info(translate("upload_first", language))
    else:
        details = repo.get_scheme_details(selected_document_id)
        if not details:
            st.info(translate("structured_missing", language))
        else:
            st.markdown(
                f"""
                <div class="scheme-summary">
                  <p class="eyebrow">{escape(translate("structured_data", language))}</p>
                  <h2>{escape(details.get("scheme_name") or translate("not_specified_short", language))}</h2>
                  <div class="summary-grid">
                    <div><span>{escape(translate("category", language))}</span><strong>{escape(details.get("category") or translate("not_specified_short", language))}</strong></div>
                    <div><span>{escape(translate("source_file", language))}</span><strong>{escape(details.get("filename") or translate("not_specified_short", language))}</strong></div>
                  </div>
                  <p>{escape(details.get("objective") or translate("not_specified_short", language))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            empty_text = translate("not_specified_short", language)
            _render_items(translate("benefits", language), details.get("benefits", []), "OK", empty_text)
            _render_items(translate("eligibility", language), details.get("eligibility", []), "EL", empty_text)
            _render_items(translate("required_documents", language), details.get("documents", []), "DOC", empty_text)
            _render_items(translate("application_process", language), details.get("application_process", []), "GO", empty_text)
