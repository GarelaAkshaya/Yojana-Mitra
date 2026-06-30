"""
History page: view past sessions / chat history.
"""

import streamlit as st

from backend.localization.translator import translate
from frontend.components.theme_loader import load_theme

load_theme()
language = st.session_state.get("language", "English")

st.title(translate("history_title", language))

messages = st.session_state.get("messages", [])

if not messages:
    st.info(translate("no_history", language))
else:
    for message in messages:
        role = (
            translate("you", language)
            if message["role"] == "user"
            else translate("assistant", language)
        )
        st.markdown(f"**{role}:** {message['content']}")
        st.divider()

    if st.button(translate("clear_history", language)):
        st.session_state["messages"] = []
        st.rerun()
