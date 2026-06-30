"""
Settings page.
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
language = st.session_state.get("language", "en")

st.title(translate("settings_title", language))

st.info(translate("settings_language_home", language))
