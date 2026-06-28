"""
Processing page: shows progress/status while uploaded files are processed.
"""

import time

import streamlit as st

st.title("⚙️ Processing")

uploaded_files = st.session_state.get("uploaded_files")

if not uploaded_files:
    st.warning("No files found. Please upload files first.")
    if st.button("← Go to Upload"):
        st.switch_page("pages/1_upload.py")
else:
    st.write(f"Processing {len(uploaded_files)} file(s)...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, file in enumerate(uploaded_files):
        status_text.text(f"Processing: {file.name}")
        # Placeholder for real processing logic
        time.sleep(0.3)
        progress_bar.progress((i + 1) / len(uploaded_files))

    st.session_state["processing_done"] = True
    st.success("Processing complete!")

    if st.button("Continue to Chat →"):
        st.switch_page("pages/3_chat.py")
