"""
Reusable component: native language buttons.
"""

import streamlit as st

from backend.localization.translator import NATIVE_LANGUAGE_NAMES, language_code, translate


def language_buttons(key_prefix: str = "language") -> str:
    """
    Render native-script language buttons and persist the selected language code.
    """
    current_language = language_code(st.session_state.get("language", "en"))
    st.markdown(f"### {translate('choose_language', current_language)}")

    columns = st.columns(len(NATIVE_LANGUAGE_NAMES))
    for index, (code, label) in enumerate(NATIVE_LANGUAGE_NAMES.items()):
        with columns[index]:
            if st.button(
                label,
                key=f"{key_prefix}_{code}",
                type="primary" if current_language == code else "secondary",
                use_container_width=True,
            ):
                st.session_state["language"] = code
                st.rerun()

    return current_language
