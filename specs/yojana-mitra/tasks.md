# Task Breakdown: Yojana Mitra — Offline Government Scheme Intelligence (v1 / MVP)

Task List ID: TASK-001

Linked Plan: PLAN-001

Linked Spec: SPEC-001

Status: Draft

Authors: Akshaya Garela, Praveen Yadav

Created: 2026-06-28
---

## Legend

- `[ ]` Not started  `[~]` In progress  `[x]` Done  `[!]` Blocked
- **Layer** tags: `ui` | `pipeline` | `ingestion` | `structuring` |
  `embeddings` | `retrieval` | `llm` | `storage` | `test` | `infra`

---

## Phase 0 — Project Scaffolding

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T0.1 | Create full folder structure per architecture doc | infra | — | No | [ ] |
| T0.2 | Write `config.yaml` + `core/config.py` (model paths, thresholds, DB path) | infra | T0.1 | Yes | [ ] |
| T0.3 | Write `core/logging_setup.py` (local file logging only, no remote sinks) | infra | T0.1 | No | [ ] |
| T0.4 | Add import-linter rule enforcing `ui → pipeline → domain → storage` direction | infra | T0.1 | Yes | [ ] |
| T0.5 | Add static-import test asserting no network client (`requests`/`httpx`/`urllib`) inside `app/` | test | T0.1 | Yes | [ ] |
| T0.6 | Write `scripts/setup_models.sh` (one-time model download, isolated from `app/`) | infra | T0.1 | No | [ ] |

## Phase 1 — Storage Foundation

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T1.1 | Write `storage/migrations/001_init.sql` (documents, schemes, chunks, embeddings, chunks_fts, query_logs) | storage | T0.2 | Yes | [ ] |
| T1.2 | Write `storage/models.py` (ORM/dataclass definitions matching DDL) | storage | T1.1 | Yes | [ ] |
| T1.3 | Write `storage/db_manager.py` (connection handling, migration runner) | storage | T1.1 | Yes | [ ] |
| T1.4 | Write `storage/repository.py` (CRUD: documents, schemes, chunks, embeddings, query_logs) | storage | T1.2, T1.3 | Yes | [ ] |
| T1.5 | Unit tests: repository CRUD round trips on in-memory SQLite | test | T1.4 | — | [ ] |

## Phase 2 — Schema Contract

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T2.1 | Write `schemas/scheme_schema.json` (JSON Schema draft-07, v1.0) | structuring | — | Yes | [ ] |
| T2.2 | Write Pydantic models mirroring the JSON Schema | structuring | T2.1 | Yes | [ ] |
| T2.3 | Unit tests: valid/invalid payloads against schema | test | T2.2 | — | [ ] |

## Phase 3 — Ingestion

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T3.1 | Write `ingestion/file_loader.py` (type detection, checksum dedup — FR-15) | ingestion | T1.4 | Yes | [ ] |
| T3.2 | Write `ingestion/pdf_extractor.py` (native text layer via PyMuPDF) | ingestion | T3.1 | Yes | [ ] |
| T3.3 | Write `ingestion/preprocessor.py` (deskew, denoise, binarize) | ingestion | T3.1 | Yes | [ ] |
| T3.4 | Write `ingestion/ocr_engine.py` (PaddleOCR wrapper, local model paths only) | ingestion | T3.3 | Yes | [ ] |
| T3.5 | Write `ingestion/language_detector.py` (Hindi/English/regional script detection) | ingestion | T3.1 | Yes | [ ] |
| T3.6 | Integration test: native PDF → extracted text | test | T3.2 | — | [ ] |
| T3.7 | Integration test: scanned image → OCR text (sample low-quality scan) | test | T3.4 | — | [ ] |

## Phase 4 — Structuring

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T4.1 | Write `structuring/chunker.py` (layout-aware, by heading/section) | structuring | T3.6, T3.7 | Yes | [ ] |
| T4.2 | Write `structuring/scheme_parser.py` rule-based extraction path | structuring | T4.1 | Yes | [ ] |
| T4.3 | Write LLM-fallback extraction path in `scheme_parser.py` (depends on Phase 6 LLM wrapper existing as stub or real) | structuring | T4.2 | Yes | [ ] |
| T4.4 | Write `structuring/schema_validator.py` + repair/re-prompt loop (max 2 retries) | structuring | T2.2, T4.3 | Yes | [ ] |
| T4.5 | Write `structuring/normalizer.py` (dates, currency, eligibility text cleanup) | structuring | T4.4 | Yes | [ ] |
| T4.6 | Integration test: raw text → validated SchemeJSON end-to-end | test | T4.5 | — | [ ] |

## Phase 5 — Embeddings

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T5.1 | Write `embeddings/bge_encoder.py` (BGE-Small, local weights only) | embeddings | T0.2 | Yes | [ ] |
| T5.2 | Write `embeddings/embedding_cache.py` (avoid recomputation on unchanged chunks) | embeddings | T5.1 | Yes | [ ] |
| T5.3 | Benchmark: embedding latency per chunk vs. budget (§8 plan: <200ms) | test | T5.1 | — | [ ] |

## Phase 6 — Retrieval

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T6.1 | Write `retrieval/faiss_index.py` (build/load/save/add/search, start with `IndexFlatIP`) | retrieval | T5.1 | Yes | [ ] |
| T6.2 | Wire `chunks_fts` (FTS5) population alongside chunk inserts | retrieval | T1.4 | Yes | [ ] |
| T6.3 | Write `retrieval/hybrid_search.py` (BM25 + vector fusion/reranking) | retrieval | T6.1, T6.2 | Yes | [ ] |
| T6.4 | Write `retrieval/retriever.py` (top-k orchestration, confidence scoring for FR-10) | retrieval | T6.3 | Yes | [ ] |
| T6.5 | Benchmark: FAISS search latency at realistic scale (§8 plan: <500ms) | test | T6.1 | — | [ ] |

## Phase 7 — LLM & Guardrails

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T7.1 | Benchmark candidate GGUF models (3B vs 7B, Q4_K_M) on target CPU hardware | llm | T0.6 | — | [ ] |
| T7.2 | Write `llm/llama_cpp_engine.py` (load chosen model, local path only) | llm | T7.1 | Yes | [ ] |
| T7.3 | Write `llm/prompt_templates.py` (extraction prompt + QA prompt) | llm | T7.2 | Yes | [ ] |
| T7.4 | Write `llm/answer_generator.py` (RAG synthesis from retrieved chunks) | llm | T7.3, T6.4 | Yes | [ ] |
| T7.5 | Write `llm/guardrails.py` (grounding verification, refusal path for FR-10) | llm | T7.4 | Yes | [ ] |
| T7.6 | Calibrate `MIN_CONFIDENCE_THRESHOLD` against sample query set | llm | T7.5, T6.4 | Yes | [ ] |

## Phase 8 — Pipeline Orchestration

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T8.1 | Write `pipeline/ingestion_pipeline.py` (file → JSON → DB → index, full wiring) | pipeline | T4.6, T6.1 | Yes | [ ] |
| T8.2 | Write `pipeline/qa_pipeline.py` (query → retrieval → LLM → guardrails → log) | pipeline | T6.4, T7.5 | Yes | [ ] |
| T8.3 | Integration test: full ingest-then-query round trip on a real sample PDF | test | T8.1, T8.2 | — | [ ] |

## Phase 9 — Streamlit UI

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T9.1 | Write `ui/upload_page.py` (calls `pipeline.run_ingestion_pipeline` only) | ui | T8.1 | Manual QA | [ ] |
| T9.2 | Write `ui/chat_page.py` + `components/citation_card.py` | ui | T8.2 | Manual QA | [ ] |
| T9.3 | Write `ui/scheme_explorer.py` (browse/filter by category/state/ministry — FR-13) | ui | T1.4 | Manual QA | [ ] |
| T9.4 | Write `ui/admin_page.py` (reindex action — FR-12, model status, logs) | ui | T8.1 | Manual QA | [ ] |
| T9.5 | Write `main.py` entry point wiring all pages | ui | T9.1–T9.4 | Manual QA | [ ] |

## Phase 10 — Validation & Benchmarking

| # | Task | Layer | Depends On | Test Required? | Status |
|---|---|---|---|---|---|
| T10.1 | Assemble 20-document hand-labeled validation set (mixed native/scanned, English/Hindi) | test | — | — | [ ] |
| T10.2 | Run extraction accuracy measurement against validation set (target ≥85%) | test | T8.1, T10.1 | — | [ ] |
| T10.3 | Run full `scripts/benchmark_cpu.py` against performance budget table (plan.md §8) | infra | T8.1, T8.2 | — | [ ] |
| T10.4 | Re-verify Constitution compliance checklist end-to-end (no network calls observed at runtime, even with airplane mode) | infra | T9.5 | — | [ ] |

---

## Blocking Issues

| Issue | Raised On | Resolved? |
|---|---|---|
| — | — | — |

## Completion Checklist (mirrors plan.md §11 Definition of Done)

- [ ] All tasks above marked `[x]`
- [ ] No `[!]` blocked tasks remain
- [ ] Tests green (unit + integration)
- [ ] Constitution compliance re-verified post-implementation (T10.4)
- [ ] Spec acceptance criteria (SPEC-001 §7) manually verified against running app
- [ ] Extraction accuracy ≥ 85% confirmed (T10.2)
- [ ] Performance budget met or documented exception (T10.3)