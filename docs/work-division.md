
## Work Division Plan

### Overview

This project splits cleanly along the backend/AI axis versus the frontend/UI axis, but the split is intentionally weighted so that the backend, AI/ML, data, and retrieval intelligence — which form the actual technical core and differentiator of this hackathon submission — sit with Akshaya, while the presentation, interaction, and integration layer sits with Praveen. The reasoning behind this weighting is that judges in an AI hackathon are primarily scoring model performance, resource efficiency, offline resiliency, and structured data extraction quality — all of which live in the backend/AI layer. The frontend's job is to make that intelligence visible and usable, which is a smaller but still essential slice of the total effort.

### Akshaya's Scope (Backend, AI/ML, Data & Retrieval Layer)

Akshaya owns the entire pipeline from the moment a file lands on disk to the moment a structured, trustworthy answer is ready to be displayed. This includes:

- **Document ingestion layer**: handling raw PDF and image uploads, validating file types, routing scanned vs. digital documents differently.
- **OCR subsystem**: integrating PaddleOCR for scanned brochures and images, tuning it for Indian government document layouts (multi-column text, stamps, letterheads, regional scripts mixed with English).
- **Text normalization and cleanup**: stripping OCR noise, fixing line-break artifacts, handling mixed-language text blocks.
- **Structured extraction engine**: designing the prompting/parsing strategy that takes raw extracted text and reliably produces the fixed JSON schema (scheme name, department, eligibility, benefits, documents, dates, contact, etc.) without hallucination.
- **Database layer**: full SQLite schema design, migrations, and CRUD operations for documents, structured fields, chat history, and cache entries.
- **Embeddings + chunking**: deciding chunk size/overlap strategy per document type, generating embeddings locally (MiniLM/BGE-small), and managing the embedding lifecycle (create, update, invalidate).
- **Vector search**: setting up FAISS, building the retrieval logic that pulls only relevant chunks instead of the whole document.
- **Local LLM integration**: wiring up llama.cpp with a quantized GGUF model, managing context windows, and writing the inference wrapper used by every downstream feature.
- **RAG orchestration**: the full retrieve → rank → construct-prompt → generate → post-process pipeline.
- **Explainability and confidence scoring**: building the logic that produces a reasoning trace (e.g., "Eligible — income below ₹2 lakh, age within range") rather than a bare answer.
- **Anti-hallucination guardrails**: detecting when retrieved context doesn't support an answer and returning the "not found in document" fallback instead of guessing.
- **API layer**: exposing all of the above as clean endpoints (`/upload`, `/process`, `/ask`, `/history`, `/status`) that the frontend can consume without needing to know any internal pipeline details.
- **Performance tuning**: making sure OCR, embedding generation, and LLM inference all run within reasonable CPU/RAM budgets, and that nothing blocks the main thread for too long.



### Praveen's Scope (Frontend, UI/UX, Localization & Integration)

Praveen owns translating Akshaya's backend capabilities into something a non-technical government-scheme applicant can actually use. This includes:

- **Full screen suite**: upload screen, processing/loading screen, summary screen, chat screen, history screen, and settings screen — built as one cohesive flow rather than disconnected pages.
- **Voice subsystem integration**: wiring microphone capture into Whisper.cpp for offline speech-to-text, and where feasible, offline TTS for voice output, across all three supported languages.
- **Localization framework**: building the i18n system itself (not just translation files) so every label, button, error message, and AI response is dynamically swapped between English, Telugu, and Hindi at runtime.
- **State and caching on the client side**: making sure repeated questions or repeated document views don't trigger unnecessary backend calls.
- **Settings and persistence**: language preference, theme, model selection, and destructive actions like cache/database reset, all with proper confirmation flows.
- **Packaging and documentation**: README, installation guide, offline setup instructions, and folder structure documentation, since this is what judges will read before they even open the app.




