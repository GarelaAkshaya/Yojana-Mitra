# Implementation Plan: Yojana Mitra — Offline Government Scheme Intelligence (v1 / MVP)

Plan ID: PLAN-001

Linked Spec: SPEC-001 (specs/yojana-mitra/spec.md)

Status: Draft

Authors: Akshaya Garela, Praveen Yadav

Created: 2026-06-28
---

## 1. Constitution Check (completed before design)

| Article | Constraint | How this plan satisfies it |
|---|---|---|
| I — Offline-First | No runtime network calls | `llm/`, `embeddings/`, `ingestion/ocr_engine.py` load models exclusively from local paths defined in `config.yaml`. `scripts/setup_models.sh` is the only file permitted to touch the network, and it lives outside `app/`. A static-import test (T-INFRA-1, see tasks.md) asserts no `requests`/`httpx`/`urllib` usage inside `app/`. |
| II — CPU-Only | Latency budget respected | Model shortlist restricted to GGUF Q4_K_M LLMs ≤ 7B params, BGE-Small (not Large), PaddleOCR mobile/server-CPU detection models. Benchmarks in §8 gate model selection. |
| III — Data Sovereignty | Data stays under `data/` | All `storage/` and `data/faiss_store/` paths are relative to project root, configured once in `config.py`; no temp-dir or system-wide cache usage for persistent data. |
| IV — Grounded Answers | Citations enforced, confidence threshold defined | `qa_pipeline.py` will hard-fail (return refusal message) if fused retrieval score < `MIN_CONFIDENCE_THRESHOLD` (default 0.35, calibrated in §8). `guardrails.py` performs a post-hoc check that every claim in the LLM answer can be traced to a retrieved chunk id before returning to UI. |
| V — Schema Discipline | Validates against `scheme_schema.json` | `schema_validator.py` runs Pydantic validation derived from the JSON Schema; failures trigger `scheme_parser.py` repair loop (max 2 retries) before flagging `status='failed'` in `documents` table. |
| VII — Layered Architecture | Respects `ui → pipeline → domain → storage` | Streamlit pages (`app/ui/*.py`) import only from `app/pipeline/`. Enforced by code review checklist + import-linter rule in CI (T-INFRA-2). |
| VIII — Simplicity | No new infra introduced | Confirmed: SQLite + FAISS + local filesystem only. No Redis/Postgres/message broker introduced for v1. |

**Deviations:** None.

## 2. Technical Approach

Build the system in four incremental layers, each independently testable,
matching the existing architecture document:

1. **Storage foundation** — SQLite schema + migrations + repository layer,
   since every other layer writes through this.
2. **Ingestion + Structuring** — file loading, OCR, PDF text extraction,
   chunking, hybrid rule/LLM field extraction, schema validation.
3. **Embedding + Retrieval** — BGE-Small encoding, FAISS index management,
   FTS5 keyword index, hybrid fusion/reranking.
4. **LLM Q&A + Guardrails + UI** — prompt templates, llama.cpp wrapper,
   grounding verification, Streamlit chat/upload/explorer/admin pages.

Each layer is built behind the same internal "API" contracts already
defined in the architecture doc (`ingest`, `structure`, `index`, `query`)
so that `pipeline/ingestion_pipeline.py` and `pipeline/qa_pipeline.py` can
be wired incrementally without rework.

## 3. Affected Modules

| Module | Change Type | Description |
|---|---|---|
| `app/storage/*` | New | SQLite models, migrations, repository CRUD |
| `app/ingestion/*` | New | File routing, OCR, PDF extraction, preprocessing |
| `app/structuring/*` | New | Chunking, hybrid extraction, validation, normalization |
| `app/embeddings/*` | New | BGE-Small wrapper, embedding cache |
| `app/retrieval/*` | New | FAISS index ops, hybrid search/rerank |
| `app/llm/*` | New | llama.cpp wrapper, prompts, answer generation, guardrails |
| `app/pipeline/*` | New | Ingestion + QA orchestrators |
| `app/ui/*` | New | Upload, chat, explorer, admin Streamlit pages |
| `schemas/scheme_schema.json` | New | JSON Schema v1.0 baseline |

## 4. Data Model Changes

- **New tables:** `documents`, `schemes`, `chunks`, `embeddings`,
  `chunks_fts` (virtual), `query_logs` — full DDL already defined in the
  architecture document; this plan adopts it as `storage/migrations/001_init.sql`.
- **Schema version bump?** N/A — this is the initial `schema_version: "1.0"`.
- **Migration script:** `storage/migrations/001_init.sql`

## 5. Interfaces / Contracts

```python
# ingestion
def load_file(file_path: str) -> DocumentRecord: ...
def extract_text(doc: DocumentRecord) -> RawTextResult: ...  # routes OCR vs native

# structuring
def chunk_text(raw_text: RawTextResult) -> list[Chunk]: ...
def extract_scheme_fields(chunks: list[Chunk]) -> SchemeDraft: ...
def validate_scheme(draft: SchemeDraft) -> SchemeValidated | ValidationError: ...

# embeddings
def encode_chunks(chunks: list[Chunk]) -> list[EmbeddingVector]: ...

# retrieval
def add_to_index(vectors: list[EmbeddingVector]) -> None: ...
def hybrid_search(query: str, k: int) -> list[RetrievedChunk]: ...

# llm
def generate_answer(query: str, context: list[RetrievedChunk]) -> GroundedAnswer: ...
def verify_grounding(answer: GroundedAnswer, context: list[RetrievedChunk]) -> bool: ...

# pipeline (the only layer app/ui is allowed to call)
def run_ingestion_pipeline(file_path: str) -> IngestionResult: ...
def run_qa_pipeline(user_query: str) -> QAResult: ...
```

## 6. Sequence of Work

1. Storage layer + migrations + repository (foundation everything writes to)
2. JSON Schema + Pydantic models (defines the contract structuring must hit)
3. Ingestion: file loader → PDF native extractor → OCR engine → preprocessor
4. Structuring: chunker → rule-based extractor → LLM-fallback extractor → validator → normalizer
5. Embeddings: BGE-Small wrapper + embedding cache
6. Retrieval: FAISS index build/load/search + FTS5 + hybrid fusion
7. LLM: llama.cpp wrapper + prompt templates + answer generator + guardrails
8. Pipeline orchestrators wiring all of the above
9. Streamlit UI: upload → chat → explorer → admin (in that order, since
   upload must work before chat has anything to query)
10. End-to-end benchmarking against performance budget (§8) and accuracy
    validation set (per spec NFR)

## 7. Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM produces malformed JSON during extraction | High | Medium | Schema validation + repair-prompt loop, max 2 retries, then manual-review flag (Constitution Art. V) |
| OCR misreads regional script / poor scan quality | Medium | High | Preprocessor (deskew/denoise/binarize) before OCR; confidence score stored per chunk; low-confidence chunks flagged in UI |
| FAISS index grows slow or memory-heavy at scale | Low | Medium | Start with `IndexFlatIP` (exact); benchmark at 10k/50k chunks; switch to `IndexHNSWFlat` if search latency exceeds budget |
| LLM hallucinates despite grounding context | Medium | High | `guardrails.py` grounding-verification step is mandatory (Constitution Art. IV); refusal path is a first-class UI state, not an error |
| 7B LLM too slow on low-end CPU (e.g., 4GB RAM devices) | Medium | High | Benchmark 3B vs 7B quantized models early (§8); document minimum supported hardware explicitly in README rather than silently degrading |
| Duplicate ingestion of the same document | Low | Low | Checksum-based dedup at `documents.checksum` (FR-15) |

## 8. Performance Budget

| Operation | Target (CPU, 8–16GB RAM, 4-core) |
|---|---|
| OCR per page (PaddleOCR) | < 5s |
| Native PDF text extraction per page | < 1s |
| Embedding per chunk (BGE-Small) | < 200ms |
| FAISS top-k search (≤ 50k chunks, Flat index) | < 500ms |
| LLM answer generation (Q4_K_M, 7B, ~300 token answer) | < 12s |
| End-to-end ingestion (10-page mixed PDF) | < 5 min |
| End-to-end Q&A turn (retrieval + generation) | < 15s |

*Benchmarking task (`scripts/benchmark_cpu.py`) must produce actual numbers
against this table before v1 is declared feature-complete — see tasks.md.*

## 9. Testing Strategy

- **Unit tests:** Each module in `ingestion/`, `structuring/`,
  `embeddings/`, `retrieval/`, `llm/` gets isolated tests with mocked model
  weights where feasible (e.g., test chunker logic without loading the
  real LLM).
- **Integration tests:** Full `ingestion_pipeline` round trip (sample PDF →
  validated JSON → SQLite → FAISS) and full `qa_pipeline` round trip
  (sample query → retrieval → grounded answer with citation).
- **Manual validation set:** Minimum 20 real/representative government
  scheme PDFs (mix of native-text and scanned, mix of English/Hindi),
  hand-labeled with expected structured fields, used to measure the ≥85%
  extraction accuracy NFR before declaring v1 production-ready.

## 10. Rollout / Migration Notes

This is a greenfield v1 — no prior schema or data exists. Migration
`001_init.sql` is the baseline. Any future schema change must ship as
`002_*.sql` and bump `schema_version` per Constitution Article V, never
as an edit to `001_init.sql`.

## 11. Definition of Done

- [ ] All FRs in SPEC-001 satisfied
- [ ] Constitution check has no unresolved deviations
- [ ] Unit + integration tests pass
- [ ] Performance budget (§8) met or documented exception with rationale
- [ ] Extraction accuracy ≥ 85% on the 20-document validation set
- [ ] `tasks.md` fully checked off with no blocked items

---
*This plan feeds into `tasks.md`. Status = Approved → task breakdown follows.*