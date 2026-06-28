# Yojana Mitra

Yojana Mitra is an AI-powered offline assistant that helps users understand government welfare schemes by answering specific questions from uploaded documents instead of displaying the entire document.

The application allows users to upload scheme PDFs or images, ask questions using text or voice, and receive concise, context-aware answers with references to the source document.

## Features

- Upload PDF documents
- Upload scanned images
- OCR for scanned documents
- Text-based question answering
- Voice-based question answering
- Offline Large Language Model (LLM)
- Retrieval-Augmented Generation (RAG)
- Multilingual support
- Source citation
- Low-resource device compatibility
- SQLite persistence for documents, schemes, chunks, queries, and cache
- Hybrid retrieval using SQLite FTS plus local embeddings/vector search
- Structured JSON extraction with schema validation

## Technology Stack

- Python
- Streamlit
- Ollama
- LangChain
- ChromaDB
- PyMuPDF
- EasyOCR
- Faster-Whisper
- Sentence Transformers

## Project Structure

```
yojana-mitra/
│
├── backend/                     # Backend Python package
│   ├── core/                    # Backend config and logging
│   ├── ingestion/               # Backend PDF/image loading and OCR
│   ├── structuring/             # Backend chunking and scheme JSON extraction
│   ├── embeddings/              # Backend local embeddings
│   ├── retrieval/               # Backend hybrid search
│   ├── llm/                     # Backend local LLM and guardrails
│   ├── pipeline/                # Backend entry points used by frontend
│   ├── speech/                  # Backend offline voice transcription
│   ├── localization/            # Backend language labels
│   └── storage/                 # Backend SQLite database layer
├── frontend/                    # Streamlit UI
├── schemas/
├── scripts/
├── data/
├── docs/
├── tests/
├── models/
├── config.yaml
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
├── USER_MANUAL.md
└── AGENTS.md
```

## Installation

```bash
git clone https://code.swecha.org/<username>/yojana-mitra.git

cd yojana-mitra

pip install -r requirements.txt
```

For the complete offline experience, place local model files under `models/`
as described by:

```bash
bash scripts/setup_models.sh
```

## Running

```bash
streamlit run frontend/app.py
```

## Backend

The backend lives in `backend/`. It handles document ingestion, OCR, structured
scheme extraction, SQLite storage, embeddings, retrieval, local LLM answering,
guardrails, caching, speech transcription, and localization support.

Backend pipeline functions are available for the frontend at:

- `backend.pipeline.ingestion_pipeline.run_ingestion_pipeline(file_path)`
- `backend.pipeline.qa_pipeline.run_qa_pipeline(question, document_id=None)`

## Testing

```bash
python3 -m pytest
python3 scripts/benchmark_cpu.py
```

## Team

- Akshaya Garela
- Project Partner

## License

This project is developed for educational and research purposes.
