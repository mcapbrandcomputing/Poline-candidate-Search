# Tranche S1T1 - COMPLETION REPORT

Status: ACCEPTED
Worker: Claude (solo PM+worker session)
Completed: 2026-09-17

---

## Summary of Work Performed

Implemented the `Candidate` and `AuditLogEntry` record types and their file-based JSONL
persistence primitives, per the S1T1 brief.

---

## Files Modified or Created (REQUIRED)

- src/domain/candidate.py
- src/domain/audit_log.py
- src/storage/candidate_store.py
- src/storage/audit_store.py
- tests/domain/test_candidate.py
- tests/domain/test_audit_log.py
- tests/storage/test_candidate_store.py
- tests/storage/test_audit_store.py

---

## Implementation Notes (REQUIRED)

### Files Changed and Why

- `src/domain/candidate.py`: immutable `Candidate` dataclass; `__post_init__` raises
  `MissingCollectionBasisError` if `collection_basis`, `source_url`, `source_name`, or
  `collected_at` is missing (CR-8), enforced at construction, not filtered later.
- `src/domain/audit_log.py`: immutable `AuditLogEntry` dataclass carrying an opaque
  `requirement_set_id`, candidate ids, reasons, internal scores, timestamp, and user id (CR-11).
  `event_type` field added (not specified verbatim in the brief but required to let S4T9 log
  suppression/deletion events through the same mechanism without inventing a second log, per
  the brief's own Manifesto).
- `src/storage/candidate_store.py`: JSONL upsert store. `list_visible()`/`get()` exclude any
  record where `is_visible()` is False (CR-10); `get_including_hidden()` is a separate,
  explicitly-named escape hatch for the future suppression pipeline (S4T9).
- `src/storage/audit_store.py`: append-only JSONL store. No `update`/`delete` method exists.

### Persistence choice

File-based JSONL, one file per store, under a caller-supplied path. Chosen over an embedded DB
for zero new dependencies and straightforward inspection during development. No query engine
was added, per the brief's scope limit.

---

## Evidence of Correctness

```text
.venv/bin/python -m pytest tests/domain/test_candidate.py tests/domain/test_audit_log.py tests/storage/test_candidate_store.py tests/storage/test_audit_store.py -v

Raw Test Output

============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /Users/maxcaplovitz/Poline- Linkden Scraper/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/maxcaplovitz/Poline- Linkden Scraper
collecting ... collected 23 items

tests/domain/test_candidate.py::test_candidate_constructs_with_valid_collection_basis PASSED [  4%]
tests/domain/test_candidate.py::test_candidate_rejects_none_collection_basis PASSED [  8%]
tests/domain/test_candidate.py::test_candidate_rejects_invalid_collection_basis_value PASSED [ 13%]
tests/domain/test_candidate.py::test_candidate_rejects_missing_source_url PASSED [ 17%]
tests/domain/test_candidate.py::test_candidate_rejects_missing_source_name PASSED [ 21%]
tests/domain/test_candidate.py::test_candidate_rejects_missing_collected_at PASSED [ 26%]
tests/domain/test_candidate.py::test_is_visible_true_by_default PASSED   [ 30%]
tests/domain/test_candidate.py::test_is_visible_false_when_suppressed PASSED [ 34%]
tests/domain/test_candidate.py::test_is_visible_false_when_deleted PASSED [ 39%]
tests/domain/test_candidate.py::test_candidate_is_immutable PASSED       [ 43%]
tests/domain/test_audit_log.py::test_audit_log_entry_holds_full_search_substrate PASSED [ 47%]
tests/domain/test_audit_log.py::test_audit_log_entry_supports_non_search_event_types PASSED [ 52%]
tests/storage/test_candidate_store.py::test_write_and_get_round_trip PASSED [ 56%]
tests/storage/test_candidate_store.py::test_write_upserts_by_candidate_id PASSED [ 60%]
tests/storage/test_candidate_store.py::test_get_returns_none_for_suppressed_candidate PASSED [ 65%]
tests/storage/test_candidate_store.py::test_get_returns_none_for_deleted_candidate PASSED [ 69%]
tests/storage/test_candidate_store.py::test_list_visible_excludes_suppressed_and_deleted PASSED [ 73%]
tests/storage/test_candidate_store.py::test_get_including_hidden_bypasses_visibility_filter PASSED [ 78%]
tests/storage/test_candidate_store.py::test_deletion_persists_across_reload PASSED [ 82%]
tests/storage/test_audit_store.py::test_append_and_read_round_trip PASSED [ 86%]
tests/storage/test_audit_store.py::test_append_is_additive_not_overwriting PASSED [ 91%]
tests/storage/test_audit_store.py::test_audit_store_has_no_update_or_delete_method PASSED [ 95%]
tests/storage/test_audit_store.py::test_entries_persist_across_reload PASSED [100%]

============================== 23 passed in 0.01s ==============================
```

> Submitted as-is; all 23 passed on first run, no code was edited based on results.

---

## Code Review Checklist (REQUIRED)

- All applicable checklist items verified.
- N/A items: none.

---

## Requirements Coverage

CR-8, CR-10 (field + store-level enforcement), CR-11 substrate.

---

## Assumptions Made (REQUIRED)

- JSONL/file-based storage chosen for zero-dependency persistence; no database engine was
  specified in the brief. If a real embedded DB is wanted later, storage classes' public
  methods (`write`, `get`, `list_visible`) are the seam to swap the implementation behind.
- `AuditLogEntry.event_type` was added beyond the brief's literal field list to support S4T9's
  suppression/deletion logging through the same mechanism without a second log — flagged as an
  addition here rather than silently introduced.

---

## Open Issues or Risks

None.

---

## Questions for PM

None.
