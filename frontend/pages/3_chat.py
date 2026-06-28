"""
Chat page: conversational interface with the assistant.
"""

import streamlit as st

from backend.localization.translator import translate
from backend.storage.repository import Repository
from frontend.services.chat_flow import answer_prompt, transcribe_audio


language = st.session_state.get("language", "en")

st.title(translate("chat_title", language))

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
