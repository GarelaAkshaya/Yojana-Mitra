"""
Reusable component: language toggle widget.
"""

import streamlit as st

SUPPORTED_LANGUAGES = ["English", "Hindi", "Telugu"]


def language_toggle(key: str = "language_toggle") -> str:
    """
    Render a language selector and return the selected language.

    Args:
        key: Unique Streamlit widget key (use different keys if rendered
             more than once on the same page).

    Returns:
        The selected language as a string.
    """
    selected = st.selectbox(
        "🌐 Language",
        SUPPORTED_LANGUAGES,
        index=SUPPORTED_LANGUAGES.index(st.session_state.get("language", "English")),
        key=key,
    )
    st.session_state["language"] = selected
    return selected
