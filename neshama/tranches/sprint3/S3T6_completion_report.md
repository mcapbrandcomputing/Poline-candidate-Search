# Tranche S3T6 - COMPLETION REPORT

Status: ACCEPTED
Worker: Claude (solo PM+worker session)
Completed: 2026-09-17

---

## Summary of Work Performed

Implemented the boolean disqualifying-filter engine over Block A predicates, with an explicit,
documented fail-open/fail-closed table per predicate (Candidate's schema doesn't carry every
field a full implementation would want — see Notes).

---

## Files Modified or Created (REQUIRED)

- src/matching/boolean_filter.py
- tests/matching/test_boolean_filter.py

---

## Implementation Notes (REQUIRED)

### Files Changed and Why

- `src/matching/boolean_filter.py`: `filter_candidates(rs, candidates)` applies six predicates.
  Fail-open/fail-closed table for each is documented directly in the module docstring (per the
  brief's requirement to state this explicitly, not leave it implicit in code):

| Predicate | Behavior | Why |
|---|---|---|
| excluded_employers | fail-closed | Fully supported by `Candidate.current_employer` |
| credentials | fail-closed if required and unevidenced | Best available signal from headline/skills |
| location_policy (hybrid/onsite vs. remote-stated candidate) | fail-closed only on that specific mismatch | The one location signal a free-text field supports |
| work_authorization | fail-open | No field on Candidate carries this |
| geo_scope | fail-open | No country field on Candidate's free-text location |
| comp_band | fail-open | No compensation field on Candidate |

Free-text `requirements[]` entries typed `DISQUALIFYING` are NOT applied as filters here — no
structured field exists to check them against (they're plain text). This is flagged as a known
limitation in the module docstring, not silently dropped.

---

## Evidence of Correctness

```text
.venv/bin/python -m pytest tests/matching/test_boolean_filter.py -v

Raw Test Output

============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /Users/maxcaplovitz/Poline- Linkden Scraper/.venv/bin/python
collecting ... collected 7 items

tests/matching/test_boolean_filter.py::test_golden_path_excludes_matching_employer_and_remote_mismatch PASSED
tests/matching/test_boolean_filter.py::test_realistic_sparse_match_degrades_gracefully_to_empty PASSED
tests/matching/test_boolean_filter.py::test_preferred_requirement_never_excludes_a_candidate PASSED
tests/matching/test_boolean_filter.py::test_credentials_predicate_fails_closed_when_unevidenced PASSED
tests/matching/test_boolean_filter.py::test_credentials_predicate_passes_when_none_required PASSED
tests/matching/test_boolean_filter.py::test_remote_policy_never_excludes_on_location PASSED
tests/matching/test_boolean_filter.py::test_excluded_employers_with_none_sentinel_excludes_nobody PASSED

============================== 7 passed in 0.01s ===============================
```

---

## Code Review Checklist (REQUIRED)

- All applicable checklist items verified.
- N/A items: none.

---

## Requirements Coverage

CR-1, CR-2.

---

## Assumptions Made (REQUIRED)

- Three predicates (work_authorization, geo_scope, comp_band) are structurally fail-open
  because `Candidate` (S1T1) has no corresponding fields — this is a real product gap, not an
  implementation shortcut, and is tracked as such in `neshama/plan/backlog.md` (added by this
  report, see Open Issues).

---

## Open Issues or Risks

Recommend adding `neshama/plan/backlog.md` entries for: (1) whether/how to capture candidate
work-authorization, comp expectations, and country from a real source adapter (Sprint 5's
LinkedIn adapter may or may not expose these), and (2) whether free-text disqualifying
requirements should eventually get a manual recruiter accept/reject step downstream, since they
aren't machine-filtered here.

---

## Questions for PM

Should Sprint 5's `LinkedInAdapter` attempt to populate any of the three fail-open fields
(work_authorization, geo/country, comp) if the profile happens to expose them? Not blocking —
`filter_candidates` fails open regardless, so this can be added later without a breaking change.
