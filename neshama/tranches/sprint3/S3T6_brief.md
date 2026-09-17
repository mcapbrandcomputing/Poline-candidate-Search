# Tranche S3T6 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the boolean disqualifying-filter engine (CR-1, CR-2, D-03). Given a confirmed
`RequirementSet` and a pool of `Candidate` records, produce the surviving subset — candidates
who fail zero disqualifying requirements.

- Input: a confirmed `RequirementSet` (S1T3) and an iterable of `Candidate` records (S1T1,
  sourced via S1T2's adapter registry — use `MockSourceAdapter` for this tranche's tests).
- For each `Requirement` typed `disqualifying`, evaluate it as a boolean predicate against each
  candidate. A candidate failing *any* disqualifying requirement is excluded entirely — CR-1 is
  explicit that this must hold "at any position," so do not implement a "soft fail" or
  near-miss allowance.
- `Requirement`s typed `preferred` must NOT affect this tranche's output set membership — CR-2
  is explicit that semantic ranking (Sprint 3's other tranche, S3T7) only orders survivors, and
  this filter must not pre-emptively favor or exclude based on preferred requirements.
- Implement predicate logic for at minimum: `work_authorization`, `credentials[]`,
  `location_policy`/`worksite`, `geo_scope`, `comp_band`, `excluded_employers[]` — the same
  Block A fields S1T3 defined and S2T5 confirms. Where a candidate record lacks the data needed
  to evaluate a given predicate (e.g. no stated comp expectation), document the chosen
  fail-open vs. fail-closed behavior explicitly in the completion report — do not leave it
  implicit in the code.
- Output must be a plain filtered candidate list — no scores, no ordering guarantee (S3T7 owns
  ordering).

---

## Manifesto (REQUIRED for mechanism-change tranches)

- **Failure evidence:** N/A — new capability. Frame instead as an explicit prediction:
- **Root cause:** Without a boolean pre-filter, any similarity/ranking step would surface
  candidates who fail hard requirements (e.g. no work authorization), which CR-1 forbids at
  any position.
- **Targeted fix:** A pre-ranking boolean filter over disqualifying requirements only.
- **Predicted impact:** Given a realistic sparse-match fixture (see acceptance tests), the
  filter excludes every candidate that fails a disqualifying requirement and zero candidates
  that only fail a preferred one.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-1, CR-2)
- neshama/context/decisions.md (D-03)
- neshama/plan/project_plan.md (risk: "over-strict filters collapse result sets")
- src/domain/requirement.py (from S1T3 — must exist)
- src/domain/candidate.py (from S1T1 — must exist)
- src/adapters/mock_adapter.py (from S1T2 — must exist, used as test fixture source)

---

## Outputs Expected (REQUIRED)

- `src/matching/boolean_filter.py` — the filter engine
- `tests/matching/test_boolean_filter.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/matching/test_boolean_filter.py -v` — all pass, raw output pasted into
  completion report.
- A golden-path test: a `RequirementSet` and candidate pool where some candidates clearly pass
  and some clearly fail one disqualifying requirement each.
- A **realistic sparse-match test** (per `neshama/plan/project_plan.md`'s named risk): a
  `RequirementSet` with several disqualifying requirements simultaneously, run against a
  candidate pool where the surviving set is very small (1–2) or empty — proving the engine
  degrades gracefully (returns an empty list, does not error) rather than crashing.
- A test proving a candidate failing only a `preferred` requirement (never a `disqualifying`
  one) is NOT excluded by this filter.

---

## Forbidden Assumptions (REQUIRED)

- Do not implement semantic similarity, embeddings, or any ranking — that is S3T7.
- Do not implement the `reasons[]` array — that is S3T7.
- Do not silently treat missing candidate data as an automatic pass or automatic fail without
  documenting the choice — see Scope above.
- Do not assume a real (non-mock) candidate source is available — use `MockSourceAdapter`.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create `src/matching/semantic_ranker.py` or `src/matching/reasons.py` — belongs to S3T7.
- Do NOT create anything under `src/shortlist/` — belongs to S4T8.

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
- Completion report must explicitly state the fail-open/fail-closed choice for missing data,
  per predicate, in a short table.

---

## Notes

This is the tranche most likely to expose the "over-strict filters collapse results" risk
named in `neshama/plan/project_plan.md`. Report findings honestly even if they suggest the
schema (S1T3) or intake defaults (S2T4) need revisiting later — do not silently loosen a
predicate to make a test pass.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint3/S3T6_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
