"""
History page: view past sessions / chat history.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402
from backend.localization.translator import translate  # noqa: E402
from frontend.bootstrap import bootstrap_project  # noqa: E402, F401
from frontend.components.theme_loader import load_theme  # noqa: E402

bootstrap_project()

load_theme()
language = st.session_state.get("language", "English")

st.title(translate("history_title", language))

messages = st.session_state.get("messages", [])

if not messages:
    st.info(translate("no_history", language))
else:
    for message in messages:
        role = translate("you", language) if message["role"] == "user" else translate("assistant", language)
        st.markdown(f"**{role}:** {message['content']}")
        st.divider()

    if st.button(translate("clear_history", language)):
        st.session_state["messages"] = []
        st.rerun()
