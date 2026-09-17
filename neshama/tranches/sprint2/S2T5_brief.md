# Tranche S2T5 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the recruiter-facing intake confirmation flow (CR-6, CR-7, C-4) on top of S2T4's draft
extraction and S1T3's schema. A CLI-based flow is sufficient for this tranche — do not build a
web UI unless a later tranche brief explicitly asks for one.

- Take a draft `RequirementSet` (from S2T4) and walk the recruiter through every field in
  Block A, presenting the extracted value (or the `NOT_FOUND_IN_JD` sentinel, rendered clearly
  as "not found — please provide") and letting them confirm or correct it.
- CR-6's hard rule: the flow must not allow proceeding to a "ready for search" state until
  every Block A field has been explicitly confirmed or corrected by the recruiter — reuse
  S1T3's `confirmed`/ready validator rather than re-implementing the check.
- Present Blocks B, C, D as well (review, not required to be exhaustive to complete — per
  CR-6 only Block A is gating), pre-filled per S2T4's output.
- Instrument the flow so a completion report can state elapsed wall-clock time for a sample
  run-through — this operationalizes C-4 (3–5 minute budget) as a measurable, not aspirational,
  property.
- On completion, persist the finished `RequirementSet` via S1T3's `requirement_store.py`.

---

## Manifesto (REQUIRED for mechanism-change tranches)

Manifesto: N/A (non-mechanism) — new capability, no prior mechanism.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-6, CR-7, full intake instrument table)
- neshama/context/decisions.md (D-05)
- neshama/context/assumptions.md (A-4)
- src/domain/requirement.py (from S1T3 — must exist)
- src/nlp/jd_extractor.py (from S2T4 — must exist)
- src/storage/requirement_store.py (from S1T3 — must exist)

---

## Outputs Expected (REQUIRED)

- `src/intake/confirmation_flow.py` — the CLI walkthrough
- `tests/intake/test_confirmation_flow.py`

---

## Acceptance Tests (REQUIRED)

- `pytest tests/intake -v` — all tests pass, raw output pasted into completion report.
- A scripted/non-interactive test proving the flow refuses to mark a `RequirementSet` ready
  while a Block A field is left as `NOT_FOUND_IN_JD` and uncorrected.
- A scripted test proving a fully-answered Block A (all fields confirmed or corrected) results
  in `confirmed=True` and a successful `requirement_store.py` write.
- A timed walkthrough using one of S2T4's fixture JDs, with elapsed time reported in the
  completion report as a data point against the 3–5 minute target (C-4). This is diagnostic,
  not a pass/fail gate — report the number honestly even if it exceeds the target.

---

## Forbidden Assumptions (REQUIRED)

- Do not build a web/GUI front end — CLI only for this tranche.
- Do not re-implement the "all Block A fields set" check — call S1T3's existing validator.
- Do not allow bypassing confirmation via a flag, env var, or "skip" shortcut — CR-6 has no
  exception path.
- Do not attempt to auto-correct or second-guess the recruiter's answers.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create anything under `src/matching/` — belongs to Sprint 3.
- Do NOT create a web server, HTTP routes, or a UI framework dependency — not scoped here.

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

If the timed walkthrough materially exceeds 3–5 minutes, flag it in the completion report as a
UX finding for `neshama/plan/issues.md` rather than silently shipping — per CLAUDE.md's
non-sprint-change rule, log it there if you act on it outside this tranche's scope.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint2/S2T5_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
