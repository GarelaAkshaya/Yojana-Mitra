"""
Reusable component: confidence badge to visually indicate a confidence score.
"""

import streamlit as st


def confidence_badge(score: float) -> None:
    """
    Render a colored badge representing a confidence score.

    Args:
        score: Confidence value between 0 and 1.
    """
    score = max(0.0, min(1.0, score))
    percentage = round(score * 100)

    if score >= 0.75:
        color, label = "green", "High Confidence"
    elif score >= 0.4:
        color, label = "orange", "Medium Confidence"
    else:
        color, label = "red", "Low Confidence"

    st.markdown(
        f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        ">
            {label} · {percentage}%
        </span>
        """,
        unsafe_allow_html=True,
    )
