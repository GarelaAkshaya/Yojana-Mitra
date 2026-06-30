from __future__ import annotations

from pathlib import Path

import streamlit as st


def load_theme() -> None:
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "theme.css"
    try:
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass
