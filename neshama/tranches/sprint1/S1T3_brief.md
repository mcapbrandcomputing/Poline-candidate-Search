# Tranche S1T3 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the typed requirement schema that the intake instrument (Sprint 2) will populate and the
matching engine (Sprint 3) will consume. This is CR-1's data model, not its execution engine.

- Define a `Requirement` record type with a `type` field constrained to `disqualifying` or
  `preferred` (CR-1) — no other value permitted.
- Define a `RequirementSet` record type (one per requisition/search) holding an ordered list
  of `Requirement`s plus the specific typed fields named in the intake instrument's Block A:
  `work_authorization`, `credentials[]`, `location_policy`, `worksite`, `geo_scope`,
  `comp_band`, `excluded_employers[]`. Blocks B/C/D fields (`role_outcomes`,
  `seat_history`, `prior_search_failure`, `scope_level`, `environment[]`,
  `positive_exemplars[]`, `negative_exemplar`, `source_companies[]`, `title_equivalents[]`,
  `experience_semantics`, `batch_size`, `ats_dedupe_policy`, `freshness_floor`) must also be
  represented as fields on `RequirementSet` — see `neshama/context/requirements.md` for the
  full field table. This tranche defines the *shape*; it does not implement the JD-extraction
  or confirmation UI that populates it (Sprint 2).
- Enforce at construction time: a `RequirementSet` cannot be marked "ready for search" (add a
  `confirmed: bool` or equivalent status) while any Block A field is unset/unconfirmed — this
  is the data-layer half of CR-6/CR-7; the UI flow enforcing it interactively is Sprint 2's job.
- Provide a persistence layer for `RequirementSet`, consistent in style with S1T1's
  `candidate_store.py` / `audit_store.py`.

---

## Manifesto (REQUIRED for mechanism-change tranches)

Manifesto: N/A (non-mechanism) — new schema, no prior mechanism.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-1, CR-2, CR-6, CR-7, and the full intake instrument table)
- neshama/context/decisions.md (D-03, D-05)
- neshama/context/glossary.md
- src/storage/candidate_store.py (from S1T1 — for storage-layer style consistency; must exist)

---

## Outputs Expected (REQUIRED)

- `src/domain/requirement.py` — `Requirement` and `RequirementSet` record types + the
  "ready for search" validator
- `src/storage/requirement_store.py` — write/read primitives
- `tests/domain/test_requirement.py`
- `tests/storage/test_requirement_store.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/domain/test_requirement.py tests/storage/test_requirement_store.py -v` — all
  pass, raw output pasted into completion report.
- A test proving `Requirement.type` rejects any value other than `disqualifying`/`preferred`.
- A test proving a `RequirementSet` cannot be marked ready/confirmed while any Block A field
  (`work_authorization`, `credentials`, `location_policy`, `worksite`, `geo_scope`,
  `comp_band`, `excluded_employers`) is unset.
- A test proving a `RequirementSet` CAN be marked ready when all Block A fields are set, even
  if some Block B/C/D fields are left empty (those are not disqualifying-gated per CR-6).

---

## Forbidden Assumptions (REQUIRED)

- Do not implement JD parsing/extraction — that is S2T4.
- Do not implement the confirmation UI/flow — that is S2T5.
- Do not implement the boolean filter *engine* that evaluates a `RequirementSet` against
  candidates — that is S3T6. This tranche only defines the data it will consume.
- Do not assume a specific UI framework, CLI, or API transport — this is a pure domain/storage
  layer.
- Do not hard-code example company names, exemplar names, or any real person's data into
  fixtures beyond generic placeholders (e.g. "Acme Corp", "Jane Example").

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create `src/nlp/` or any JD-extraction file — belongs to S2T4.
- Do NOT create anything under `src/intake/` (confirmation flow) — belongs to S2T5.
- Do NOT create anything under `src/matching/` — belongs to Sprint 3.

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
- One-line docstring per public class/function stating its contract.

---

## Notes

Field list is exhaustive per the source requirements doc — do not add fields beyond the Block
A–D table in `neshama/context/requirements.md`, and do not drop any of them.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint1/S1T3_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
