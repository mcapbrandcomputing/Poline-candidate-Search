# Tranche S1T2 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the source-adapter interface (CR-9) and exactly one reference implementation: a **mock
adapter** that returns synthetic, hard-coded `Candidate` records. No live network access, no
scraping, no HTTP calls to any real site.

- Define an abstract interface (e.g. `SourceAdapter`) with a method that returns candidate
  records already shaped so they can be passed to `Candidate` (from S1T1) — including a
  correctly populated `collection_basis`.
- The interface must be the *only* thing the rest of the system depends on to get candidates
  from a source — no adapter-specific types leak outside `src/adapters/`.
- Implement `MockSourceAdapter` that returns a small fixed set (5–10) of synthetic candidates
  with varied fields, useful as fixture data for Sprint 3's matching-engine tests.
- Adding or removing an adapter must require zero changes outside `src/adapters/` and the
  adapter registry — prove this in the completion report by pointing to the single
  registration point.

---

## Manifesto (REQUIRED for mechanism-change tranches)

Manifesto: N/A (non-mechanism) — new interface, no prior mechanism to compare against.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-9, CR-8)
- neshama/context/decisions.md (D-01)
- neshama/context/assumptions.md (A-3, A-7)
- src/domain/candidate.py (from S1T1 — must exist before this tranche starts)

> All links must resolve. If `src/domain/candidate.py` does not exist yet, this tranche is
> invalid — S1T1 must be ACCEPTED first.

---

## Outputs Expected (REQUIRED)

- `src/adapters/base.py` — the `SourceAdapter` interface
- `src/adapters/mock_adapter.py` — `MockSourceAdapter` implementation
- `src/adapters/registry.py` — the single point where adapters are registered/looked up
- `tests/adapters/test_base.py`
- `tests/adapters/test_mock_adapter.py`
- `tests/adapters/test_registry.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/adapters -v` — all tests pass, raw output pasted into completion report.
- A test proving every record `MockSourceAdapter` returns constructs successfully as a
  `Candidate` (i.e. passes S1T1's `collection_basis` validation) with no post-hoc patching.
- A test proving a second adapter can be registered without editing `base.py`,
  `mock_adapter.py`, or any file in `src/domain/`.

---

## Forbidden Assumptions (REQUIRED)

- Do not name or shape this adapter after any real site (LinkedIn, Indeed, etc.) — D-01 is
  unresolved. Keep it generic and synthetic.
- Do not make any real HTTP request, even to a test/sandbox endpoint.
- Do not implement rate-limiting, retry, or auth logic — out of scope until a real source is
  chosen (Sprint 5, gated on D-01).
- Do not modify `src/domain/candidate.py` from S1T1 — if the interface needs a change there,
  raise it via `tranche.question` instead of editing it directly.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create `src/domain/requirement.py` — belongs to S1T3.
- Do NOT create any file implementing a real (non-mock) source — belongs to Sprint 5, and
  only after D-01 is resolved.
- Do NOT create anything under `src/matching/` — belongs to Sprint 3.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`

> **Explicitly NOT allowed unless added above:** `pip install`, any network-capable command
> (`curl`, `wget`, browser automation), background processes, permission changes.

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

This is the only adapter this project will have until D-01 is resolved by a human decision
(see `neshama/context/decisions.md` and `neshama/plan/backlog.md`). Do not treat "the mock
works" as license to start a real adapter — that requires an explicit new tranche brief after
D-01 closes.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint1/S1T2_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
