"""
Upload page: lets the user upload files for processing.
"""

import streamlit as st

st.title("📤 Upload")

st.write("Upload one or more files to get started.")

uploaded_files = st.file_uploader(
    "Choose file(s)",
    accept_multiple_files=True,
)

if uploaded_files:
    st.session_state["uploaded_files"] = uploaded_files
    st.success(f"Uploaded {len(uploaded_files)} file(s) successfully.")

    for file in uploaded_files:
        with st.expander(file.name):
            st.write(f"**Type:** {file.type}")
            st.write(f"**Size:** {file.size} bytes")

    if st.button("Continue to Processing →"):
        st.switch_page("pages/2_processing.py")
else:
    st.info("No files uploaded yet.")
