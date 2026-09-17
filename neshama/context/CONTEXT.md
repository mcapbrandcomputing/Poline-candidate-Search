# Project Context

> Living project memory — tables and bullets only, no prose paragraphs.
> Keep under ~120 lines. Update via context-update agent after accepted tranches.

## Status

| Item | Value |
|---|---|
| Current sprint | Sprint 5 — first live source adapter (LinkedIn) |
| Active tranche | S5T10 — DRAFT, not yet implemented |
| Blocking issues | none |

## Open Work

| Sprint | Tranches | Status |
|---|---|---|
| Sprint 1 | S1T1, S1T2, S1T3 | ACCEPTED — 43 tests passing |
| Sprint 2 | S2T4, S2T5 | ACCEPTED — 14 tests passing |
| Sprint 3 | S3T6, S3T7 | ACCEPTED — 20 tests passing |
| Sprint 4 | S4T8, S4T9 | ACCEPTED — 19 tests passing |
| Sprint 5 | S5T10 (LinkedIn adapter) | DRAFT — not yet dispatched/implemented |

Full pipeline (JD text -> extraction -> confirmation -> boolean filter -> semantic rank ->
reasons -> shortlist render -> suppression/deletion) is implemented and tested end-to-end
against `MockSourceAdapter`. 96/96 tests passing as of 2026-09-17
(`.venv/bin/python -m pytest tests/ -v`). Only the real (LinkedIn) source adapter remains.

## Key Decisions

| ID | Summary | Status |
|---|---|---|
| D-01 | Personal-use tool: direct scraping (incl. LinkedIn) in scope; legal/buyer-review posture N/A | DECIDED (revised 2026-09-17) |
| D-02 | Reasons array, not scores; no ranking shown to recruiter | DECIDED |
| D-03 | Boolean disqualifying filters before semantic ranking | DECIDED |
| D-04 | v1 buyer = in-house TA, mid-size; ATS-bound output, no contact enrichment | DECIDED |
| D-05 | JD is a seed; recruiter must confirm every disqualifying requirement | DECIDED |

Full rationale: `neshama/context/decisions.md`. Full requirement text: `neshama/context/requirements.md`.
Known gaps tracked in `neshama/plan/backlog.md`: Candidate schema has no work_authorization/
comp_band/geo fields (those predicates fail-open in `src/matching/boolean_filter.py`).
