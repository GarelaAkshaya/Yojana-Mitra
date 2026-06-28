# AGENTS.md

This document describes the AI agents/modules used in Yojana Mitra.

---

# Agent 1 — Document Processing Agent

Responsibilities

- Read uploaded PDFs
- Read images
- Extract text
- Split text into chunks

Tools

- PyMuPDF
- EasyOCR

---

# Agent 2 — Embedding Agent

Responsibilities

- Convert text into embeddings
- Store embeddings

Tools

- Sentence Transformers
- ChromaDB

---

# Agent 3 — Retrieval Agent

Responsibilities

- Find the most relevant document chunks
- Return context for answering

Tools

- LangChain Retriever

---

# Agent 4 — Question Answering Agent

Responsibilities

- Accept user questions
- Generate concise answers
- Prevent hallucinations using retrieved context

Tools

- Ollama
- Mistral/Llama 3

---

# Agent 5 — Speech Agent

Responsibilities

- Convert voice to text

Tools

- Faster-Whisper

---

# Agent 6 — Translation Agent

Responsibilities

- Translate user questions
- Translate responses

Supported Languages

- English
- Telugu
- Hindi

---

## Design Principles

- Modular architecture
- Offline-first
- Secure processing
- No cloud dependency
- Easy to extend

---

## Future Agents

- Scheme Recommendation Agent
- Eligibility Prediction Agent
- Chat History Agent
- Analytics Agent