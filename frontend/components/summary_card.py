"""
Reusable component: summary card for displaying a title, text and metadata.
"""

import streamlit as st


def summary_card(title: str, summary: str, metadata: dict | None = None) -> None:
    """
    Render a styled summary card.

    Args:
        title: Card title.
        summary: Main body text / summary content.
        metadata: Optional dict of extra key-value info to display
                   (e.g. {"Date": "2026-06-28", "Source": "report.pdf"}).
    """
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(summary)

        if metadata:
            cols = st.columns(len(metadata))
            for col, (key, value) in zip(cols, metadata.items()):
                with col:
                    st.caption(key)
                    st.write(value)
