Work-Division Plan
Akshaya — AI/ML + Data Layer

Owns everything that touches the document → structured data → answer pipeline.

OCR integration (PaddleOCR) + PDF text extraction
Structured JSON extraction logic (scheme name, eligibility, benefits, dates, etc.)
Embeddings generation + local vector store (FAISS/sqlite-vec)
Local LLM setup (llama.cpp + GGUF model) + RAG retrieval + QA logic
Confidence score + "explainable AI" reasoning (eligibility checks like income/age)
SQLite schema design + DB write/read for structured data

Praveen — Frontend/UI + Integration

Owns everything the user sees and the glue that holds the app together.

UI screens: Upload, Processing, Chat, History, Settings (Streamlit or React)
Localization (English/Telugu/Hindi) — UI strings, language toggle
Offline voice input (Whisper.cpp integration) + voice output if feasible
Caching layer, error/graceful-failure handling, loading states
Packaging (folder structure, requirements.txt, model download scripts)
README, architecture diagrams, demo prep, testing