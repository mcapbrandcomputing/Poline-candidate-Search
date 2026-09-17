# Tranche S5T10 - BRIEF

Status: ACCEPTED
Owner: PM
Created: 2026-09-17

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Build the first real (non-mock) source adapter: a LinkedIn profile scraper, implementing S1T2's
`SourceAdapter` interface. D-01 is resolved for this personal-use, single-user build — direct
scraping is in scope; see `neshama/context/decisions.md`.

- Implement `LinkedInAdapter(SourceAdapter)` in `src/adapters/linkedin_adapter.py`, registered
  through S1T2's `registry.py` alongside (not replacing) `MockSourceAdapter`.
- Given a search input (e.g. a set of keywords/titles derived from a `RequirementSet`'s
  `source_companies[]`, `title_equivalents[]`, and free-text fields), retrieve candidate
  profile data and construct valid `Candidate` records (S1T1) with `collection_basis` set to
  `personal-use-scrape` (added to the enum in S1T3/S1T1 — extend it there if not already
  present, via a small follow-up to that file, and note the change in
  `neshama/plan/issues.md` per CLAUDE.md's non-sprint-change rule if S1T1 is already ACCEPTED).
- Populate `source_url`, `source_name="linkedin"`, and `collected_at` for every record — CR-8's
  validation (from S1T1) must still reject any record missing these.
- Session/auth handling: use the owner's own logged-in browser session or credentials — do not
  hard-code credentials in source files. Read any required session token/cookie from an
  environment variable or a local, git-ignored config file. Document the exact variable/file
  name in the completion report.
- Respect basic self-throttling (a request-rate cap and randomized delay) — this is for the
  owner's own account stability, not a legal requirement in this personal-use context. A fixed,
  documented rate (e.g. "no more than N requests per minute") is sufficient; no need for
  circuit-breakers or backoff sophistication beyond that.
- Handle structural breakage gracefully (C-3 still applies even outside the legal context — a
  markup change should raise a clear, typed error, not corrupt partial data into the store).

---

## Manifesto (REQUIRED for mechanism-change tranches)

- **Failure evidence:** N/A — new capability, first real adapter.
- **Root cause:** `MockSourceAdapter` (S1T2) proves the interface but returns no real
  candidates — the tool cannot do its actual job (source real people from LinkedIn) without
  this tranche.
- **Targeted fix:** A `SourceAdapter` implementation backed by real LinkedIn scraping, isolated
  behind the existing interface so S3T6/S3T7/S4T8 need zero changes to consume it.
- **Predicted impact:** Running a search end-to-end (S2T5 intake → S3T6 filter → S3T7 rank →
  S4T8 shortlist) with `LinkedInAdapter` registered produces a non-empty, CR-8-valid shortlist
  for at least one realistic role, with zero changes required in any Sprint 1–4 file.

---

## Inputs to Read (REQUIRED)

- neshama/context/decisions.md (D-01, revised entry)
- neshama/context/requirements.md (CR-8, CR-9)
- neshama/context/assumptions.md (A-2 superseded, A-7 resolved)
- src/adapters/base.py, src/adapters/registry.py (from S1T2 — must exist)
- src/domain/candidate.py (from S1T1 — must exist)

---

## Outputs Expected (REQUIRED)

- `src/adapters/linkedin_adapter.py` — `LinkedInAdapter` implementation
- `tests/adapters/test_linkedin_adapter.py` — unit tests against recorded/fixture HTML or
  mocked HTTP responses (not live network calls in the test suite)
- A short `docs/linkedin_adapter_setup.md` explaining how the owner supplies their session
  credentials locally (env var or git-ignored file — name it explicitly)

---

## Acceptance Tests (REQUIRED)

- `pytest tests/adapters/test_linkedin_adapter.py -v` — all pass using recorded fixtures, no
  live network access during the test run, raw output pasted into completion report.
- A test proving every `Candidate` constructed from adapter output passes S1T1's CR-8
  validation (has `source_url`, `source_name`, `collected_at`, `collection_basis`).
- A test proving a malformed/unexpected page structure raises a typed error rather than
  silently returning a partially-populated or invalid `Candidate`.
- A manual end-to-end run (documented in the completion report, not a pytest test) showing one
  real search producing a non-empty shortlist through the full S2→S4 pipeline.

---

## Forbidden Assumptions (REQUIRED)

- Do not hard-code any credential, session cookie, or token directly in a source file.
- Do not commit any fixture that contains another real person's private data beyond what is
  ordinarily visible on a public/logged-in profile page used strictly for the owner's own
  personal sourcing use.
- Do not modify `src/matching/`, `src/shortlist/`, or `src/suppression/` — this tranche is
  adapter-only; if the interface genuinely needs to change, raise it via `tranche.question`
  rather than editing S1T2's `base.py` directly.
- Do not remove or disable `MockSourceAdapter` — keep it for future test fixtures.

---

## Allowed Terminal Commands

- Test runners: `pytest`
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `python -m py_compile`

> **Explicitly NOT allowed unless added above:** `pip install` (ask via `tranche.question` if
> an HTTP/scraping library is genuinely needed), background processes, permission changes. Live
> scraping runs (outside the test suite) are fine to execute manually for the end-to-end check,
> but do not automate them into a CI-style loop within this tranche.

---

## Questions for PM

The worker may append clarification questions here before starting work.

---

## Completion Gate (MANDATORY)

See the Worker KICKSTART_PROMPT for full completion requirements.
Tests must be run locally with raw output pasted into the Completion Report.

---

## Delivery Format

- Code + tests + the short setup doc.
- Completion report must name the exact env var / config file used for credentials, and
  confirm it is git-ignored.

---

## Notes

D-01 is resolved specifically for this personal-use context (see `neshama/context/decisions.md`,
2026-09-17 revision). If this tool is ever shared with or used by anyone other than the owner,
stop and re-open D-01 before continuing to use this adapter.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprint5/S5T10_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
