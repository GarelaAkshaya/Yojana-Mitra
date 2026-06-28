"""
Settings page: app preferences (language, theme, voice input, etc.)
"""

import streamlit as st

st.title("⚙️ Settings")

st.subheader("Language")
language = st.selectbox("Choose your preferred language", ["English", "Hindi", "Telugu"])
st.session_state["language"] = language

st.subheader("Theme")
theme = st.radio("Choose theme", ["Light", "Dark"], horizontal=True)
st.session_state["theme"] = theme

st.subheader("Voice Input")
voice_enabled = st.toggle("Enable voice input", value=False)
st.session_state["voice_enabled"] = voice_enabled

st.divider()

if st.button("Save Settings"):
    st.success("Settings saved successfully!")
