# Tranche S1T1 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the candidate record schema and the audit-log substrate. This is pure data-layer work —
no scraping, no UI, no matching logic.

- Define a `Candidate` record type covering: profile fields needed for later matching
  (name, headline/title, current employer, location, stated skills/experience — kept generic,
  not source-specific) plus the mandatory provenance fields from CR-8: `source_url`,
  `source_name`, `collected_at`, `collection_basis` (enum: `licensed`, `public-permissible`,
  `candidate-submitted`).
- Enforce CR-8's hard rule in code: a record missing `collection_basis` must be rejected at
  the point of write, not filtered out later. Write a validation function/constructor that
  cannot construct a `Candidate` without it.
- Define an `AuditLogEntry` record type that can hold, per CR-11: a full requirement set
  (opaque reference to a requirement-set ID — the concrete requirement schema is S1T3's job,
  do not invent its shape here), the returned candidate ID set, the reasons shown, a
  timestamp, and a user identifier.
- Provide a minimal persistence layer (file-based or embedded DB — your choice, document it
  in the completion report) with write/read functions for both record types. No query engine,
  no API endpoints — this tranche is schema + storage primitives only.
- Provide a suppression/deletion marker field on `Candidate` (a boolean or status enum, e.g.
  `suppressed: bool`, `deleted_at: datetime | None`) so S4T9 has something to set. Do not
  implement the deletion *pipeline* itself — just the field and a storage-level guarantee
  that a deleted record is excluded from any read helper you write here.

---

## Manifesto (REQUIRED for mechanism-change tranches)

Manifesto: N/A (non-mechanism) — this is a new project, not a change to an existing mechanism.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-8, CR-9, CR-10, CR-11)
- neshama/context/decisions.md (D-01, D-04)
- neshama/context/assumptions.md (A-1, A-3, A-7)
- neshama/context/glossary.md

---

## Outputs Expected (REQUIRED)

- `src/domain/candidate.py` — `Candidate` record type + constructor/validator enforcing CR-8
- `src/domain/audit_log.py` — `AuditLogEntry` record type
- `src/storage/candidate_store.py` — write/read primitives, excludes deleted/suppressed records from reads
- `src/storage/audit_store.py` — append-only write/read primitives for audit entries
- `tests/domain/test_candidate.py`
- `tests/domain/test_audit_log.py`
- `tests/storage/test_candidate_store.py`
- `tests/storage/test_audit_store.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/domain tests/storage -v` — all tests pass, raw output pasted into completion report.
- A test proving a `Candidate` cannot be constructed/persisted without `collection_basis` set.
- A test proving a `Candidate` with `deleted_at` set (or `suppressed=True`) is excluded from
  the store's standard read/list function.
- A test proving `AuditLogEntry` writes are append-only (no update/delete function exists on
  `audit_store.py`, or an attempted mutation raises).

---

## Forbidden Assumptions (REQUIRED)

- Do not assume which source(s) candidates come from — D-01 is unresolved. No field, enum
  value, or comment should name LinkedIn, Indeed, or any specific site.
- Do not invent the requirement-set schema (typed disqualifying/preferred fields) — that is
  S1T3. Reference it only as an opaque ID.
- Do not implement the boolean filter engine, semantic ranking, or reasons generation — that
  is Sprint 3.
- Do not implement a suppression/deletion API or SLA enforcement — that is S4T9. This tranche
  only adds the field the later pipeline will set.
- No mock data source, no live network calls, no scraping code of any kind.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create `src/domain/requirement.py` or any requirement-schema file — belongs to S1T3.
- Do NOT create `src/adapters/` (source adapter interface) — belongs to S1T2.
- Do NOT create any file under `src/matching/` — belongs to Sprint 3.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`
- Package management: none — if a dependency beyond the Python standard library is needed
  (e.g. `pydantic`), ask via `tranche.question` before adding it.

> **Explicitly NOT allowed unless added above:** `pip install`, background processes,
> permission changes.

---

## Questions for PM

The worker may append clarification questions here before starting work.

---

## Completion Gate (MANDATORY)

See the Worker KICKSTART_PROMPT for full completion requirements.
Tests must be run locally with raw output pasted into the Completion Report.

---

## Delivery Format

- Code + tests only. No speculative documentation beyond docstrings.
- Every public function/class needs a one-line docstring stating its contract, not its
  implementation.

---

## Notes

This tranche is deliberately storage-only so it does not depend on D-01 being resolved. See
`neshama/context/decisions.md` — D-01 is a Position, not a Decision, and Sprint 5 (the first
live source adapter) is the only sprint gated on it.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint1/S1T1_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
