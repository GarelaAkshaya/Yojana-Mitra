"""
History page: view past sessions / chat history.
"""

import streamlit as st

st.title("🕘 History")

messages = st.session_state.get("messages", [])

if not messages:
    st.info("No history yet. Start a chat to see your history here.")
else:
    for i, message in enumerate(messages):
        role = "🧑 You" if message["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {message['content']}")
        st.divider()

    if st.button("Clear History"):
        st.session_state["messages"] = []
        st.rerun()
