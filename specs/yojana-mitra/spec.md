# Feature Spec: Yojana Mitra — Offline Government Scheme Intelligence (v1 / MVP)

Spec ID: SPEC-001

Project: Yojana Mitra

Version: 1.0

Status: Draft

Authors: Akshaya Garela, Praveen Yadav

Created: 2026-06-28

---

## 1. Summary

Yojana Mitra is an offline-first, CPU-only desktop application that ingests
Government Scheme documents (PDFs and scanned images), converts them into
structured, schema-validated JSON records, indexes them for hybrid
semantic + keyword search, and lets a user ask natural-language questions
that are answered by a local LLM grounded strictly in the indexed corpus —
with no document, query, or model call ever leaving the device.

## 2. Problem Statement

Government scheme information in India is fragmented across PDFs, scanned
circulars, and regional-language notices, often with no searchable digital
form. Citizens and field officers in low-connectivity areas cannot rely on
cloud-based tools to check eligibility or benefits. There is no existing
tool that is simultaneously: (a) fully offline, (b) usable on
low-spec/no-GPU hardware, and (c) able to answer free-text eligibility
questions with traceable citations rather than hallucinated guesses.

## 3. Goals

- [ ] Ingest PDF and image files (scanned or native-text) of government
      scheme documents
- [ ] Extract structured fields (scheme name, eligibility, benefits,
      documents required, application process, deadline) into validated JSON
- [ ] Persist structured + raw data locally in SQLite
- [ ] Build a hybrid (vector + keyword) retrieval index over document chunks
- [ ] Answer free-text user questions using a local LLM, grounded in
      retrieved chunks, with citations to source document/page
- [ ] Provide a Streamlit UI for upload, chat Q&A, scheme browsing, and admin/reindex
- [ ] Operate entirely on CPU with no network calls at runtime

### Non-Goals (v1)

- Multi-user concurrent access / networked deployment
- Automatic crawling/scraping of government websites for new schemes
- Support for video/audio scheme announcements
- Fine-tuning or training any model (only inference with pre-trained/quantized models)
- Mobile app (Streamlit web UI, locally hosted, is the only client in v1)
- Multi-language UI chrome (document content may be multilingual; UI labels are English-only in v1)

## 4. User Stories

1. As a **citizen user**, I want to upload a scheme PDF and ask "Am I
   eligible for this scheme if my income is ₹2 lakh?", so that I get a
   direct grounded answer instead of reading the full document.
2. As a **field officer**, I want to bulk-upload scanned scheme circulars
   collected in the field, so that they become searchable without typing
   anything manually.
3. As a **field officer**, I want every answer to show which document and
   page it came from, so that I can verify it before advising a citizen.
4. As a **system admin**, I want to trigger a full re-index from the admin
   page, so that I can recover if the FAISS index becomes inconsistent
   with SQLite.
5. As a **citizen user**, I want to browse all ingested schemes by
   category/state even without asking a question, so that I can discover
   schemes I didn't know to ask about.

## 5. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | System must detect whether an uploaded PDF has a native text layer or requires OCR | Must |
| FR-2 | System must run PaddleOCR on scanned PDFs/images to extract raw text | Must |
| FR-3 | System must chunk extracted text in a layout-aware manner (by heading/section) | Must |
| FR-4 | System must extract structured fields via rule-based parsing first, falling back to local LLM extraction for ambiguous free-text fields | Must |
| FR-5 | System must validate all extracted JSON against `schemas/scheme_schema.json` before persisting | Must |
| FR-6 | System must store structured schemes, raw chunks, and document metadata in SQLite | Must |
| FR-7 | System must generate embeddings for each chunk using BGE-Small and store vectors in FAISS | Must |
| FR-8 | System must maintain a SQLite FTS5 keyword index in parallel with the FAISS vector index | Must |
| FR-9 | System must answer user questions by retrieving top-k chunks via hybrid search and passing them to the local LLM as grounding context | Must |
| FR-10 | System must refuse to answer (explicitly) when retrieval confidence is below threshold, rather than guessing | Must |
| FR-11 | System must display citations (document name, page number, scheme name) alongside every generated answer | Must |
| FR-12 | System must provide an admin action to fully rebuild the FAISS index from SQLite chunks | Should |
| FR-13 | System must allow browsing/filtering structured schemes by category, state, ministry | Should |
| FR-14 | System must log every query, retrieved chunk IDs, and generated answer for audit purposes | Should |
| FR-15 | System must detect document checksum to avoid duplicate re-ingestion of the same file | Could |

## 6. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Q&A response < 15s on 8GB RAM / 4-core CPU, no GPU |
| Performance | Per-page ingestion (OCR + structuring) < 30s on same hardware class |
| Offline guarantee | Zero runtime network calls — verified via static import audit of `app/` package (Constitution Art. I) |
| Accuracy | Structured field extraction accuracy ≥ 85% on a hand-labeled validation set of ≥ 20 real scheme documents before v1 is considered production-ready |
| Privacy | All uploaded files, derived JSON, embeddings, and logs remain under `data/` on local disk (Constitution Art. III) |
| Robustness | Malformed LLM JSON output triggers a repair/re-prompt loop, max 2 retries, then flags the scheme for manual review rather than silently storing bad data |

## 7. Acceptance Criteria

- [ ] Given a native-text PDF of a scheme, when uploaded, then a structured
      JSON record validating against `scheme_schema.json` is created and
      visible in Scheme Explorer within the performance budget.
- [ ] Given a scanned (image-only) PDF, when uploaded, then PaddleOCR
      extracts text and the same structuring pipeline produces a valid
      structured record.
- [ ] Given an ingested scheme, when a user asks an eligibility question
      in the chat UI, then the answer includes at least one citation
      pointing to the correct source document and page.
- [ ] Given a question whose answer is not present in any indexed
      document, when asked, then the system responds with an explicit
      "not enough information" message rather than a fabricated answer.
- [ ] Given the application is run with network access fully disabled at
      the OS level (after initial model setup), when any feature is used,
      then no feature fails due to a network error (because none is attempted).
- [ ] Given the admin page "Reindex All" action is triggered, when it
      completes, then FAISS index vector count matches SQLite chunk count.

## 8. Data Involved

- **Inputs:** PDF files (native or scanned), image files (JPG/PNG/TIFF) of
  scheme notices/circulars
- **Outputs:**
  - Structured JSON per scheme (per `schemas/scheme_schema.json`)
  - SQLite rows in `documents`, `schemes`, `chunks`, `embeddings`, `query_logs`
  - FAISS index files (`index.faiss`, `id_mapping.pkl`) under `data/faiss_store/`
- **Schema impact:** Establishes `schema_version: "1.0"` as the baseline;
  no prior schema exists (this is the first version)

## 9. Out of Scope / Future Considerations

- Multi-user/networked mode (would require revisiting Constitution Art.
  VIII simplicity stance — explicitly deferred, not assumed)
- Automated periodic re-crawling of official scheme portals (violates
  offline-first by definition unless made a manual, explicit, user-triggered
  "online update" mode in a future spec)
- On-device fine-tuning of the LLM or embedding model on corrected extraction data
- Voice input/output for low-literacy users

## 10. Open Questions

- [ ] Which exact LLM checkpoint (Mistral-7B-Instruct Q4_K_M vs. a smaller
      Indic-tuned 2–3B model) gives the best accuracy/latency tradeoff on
      target hardware? — to be resolved via benchmarking in `plan.md` §8.
- [ ] What confidence threshold (cosine similarity / fused score) should
      trigger the "not enough information" refusal in FR-10? — needs an
      initial value plus calibration plan.
- [ ] Should regional language UI labels be supported in v1.1, and if so,
      which languages first (Hindi is the obvious first candidate)?

## 11. Constitution Compliance Check

| Article | Compliant? | Notes |
|---|---|---|
| I — Offline-First | Yes | No HTTP client anywhere in `app/`; setup scripts isolated |
| II — CPU-Only | Yes | All models chosen specifically for CPU quantized inference |
| III — Data Sovereignty | Yes | All data under `data/`, no telemetry |
| IV — Grounded Answers | Yes | FR-9, FR-10, FR-11 directly enforce this |
| V — Schema Discipline | Yes | FR-5 mandates validation before persistence |
| VII — Layered Architecture | Yes | UI only calls `pipeline/`, per existing architecture |
| VIII — Simplicity | Yes | No new infra introduced beyond SQLite/FAISS/filesystem |

---
*This spec feeds into `plan.md`. Status = Approved → planning may begin.*