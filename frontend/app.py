"""
Streamlit entrypoint for the application.
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="My App",
    page_icon="static/images/logo.png",
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
    load_css("static/css/theme.css")

    st.sidebar.image("static/images/logo.png", width=120)
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
