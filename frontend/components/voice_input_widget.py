"""
Reusable component: voice input widget.

Note: Streamlit doesn't have native microphone capture. This component
uses `st.audio_input` (Streamlit >= 1.38) to record audio, which can then
be passed to a speech-to-text backend.
"""

import streamlit as st


def voice_input_widget(key: str = "voice_input"):
    """
    Render a voice/audio input widget.

    Args:
        key: Unique Streamlit widget key.

    Returns:
        The recorded audio file-like object (or None if nothing recorded).
    """
    st.caption("🎤 Voice Input")

    try:
        audio_value = st.audio_input("Record your message", key=key)
    except AttributeError:
        st.warning("Voice input requires Streamlit >= 1.38. Please upgrade Streamlit to use this feature.")
        return None

    if audio_value is not None:
        st.audio(audio_value)
        st.success("Audio recorded. Ready to process.")

    return audio_value
