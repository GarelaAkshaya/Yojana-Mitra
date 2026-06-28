# Backend Package

This `backend/` directory is the backend for Yojana Mitra.

It contains the offline AI/data pipeline used by the Streamlit frontend:

- `pipeline/` - frontend-facing ingestion and question-answering functions
- `ingestion/` - file loading, PDF extraction, OCR, and language detection
- `structuring/` - text cleanup, chunking, scheme extraction, validation
- `storage/` - SQLite migrations, database manager, repository layer
- `embeddings/` - local embedding generation and cache support
- `retrieval/` - hybrid keyword/vector retrieval
- `llm/` - local llama.cpp wrapper, prompts, answer guardrails
- `speech/` - offline speech-to-text wrapper
- `localization/` - English, Hindi, and Telugu UI/backend labels
- `core/` - configuration and logging

The frontend should call only these backend entry points:

```python
from backend.pipeline.ingestion_pipeline import run_ingestion_pipeline
from backend.pipeline.qa_pipeline import run_qa_pipeline
```

The folder is named `backend` so it is visually separate from `frontend/` and clear for review.
