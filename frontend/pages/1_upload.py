"""
Upload page: lets the user upload files for processing.
"""

import streamlit as st

from backend.localization.translator import translate
from frontend.components.theme_loader import load_theme

load_theme()
language = st.session_state.get("language", "English")

st.title(translate("upload_title", language))
st.write(translate("upload_body", language))

uploaded_files = st.file_uploader(
    translate("choose_files", language),
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.session_state["uploaded_files"] = uploaded_files
    st.success(translate("uploaded", language, count=len(uploaded_files)))

    for file in uploaded_files:
        with st.expander(file.name):
            st.write(f"**{translate('file_type', language)}:** {file.type}")
            st.write(f"**{translate('file_size', language)}:** {file.size} bytes")

    if st.button(translate("continue_processing", language)):
        st.switch_page("pages/2_processing.py")
else:
    st.info(translate("no_files", language))
