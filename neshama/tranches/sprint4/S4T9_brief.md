# Tranche S4T9 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## SLA (resolved 2026-09-17)

Suppression takes effect **synchronously** — the candidate is excluded from the very next read
through any pipeline stage. Hard deletion propagates and purges the underlying record within
**24 hours**. Set by the project owner; see `neshama/context/decisions.md` and
`neshama/plan/backlog.md`.

---

## Scope (REQUIRED)

Build the suppression/deletion pipeline (CR-10, C-1) on top of S1T1's `suppressed`/`deleted_at`
field.

- Accept a suppression request (temporary — candidate excluded from future results but record
  retained) and a deletion request (permanent — candidate removed and must not reappear) keyed
  by candidate identifier.
- Both requests must be recorded (who requested it, when, which kind) — reuse the audit-log
  mechanism from S1T1/S3T7 rather than inventing a second log.
- Suppression must be synchronous: the write call returns only after the candidate is excluded
  from `candidate_store.py` reads. Deletion may run through a background purge job but must
  complete within 24 hours; implement the 24-hour bound as an enforceable, testable property
  (e.g. a max-latency test against the purge job), not just a comment.
- CR-10 is explicit: **deletion must not be reversed by a subsequent crawl.** If a source
  adapter (S1T2's mock, or any future real adapter) returns a candidate matching a
  previously-deleted identifier, the deletion must win — write a re-suppression/re-deletion
  check into the candidate ingestion path, not just the initial write path.
- Suppressed/deleted candidates must already be excluded from reads per S1T1's store — confirm
  this still holds when reached through S3T6/S3T7/S4T8's full pipeline, not just the raw store.

---

## Manifesto (REQUIRED for mechanism-change tranches)

- **Failure evidence:** N/A — new capability.
- **Root cause:** Without an explicit re-ingestion guard, a subsequent adapter crawl (Sprint 5,
  once D-01 resolves) would silently resurrect a deleted candidate, violating CR-10 and C-1
  (candidates who have not consented to being indexed must be able to have deletion honored).
- **Targeted fix:** A deletion-tombstone check in the ingestion path plus an SLA-bounded
  propagation job.
- **Predicted impact:** Re-running the mock adapter's ingestion after a deletion, for the same
  candidate identifier, results in the candidate remaining absent from all read paths
  (raw store, S3T6 filter, S3T7 search, S4T8 shortlist).

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-10)
- neshama/context/decisions.md (D-04)
- neshama/context/assumptions.md (A-1)
- src/domain/candidate.py, src/storage/candidate_store.py (from S1T1 — must exist)
- src/adapters/mock_adapter.py, src/adapters/registry.py (from S1T2 — for the
      re-ingestion test)

---

## Outputs Expected (REQUIRED)

- `src/suppression/pipeline.py` — request handling + SLA-bounded propagation
- `src/suppression/tombstone.py` — the re-ingestion deletion guard
- `tests/suppression/test_pipeline.py`
- `tests/suppression/test_tombstone.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/suppression -v` — all pass, raw output pasted into completion report.
- A test proving a suppression request excludes the candidate from `candidate_store.py` reads
  immediately (synchronously), with no polling/wait needed in the test.
- A test proving a deletion request's underlying record purge completes within 24 hours of the
  request (simulate/advance time in the test rather than sleeping for real hours).
- A test proving a deletion request is permanent: re-running `MockSourceAdapter` ingestion for
  the same candidate identifier after deletion does not restore it to any read path.
- A test proving every suppression/deletion request is recorded (requester, timestamp, kind)
  in the audit-log mechanism.

---

## Forbidden Assumptions (REQUIRED)

- Do not invent a second audit/logging mechanism — extend S1T1's.
- Do not assume a real (non-mock) source adapter exists — test the re-ingestion guard against
  `MockSourceAdapter`.
- Do not build a recruiter-facing UI for submitting suppression/deletion requests — accept the
  request as a direct function call/API for this tranche; a UI is a later, unscoped tranche.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create a real (non-mock) source adapter here — that is Sprint 5's S5T10, even though
  D-01 is now resolved. This tranche only needs `MockSourceAdapter` for its re-ingestion test.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`

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

- Code + tests only.
- Completion report must restate the SLA (synchronous suppression, 24h deletion purge) and
  show the tests proving both are met.

---

## Notes

This is the tranche most directly tied to C-1 (candidates have not consented to being indexed).
The SLA and D-01 blockers noted in earlier drafts of this brief are resolved — see
`neshama/context/decisions.md`.

---

## PM Reminder: Dispatching to Worker

Present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint4/S4T9_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
