# Implementation Plan: [FEATURE NAME]

Plan ID: PLAN-001

Linked Spec: SPEC-001 (specs/yojana-mitra/spec.md)

Status: Draft

Authors: Akshaya Garela, Praveen Yadav

Created: 2026-06-28

---

## 1. Constitution Check (MUST complete before design)

| Article | Constraint | How this plan satisfies it |
|---|---|---|
| I — Offline-First | No runtime network calls | |
| II — CPU-Only | Latency budget respected | |
| III — Data Sovereignty | Data stays under `data/` | |
| IV — Grounded Answers | Citations enforced, confidence threshold defined | |
| V — Schema Discipline | Validates against `scheme_schema.json` | |
| VII — Layered Architecture | Respects `ui → pipeline → domain → storage` | |
| VIII — Simplicity | No new infra introduced, or justified below | |

**Deviations (if any):** [Must be explicit. "None" if fully compliant.]

## 2. Technical Approach

[Narrative: how will this be built. Reference existing modules from the
architecture (ingestion/, structuring/, embeddings/, retrieval/, llm/,
storage/, app/ui/). State which modules are touched/created.]

## 3. Affected Modules

| Module | Change Type | Description |
|---|---|---|
| `app/ingestion/...` | New / Modified | |
| `app/structuring/...` | New / Modified | |
| `app/storage/...` | New / Modified | |

## 4. Data Model Changes

- **New tables / columns:** [list, or "None"]
- **Schema version bump?** [Yes → new version / No]
- **Migration script:** `storage/migrations/00X_description.sql`

## 5. Interfaces / Contracts

```
[Function signatures or internal "API" contracts this plan introduces,
 e.g.:
 def extract_eligibility(chunk_text: str) -> EligibilityModel: ...
]
```

## 6. Sequence of Work

1. [Step — what gets built first and why]
2. [Step]
3. [Step]

## 7. Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM produces malformed JSON | High | Medium | Schema validation + repair-prompt loop (Art. V) |
| OCR misreads regional script | Medium | High | Confidence score thresholding + manual review flag |
| FAISS index grows slow at scale | Low | Medium | Benchmark at N=10k chunks; switch to HNSW if needed |

## 8. Performance Budget

| Operation | Target (CPU, 8–16GB RAM) |
|---|---|
| OCR per page | |
| Embedding per chunk | |
| FAISS top-k search | |
| LLM answer generation | |
| End-to-end ingestion (per 10-page PDF) | |
| End-to-end Q&A turn | |

## 9. Testing Strategy

- **Unit tests:** [which modules, what's mocked]
- **Integration tests:** [pipeline-level, e.g. full ingest → query round trip]
- **Manual validation set:** [e.g., N sample govt scheme PDFs with hand-labeled expected JSON]

## 10. Rollout / Migration Notes

[How does this affect existing indexed data? Re-index required? Backward
compatible with old schema_version records?]

## 11. Definition of Done

- [ ] All FRs in linked spec satisfied
- [ ] Constitution check has no unresolved deviations
- [ ] Tests pass (unit + integration)
- [ ] Performance budget met or documented exception
- [ ] `tasks.md` generated and reviewed

---
*This plan feeds into `tasks.md`. Do not begin implementation until Status = Approved.*