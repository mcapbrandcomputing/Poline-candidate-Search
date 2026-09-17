# Tranche S2T4 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the JD-to-draft-`RequirementSet` extraction engine (CR-6, CR-7, D-05). Given raw JD text,
produce a `RequirementSet` (from S1T3) with fields pre-populated where the JD supports it, and
an explicit "not found in JD" marker where it does not — CR-7 forbids silently leaving a field
blank with no distinction from "the JD said nothing here."

- Input: raw JD text (string).
- Output: a draft `RequirementSet` instance (not yet `confirmed`) with every Block A–D field
  either populated with an extracted value or explicitly marked `NOT_FOUND_IN_JD` (use a
  sentinel, not `None`/empty-string, so the confirmation UI in S2T5 can render it distinctly).
- For Block A specifically, extract every requirement-shaped sentence from the JD as a
  candidate `Requirement`, defaulting `type` to `disqualifying` (JDs bury real requirements
  among boilerplate — CR-1's note that "JDs list ten, usually two are real" means the *default*
  should force a human decision, not silently classify as `preferred`). Do not attempt to
  guess which ones are "really" disqualifying — that judgment belongs to the recruiter in S2T5.
- No ML/LLM call is required to satisfy this brief — deterministic rule/heuristic extraction
  (keyword and pattern matching for years-of-experience, location phrases, degree/certification
  mentions, etc.) is sufficient. If you use an external NLP library, document exactly which one
  and why in the completion report; do not add a network-dependent extraction step.

---

## Manifesto (REQUIRED for mechanism-change tranches)

Manifesto: N/A (non-mechanism) — new capability, no prior mechanism.

---

## Inputs to Read (REQUIRED)

- neshama/context/requirements.md (CR-6, CR-7, full intake instrument table)
- neshama/context/decisions.md (D-05)
- neshama/context/assumptions.md (A-4)
- src/domain/requirement.py (from S1T3 — must exist)

---

## Outputs Expected (REQUIRED)

- `src/nlp/jd_extractor.py` — the extraction function/class

> Note (added after S1T3 completed): `NOT_FOUND_IN_JD` already exists in
> `src/domain/requirement.py` — import it from there rather than creating a separate
> `src/nlp/sentinels.py`, per S1T3's completion report.
- `tests/nlp/test_jd_extractor.py`
- `tests/fixtures/sample_jds/` — at least 3 realistic sample JD text fixtures used by tests
  (a technical role, a non-technical role, and a sparse/poorly-written JD)

---

## Acceptance Tests (REQUIRED)

- `pytest tests/nlp -v` — all tests pass, raw output pasted into completion report.
- A test proving every Block A field is either populated or explicitly `NOT_FOUND_IN_JD` —
  never `None`/empty/absent — for all 3 fixture JDs.
- A test proving extracted requirements default to `type=disqualifying`.
- A test proving the sparse/poorly-written fixture JD still produces a valid draft
  `RequirementSet` (does not crash, does not silently drop the confirmation-required shape).

---

## Forbidden Assumptions (REQUIRED)

- Do not mark the resulting `RequirementSet` as `confirmed`/ready-for-search — extraction
  output is always a draft. Only the confirmation flow (S2T5) may set that flag.
- Do not call out to a network-based NLP/LLM service. Keep extraction local and deterministic.
- Do not silently default any field to a guessed value where the JD is actually silent — use
  the sentinel.
- Do not build the confirmation UI itself — that is S2T5.

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

- Do NOT create anything under `src/intake/` (confirmation flow) — belongs to S2T5.
- Do NOT create anything under `src/matching/` — belongs to Sprint 3.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`

> **Explicitly NOT allowed unless added above:** `pip install` (ask via `tranche.question`
> first if a parsing library is genuinely needed), any network-capable command, background
> processes, permission changes.

---

## Questions for PM

The worker may append clarification questions here before starting work.

---

## Completion Gate (MANDATORY)

See the Worker KICKSTART_PROMPT for full completion requirements.
Tests must be run locally with raw output pasted into the Completion Report.

---

## Delivery Format

- Code + tests + the 3 fixture files.
- One-line docstring per public class/function stating its contract.

---

## Notes

C-4 (3–5 minute intake budget) is a UX constraint on S2T5, not on this tranche — but a
poor extraction here (too many `NOT_FOUND_IN_JD` markers, wrong requirement defaults) directly
inflates the confirmation flow's completion time. Extraction quality on the sparse-JD fixture
is a leading indicator worth flagging in the completion report even though it isn't a hard gate.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint2/S2T4_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
