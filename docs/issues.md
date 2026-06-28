## Issues — Backend / AI / Data Layer (Heavier Load)

| # | Issue | Estimate | Due Day |
|---|-------|----------|---------|
| 1 | Set up backend project structure, virtual environment, dependency management (requirements.txt), and config management (model paths, language settings, thresholds) | 3h | Day 1 |
| 2 | Build PDF text extraction module supporting both digital-text PDFs and mixed image-text PDFs, with fallback detection logic | 3h | Day 1 |
| 3 | Integrate PaddleOCR for image uploads (PNG/JPG/JPEG) and scanned PDFs; tune preprocessing (deskew, denoise, contrast) for low-quality brochure scans | 5h | Day 1 |
| 4 | Build text normalization layer to clean OCR artifacts, merge broken lines, and handle mixed-script (English + regional language) content | 3h | Day 1–2 |
| 5 | Design and implement the structured JSON extraction schema and the extraction logic that maps raw document text into scheme_name, department, state, eligibility, benefits, documents, dates, application_process, contact, summary | 6h | Day 2 |
| 6 | Build validation layer for extracted JSON (missing-field handling, type checks, default fallbacks like "Not specified in document") | 2h | Day 2 |
| 7 | Design SQLite schema (documents, extracted_fields, chunks, embeddings_meta, chat_history, cache) and write migration scripts | 3h | Day 2 |
| 8 | Implement full CRUD layer for all database tables with proper indexing for fast lookups | 3h | Day 2 |
| 9 | Build chunking strategy for extracted document text (size, overlap, section-aware splitting) | 2h | Day 2 |
| 10 | Generate local embeddings (MiniLM or BGE-small) for each chunk and persist them alongside metadata | 3h | Day 2–3 |
| 11 | Set up FAISS vector index, including index persistence to disk and reload-on-startup logic | 3h | Day 3 |
| 12 | Build semantic retrieval function: query embedding → top-k relevant chunk retrieval → relevance filtering | 3h | Day 3 |
| 13 | Integrate llama.cpp with a quantized GGUF model; build a reusable inference wrapper (load once, reuse across requests) | 4h | Day 3 |
| 14 | Build prompt templates for concise, scoped answers (age limit → just the number, documents → just the list, etc.) per question type | 4h | Day 3 |
| 15 | Build the full RAG pipeline connecting retrieval, prompt construction, LLM inference, and answer post-processing | 4h | Day 3 |
| 16 | Implement confidence scoring logic based on retrieval similarity scores and answer-context overlap | 3h | Day 3–4 |
| 17 | Implement explainability output (structured reasoning trace) for eligibility-style and reasoning-based questions | 3h | Day 4 |
| 18 | Implement hallucination guardrail: detect low-confidence/no-match cases and return the standard "not found in document" response instead of generating freely | 3h | Day 4 |
| 19 | Build response caching layer at the backend level (cache by document hash + normalized question) to avoid recomputation | 2h | Day 4 |
| 20 | Build and document all backend API endpoints (upload, process-status, ask, history, reset) with consistent request/response contracts for frontend consumption | 4h | Day 4 |
| 21 | Load-test and tune memory/CPU usage across OCR, embedding, and LLM inference stages; document benchmark numbers for the README | 3h | Day 4–5 |
| 22 | Write unit/integration tests for extraction accuracy, retrieval correctness, and guardrail behavior | 3h | Day 5 |

**Backend total: ~67h**

---

## Issues — Frontend / UI / Localization Layer (Fewer, Larger Issues)

| # | Issue | Estimate | Due Day |
|---|-------|----------|---------|
| 1 | Build the complete core screen suite — upload screen (drag-drop + validation for PDF/PNG/JPG/JPEG), processing/loading screen with real-time status feedback, and summary screen (short summary, key benefits, eligible beneficiaries) — as one connected flow wired to backend upload/process/status endpoints | 10h | Day 1–2 |
| 2 | Build the full conversational layer — chat interface with typed input, message history, confidence/explainability display per answer, plus complete offline voice integration (mic capture → Whisper.cpp speech-to-text, and offline TTS for voice output where feasible) across all three supported languages | 12h | Day 2–3 |
| 3 | Build the complete localization framework — runtime i18n system (not just translation files) covering UI labels, buttons, menus, error messages, and AI response wrapping for English, Telugu, and Hindi, with a persistent language toggle accessible from every screen | 8h | Day 3 |
| 4 | Build the remaining supporting screens and systems as one bundle — history page (past documents + past Q&A), settings page (language, model, theme, cache/database reset with confirmation dialogs), client-side response caching, and final integration testing against all backend endpoints | 9h | Day 4 |
| 5 | Produce all project packaging and documentation — README, installation guide, offline setup instructions, folder structure documentation, and screenshots/demo walkthrough for submission | 4h | Day 4–5 |

**Frontend total: ~43h**
