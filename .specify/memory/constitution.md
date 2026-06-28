# Yojana Mitra — Project Constitution

**Version:** 1.0.0
**Ratified:** 2026-06-28
**Status:** Active — binding on all specs, plans, and tasks in this repository

> This document defines the non-negotiable principles for Yojana Mitra.
> Every `spec.md`, `plan.md`, and `tasks.md` produced for this project MUST
> comply with these articles. Any deviation must be explicitly justified
> in a "Constitution Check" section of the plan, or the plan is invalid.

---

## Article I — Offline-First, Always

1. The application MUST function with zero network connectivity at runtime,
   for all core features (ingestion, structuring, embedding, retrieval, Q&A).
2. No feature may introduce a hard dependency on an external HTTP call,
   cloud API, or remote model endpoint. If a feature cannot be built without
   one, it is out of scope for this project, not an exception to this article.
3. The only acceptable network usage anywhere in the codebase is in
   one-time setup/install scripts (`scripts/setup_models.sh`) that download
   model weights *before* first offline run. This must be isolated from the
   `app/` runtime package — `app/` must never import a network client.
4. Every plan MUST include a "Network Boundary Check" confirming no new
   runtime network calls were introduced.

## Article II — CPU-Only Execution

1. All models (LLM, OCR, embeddings) MUST run on CPU with acceptable
   latency on commodity hardware (target: 8–16GB RAM, no discrete GPU).
2. Model selection MUST prefer quantized/distilled variants
   (e.g., GGUF Q4_K_M for LLM, "small"-tier embedding/OCR models) over
   larger variants, even at moderate accuracy cost, unless a measured
   benchmark proves the larger model is still within latency budget
   (defined per-feature in `plan.md`, default: < 15s per Q&A turn,
   < 30s per page ingestion).
3. GPU-specific code paths (CUDA, ROCm, MPS) MAY exist as optional
   acceleration but MUST NOT be required for any feature to function.

## Article III — Data Sovereignty & Privacy

1. User-uploaded documents, derived structured JSON, embeddings, and
   query logs MUST remain on local disk under `data/` at all times.
2. No telemetry, analytics, or crash-reporting SDK that phones home is
   permitted, even if anonymized, unless it is fully local
   (e.g., writes only to local log files).
3. Government scheme data and citizen query history are treated as
   sensitive by default. Any export feature must be explicit, user-initiated,
   and clearly labeled.

## Article IV — Grounded Answers Over Fluent Answers

1. The LLM MUST NOT answer user questions from parametric knowledge alone.
   Every answer in the Q&A flow MUST be grounded in retrieved chunks from
   the local corpus, with citations (doc_id, scheme_id, page_number).
2. If retrieval confidence is below the threshold defined in `plan.md`,
   the system MUST respond with an explicit "I don't have enough
   information in the indexed documents" rather than guessing.
3. Every structured extraction (PDF/image → JSON) MUST preserve a
   traceable `source` field linking back to the originating document
   and page. Untraceable structured data is treated as a defect.
4. A guardrails/grounding-verification step is mandatory in the Q&A
   pipeline and may not be removed for latency optimization without
   an explicit, documented exception in `plan.md`.

## Article V — Schema Discipline

1. All structured scheme data MUST validate against the JSON Schema in
   `schemas/scheme_schema.json` before being persisted to SQLite.
2. Schema changes MUST be versioned (`schema_version` field) and
   accompanied by a migration note in `tasks.md` — never silently
   altered in place.
3. Invalid LLM extraction output triggers a repair/re-prompt loop, not a
   silent fallback to unstructured storage.

## Article VI — Test-Before-Build Discipline (Spec-Driven Development)

1. No feature in `tasks.md` may be marked "in progress" without a
   corresponding entry in `spec.md` describing its user-facing behavior
   and acceptance criteria.
2. Every module boundary defined in the architecture (`ingestion`,
   `structuring`, `embeddings`, `retrieval`, `llm`, `storage`) MUST have
   at least one automated test before being considered "done."
3. Plans MUST be written before code. Tasks MUST be derived from plans.
   Code MUST be derived from tasks. Skipping a layer requires explicit
   justification recorded in `plan.md`.

## Article VII — Layered Architecture Integrity

1. The dependency direction is fixed: `app/ui` → `pipeline` → domain
   modules (`ingestion`, `structuring`, `embeddings`, `retrieval`, `llm`)
   → `storage`. Reverse or skip-level imports (e.g., `ui` importing
   `llm` directly) are constitutional violations and must be refactored,
   not grandfathered in.
2. Streamlit-specific code MUST stay inside `app/ui/`. No business logic
   (extraction, retrieval, prompting) may live in a Streamlit page file.

## Article VIII — Simplicity & YAGNI

1. Do not introduce a new dependency, service, or abstraction layer
   (message queues, microservices, container orchestration) unless a
   specific requirement in `spec.md` cannot be met without it.
2. Prefer SQLite + FAISS + filesystem over any added database/service
   for as long as the corpus size and single-user assumption hold
   (re-evaluate only if `spec.md` introduces multi-user/networked use).

## Article IX — Amendment Process

1. This constitution may be amended only by an explicit PR-style entry
   appended to this file under "Amendment Log" below, with rationale.
2. Amendments require the version number to be bumped
   (MAJOR for principle removal/reversal, MINOR for new article,
   PATCH for clarification wording).

---

## Amendment Log

| Version | Date | Change | Rationale |
|---|---|---|---|
| 1.0.0 | 2026-06-28 | Initial ratification | Establish offline-first, CPU-only, grounded-answer guarantees before any code is written |