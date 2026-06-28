"""
Settings page.
"""

import streamlit as st

from backend.localization.translator import translate

language = st.session_state.get("language", "en")

st.title(translate("settings_title", language))

st.info(translate("settings_language_home", language))
