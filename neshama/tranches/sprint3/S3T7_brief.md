# Tranche S3T7 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build semantic ranking over S3T6's survivors, plus the `reasons[]` array generation (CR-2,
CR-3, D-02, D-03).

- Input: the candidate list surviving S3T6's boolean filter, plus the full `RequirementSet`
  (both disqualifying and preferred requirements, plus Block B/C free-text/exemplar fields —
  `role_outcomes`, `positive_exemplars[]`, `negative_exemplar`, `source_companies[]`,
  `title_equivalents[]`, `experience_semantics`).
- Compute an internal relevance score per candidate (CR-4: "internal relevance scores are
  computed and written to an audit log ... and retained"). This tranche must write those scores
  to the `AuditLogEntry` mechanism from S1T1 — do not invent a separate scoring log.
- CR-2 is explicit: this step orders the survivor set, it does not add to it. The output
  candidate set must be identical (same members) to S3T6's input set, only reordered.
- CR-4/CR-5 are explicit: **the score itself, and any derived rank number, percentage, star
  rating, or letter grade, must never appear in any value this function returns to a caller
  that might render it to a recruiter.** The public return type should carry the reordered
  candidate list and the `reasons[]` array only — keep the raw score internal to the
  audit-logging path.
- Build `reasons[]` per CR-3: each candidate's reasons array must have one element per intake
  requirement it satisfies, each naming the requirement and the specific profile evidence. A
  candidate with zero populated reasons must not be returned (CR-3) — drop it from the final
  output entirely, do not return it with an empty reasons array.
- Output order: CR-5 requires the recruiter-facing order to be *stable and non-ranked*
  (alphabetical or most-recently-updated) — so this tranche's semantic ranking exists only to
  decide the audit-logged internal score and to decide truncation when a batch size is applied
  (Block D `batch_size`, consumed here or by S4T8 — your choice, document it); it must NOT
  determine the order handed to S4T8's shortlist UI. Re-sort the final output by name or
  `collected_at`/updated-at before returning, and document this explicitly in the completion
  report so S4T8's author does not need to re-derive it.

---

## Manifesto (REQUIRED for mechanism-change tranches)

- **Failure evidence:** N/A — new capability.
- **Root cause:** Without CR-3's evidence-per-requirement reasoning, a recruiter cannot defend
  a shortlist decision, and without CR-4/CR-5's suppression of scores, the product becomes an
  automated employment decision tool it is not designed or reviewed to be.
- **Targeted fix:** Semantic ranking confined to internal audit logging; public output carries
  only a non-ranked candidate list plus evidence-backed reasons.
- **Predicted impact:** No caller of this module's public function can obtain a numeric score
  or rank without deliberately reading the audit log — this is falsifiable by grepping the
  function's return type/signature for any score/rank field.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-2, CR-3, CR-4, CR-5)
- neshama/context/decisions.md (D-02, D-03)
- neshama/context/assumptions.md (A-5)
- src/matching/boolean_filter.py (from S3T6 — must exist)
- src/domain/audit_log.py, src/storage/audit_store.py (from S1T1 — must exist)

---

## Outputs Expected (REQUIRED)

- `src/matching/semantic_ranker.py` — internal scoring (writes to audit log via S1T1's
  `audit_store.py`)
- `src/matching/reasons.py` — `reasons[]` generation
- `src/matching/search.py` — the orchestration function tying S3T6 + this tranche together,
  whose public return type is documented to carry no score/rank field
- `tests/matching/test_semantic_ranker.py`
- `tests/matching/test_reasons.py`
- `tests/matching/test_search.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/matching/test_semantic_ranker.py tests/matching/test_reasons.py tests/matching/test_search.py -v`
  — all pass, raw output pasted into completion report.
- A test proving `search.py`'s public return type/object contains no numeric score, percentage,
  rank, or grade field reachable without going through the audit log.
- A test proving the audit log (via `audit_store.py`) receives a written entry containing the
  internal score for the query + candidate set.
- A test proving a candidate with zero populated `reasons[]` elements is absent from the final
  output (not present with an empty array).
- A test proving the final output candidate *set* (membership) is unchanged from S3T6's input,
  and the final output *order* is alphabetical or by updated-at — not by internal score.

---

## Forbidden Assumptions (REQUIRED)

- Do not expose the internal relevance score, or any rank derived from it, in any
  recruiter-facing return value — CR-4/CR-5 are absolute on this point.
- Do not re-implement the boolean filter — call S3T6's function.
- Do not build the shortlist UI — that is S4T8.
- Do not assume any particular embedding/similarity library is pre-installed; if one is
  needed, ask via `tranche.question` before adding a dependency.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create anything under `src/shortlist/` — belongs to S4T8.
- Do NOT create anything under `src/suppression/` or deletion-pipeline code — belongs to S4T9.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`

> **Explicitly NOT allowed unless added above:** `pip install` (ask first if an embedding
> library is genuinely needed), background processes, permission changes.

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
- Completion report must explicitly document: (1) where `batch_size` truncation happens, (2)
  the recruiter-facing sort key used instead of score.

---

## Notes

CR-4/CR-5 are the two requirements a reviewer/security questionnaire will check first (C-2).
Treat "no score leaks to the recruiter-facing output" as the single most important acceptance
criterion in this tranche.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint3/S3T7_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
