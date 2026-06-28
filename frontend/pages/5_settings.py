"""
Settings page: app language preference.
"""

import streamlit as st

from backend.localization.translator import translate
from frontend.components.language_toggle import language_toggle

language = st.session_state.get("language", "English")

st.title(translate("settings_title", language))

language_toggle("settings_language")

st.divider()

if st.button(translate("save_settings", st.session_state.get("language", "English"))):
    st.success(translate("settings_saved", st.session_state.get("language", "English")))
