"""
Chat page: conversational interface with the assistant.
"""

import streamlit as st

from backend.pipeline.qa_pipeline import run_qa_pipeline
from backend.storage.repository import Repository

st.title("💬 Chat")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

processed_documents = st.session_state.get("processed_documents", [])
document_options = {
    f"{doc['scheme']['scheme_name']} ({doc['document_id']})": doc["document_id"]
    for doc in processed_documents
}

if not document_options:
    document_options = {
        f"{scheme['scheme_name']} ({scheme['document_id']})": scheme["document_id"]
        for scheme in Repository().list_schemes()
    }

selected_document_id = None
if document_options:
    selected_label = st.selectbox("Document", list(document_options.keys()))
    selected_document_id = document_options[selected_label]
else:
    st.warning("Upload and process a document before asking questions.")

# Display chat history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if selected_document_id is None:
        response = "Please upload and process a document first, then ask your question."
    else:
        with st.spinner("Searching the document..."):
            try:
                result = run_qa_pipeline(prompt, document_id=selected_document_id)
                response = result.answer or "I could not find this answer in the uploaded document."
                if result.citations:
                    sources = ", ".join(
                        f"{citation.get('document_name', 'document')} page {citation.get('page_number', 1)}"
                        for citation in result.citations[:3]
                    )
                    response = f"{response}\n\nSources: {sources}"
            except Exception as exc:
                response = f"Sorry, I could not answer that because processing failed: {exc}"

    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
