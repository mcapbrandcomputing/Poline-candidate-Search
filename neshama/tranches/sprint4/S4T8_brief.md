# Tranche S4T8 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the recruiter-facing, non-ranked shortlist presentation (CR-4, CR-5) plus the Block D
search-behavior fields (`batch_size`, `ats_dedupe_policy`, `freshness_floor`). A CLI-rendered
output is sufficient — no web UI unless a later brief asks for one.

- Consume S3T7's `search.py` output (candidate list + `reasons[]`, already in non-ranked
  order) and render it to the recruiter: candidate identity, its `reasons[]` (each showing the
  requirement + evidence), and no numeric score, percentage, star rating, letter grade, or
  positional-fitness implication anywhere in the rendering (CR-4, CR-5 — re-verify this at the
  presentation layer even though S3T7 already enforces it at the data layer; defense in depth).
- Apply `batch_size` (from the `RequirementSet`) to determine how many candidates are shown per
  page/batch, if S3T7 did not already truncate — check S3T7's completion report for where
  truncation happens and do not duplicate it.
- Apply `ats_dedupe_policy` (`exclude` / `flag` / `include`): given a set of "already in ATS"
  candidate identifiers (accept this as a simple input — do not build an ATS integration),
  filter, flag, or pass through candidates accordingly.
- Apply `freshness_floor`: exclude candidates whose `Candidate.collected_at` (or an
  updated-at field, if S1T1 has one) is older than the recruiter-set threshold.
- Render explicitly labeled with the fact that this is a sourcing aid, not a recommendation
  (C-5) — a short, fixed disclaimer string is sufficient; do not word it as encouragement to
  hire/reject/advance/exclude anyone.

---

## Manifesto (REQUIRED for mechanism-change tranches)

- **Failure evidence:** N/A — new capability.
- **Root cause:** Without a dedicated presentation layer, there is no single place enforcing
  "never render a score" at the boundary the recruiter actually sees, and no shortlist could
  reflect `ats_dedupe_policy`/`freshness_floor`.
- **Targeted fix:** A rendering function that only accepts CR-4/CR-5-compliant inputs and
  applies Block D filtering.
- **Predicted impact:** Grepping this module's rendered output strings for any digit adjacent
  to "%", "score", "rank", "star", or similar finds nothing across the test fixtures.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-4, CR-5, Block D table)
- neshama/context/decisions.md (D-02)
- neshama/context/assumptions.md (A-5)
- src/matching/search.py (from S3T7 — must exist)

---

## Outputs Expected (REQUIRED)

- `src/shortlist/render.py` — the presentation function
- `src/shortlist/filters.py` — `ats_dedupe_policy` and `freshness_floor` application
- `tests/shortlist/test_render.py`
- `tests/shortlist/test_filters.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/shortlist -v` — all pass, raw output pasted into completion report.
- A test proving rendered output contains no score/percentage/rank/star/grade token for a
  fixture candidate set that has known internal scores in the audit log.
- A test proving `ats_dedupe_policy=exclude` removes matching candidates, `=flag` marks them
  without removing, `=include` passes them through unchanged.
- A test proving `freshness_floor` excludes a candidate whose `collected_at` predates the
  threshold and retains one that postdates it.
- A test proving `batch_size` is respected (exact count returned per batch, no duplication
  across sequential batches if pagination is implemented).

---

## Forbidden Assumptions (REQUIRED)

- Do not re-derive or re-expose the internal relevance score — S3T7 already keeps it out of
  the data this tranche consumes; do not add a new path that surfaces it.
- Do not build an actual ATS integration — accept ATS-membership as a plain input.
- Do not word the disclaimer or any UI copy as a recommendation to hire/reject/advance/exclude
  (C-5).
- Do not build a web front end unless explicitly asked in a later brief.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create anything under `src/suppression/` — belongs to S4T9.

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
- Completion report must include a sample rendered shortlist (raw text output) so a human can
  visually confirm no score/rank leaks through.

---

## Notes

This is the last engine-facing tranche before the product could, in principle, be demoed
end-to-end on the mock adapter. It does not require D-01 to be resolved.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint4/S4T8_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
