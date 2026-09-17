# Tranche S2T4 - COMPLETION REPORT

Status: ACCEPTED
Worker: Claude (solo PM+worker session)
Completed: 2026-09-17

---

## Summary of Work Performed

Implemented deterministic, local JD-to-draft-`RequirementSet` extraction (regex/heuristic
based, no network calls), plus 3 fixture JDs.

---

## Files Modified or Created (REQUIRED)

- src/nlp/jd_extractor.py
- tests/nlp/test_jd_extractor.py
- tests/fixtures/sample_jds/technical_role.txt
- tests/fixtures/sample_jds/nontechnical_role.txt
- tests/fixtures/sample_jds/sparse_role.txt

---

## Implementation Notes (REQUIRED)

### Files Changed and Why

- `src/nlp/jd_extractor.py`: regex-based extraction for work_authorization, credentials,
  location_policy/worksite, geo_scope, comp_band, experience_semantics, and bullet-list
  requirements (defaulted to `RequirementType.DISQUALIFYING`, per CR-1's note that JDs bury
  real requirements among boilerplate). Every Block A scalar field is either a real value or
  the `NOT_FOUND_IN_JD` sentinel imported from `src/domain/requirement.py` (S1T3) — no separate
  `src/nlp/sentinels.py` was created; see S1T3's completion report and the brief note added
  before this tranche started.
- List-typed Block A fields (`credentials`, `excluded_employers`) use an empty tuple `()` for
  "not found," consistent with `RequirementSet`'s own unset-check (which already treats `()` as
  unset) rather than wrapping the string sentinel in a tuple.

---

## Evidence of Correctness

```text
.venv/bin/python -m pytest tests/nlp -v

Raw Test Output

============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /Users/maxcaplovitz/Poline- Linkden Scraper/.venv/bin/python
collecting ... collected 8 items

tests/nlp/test_jd_extractor.py::test_every_block_a_scalar_field_is_populated_or_explicitly_not_found[technical_role.txt] PASSED
tests/nlp/test_jd_extractor.py::test_every_block_a_scalar_field_is_populated_or_explicitly_not_found[nontechnical_role.txt] PASSED
tests/nlp/test_jd_extractor.py::test_every_block_a_scalar_field_is_populated_or_explicitly_not_found[sparse_role.txt] PASSED
tests/nlp/test_jd_extractor.py::test_extraction_result_is_never_confirmed PASSED
tests/nlp/test_jd_extractor.py::test_extracted_requirements_default_to_disqualifying PASSED
tests/nlp/test_jd_extractor.py::test_technical_role_extracts_hybrid_and_comp_and_geo PASSED
tests/nlp/test_jd_extractor.py::test_nontechnical_role_extracts_remote_and_comp PASSED
tests/nlp/test_jd_extractor.py::test_sparse_jd_does_not_crash_and_produces_valid_draft PASSED

============================== 8 passed in 0.01s ===============================
```

---

## Code Review Checklist (REQUIRED)

- All applicable checklist items verified.
- N/A items: none.

---

## Requirements Coverage

CR-6, CR-7.

---

## Assumptions Made (REQUIRED)

- No ML/LLM extraction used, per the brief's explicit allowance — deterministic regex/keyword
  heuristics only. Extraction quality is intentionally rough (e.g. `geo_scope` only recognizes
  a few US-indicating phrases); recruiter confirmation (S2T5) is the real correctness gate.

---

## Open Issues or Risks

Extraction recall is limited (regex-based); flagged as expected, not a defect — S2T5's
confirmation flow exists specifically because JD extraction is never trusted as final (D-05).

---

## Questions for PM

None.
