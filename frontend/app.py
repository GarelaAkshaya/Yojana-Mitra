"""
Streamlit entrypoint for the application.
Run with: streamlit run frontend/app.py
"""

from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "static" / "images" / "logo.png"
CSS_PATH = APP_DIR / "static" / "css" / "theme.css"

st.set_page_config(
    page_title="Yojana Mitra",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(file_path: str) -> None:
    """Load a local CSS file into the Streamlit app."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def main() -> None:
    load_css(str(CSS_PATH))

    st.sidebar.image(str(LOGO_PATH), width=120)
    st.sidebar.title("Navigation")
    st.sidebar.markdown(
        """
        Use the pages in the sidebar to:
        - **Upload** your files
        - **Process** your data
        - **Chat** with the assistant
        - View **History**
        - Manage **Settings**
        """
    )

    st.title("Welcome")
    st.write("Select a page from the sidebar to get started.")


if __name__ == "__main__":
    main()
