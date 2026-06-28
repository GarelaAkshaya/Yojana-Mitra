"""
Reusable component: language selector widget.
"""

import streamlit as st

from backend.localization.translator import LANGUAGE_NAMES, language_name, translate


def language_toggle(key: str = "language_toggle") -> str:
    """
    Render a language selector and return the selected language name.
    """
    supported_languages = list(LANGUAGE_NAMES.keys())
    current_language = language_name(st.session_state.get("language", "English"))
    selected = st.selectbox(
        translate("language", current_language),
        supported_languages,
        index=supported_languages.index(current_language),
        key=key,
    )
    st.session_state["language"] = selected
    return selected
