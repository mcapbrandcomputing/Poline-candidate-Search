import dataclasses
from pathlib import Path

import pytest

from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.matching.search import SearchResult, run_search
from src.storage.audit_store import AuditStore


@pytest.fixture
def audit_store(tmp_path: Path) -> AuditStore:
    return AuditStore(tmp_path / "audit.jsonl")


def all_candidates():
    return MockSourceAdapter().fetch_candidates("x")


def test_search_result_has_no_score_or_rank_field():
    """CR-4/CR-5: grep the dataclass fields for anything score/rank-shaped."""
    field_names = {f.name for f in dataclasses.fields(SearchResult)}
    forbidden_substrings = ("score", "rank", "percent", "grade", "star")
    for name in field_names:
        assert not any(bad in name.lower() for bad in forbidden_substrings), name


def test_search_writes_internal_score_to_audit_log(audit_store):
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
    )
    run_search(rs, all_candidates(), audit_store, user_id="owner")

    entries = list(audit_store.read_all())
    assert len(entries) == 1
    assert entries[0].internal_scores  # non-empty: scores were captured somewhere


def test_candidates_with_zero_reasons_are_absent_from_result(audit_store):
    """mock-4 (typescript/react) has no skill overlap with a python-only requirement -- it must
    be entirely absent, not present with an empty reasons list."""
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
    )
    result = run_search(rs, all_candidates(), audit_store, user_id="owner")
    result_ids = {c.candidate_id for c in result.candidates}
    assert "mock-4" not in result_ids
    assert all(result.reasons[cid] for cid in result_ids)


def test_result_set_matches_boolean_filter_survivors_before_batching(audit_store):
    """Membership must equal S3T6's survivor set (modulo the zero-reasons drop and batch_size
    truncation) -- ranking never adds candidates (CR-2)."""
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
        excluded_employers=("Acme Corp",),
    )
    result = run_search(rs, all_candidates(), audit_store, user_id="owner")
    result_ids = {c.candidate_id for c in result.candidates}
    assert "mock-1" not in result_ids  # excluded employer
    assert "mock-4" not in result_ids  # excluded employer AND no python anyway
    assert result_ids.issubset({c.candidate_id for c in all_candidates()})


def test_final_order_is_alphabetical_not_by_score(audit_store):
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
    )
    result = run_search(rs, all_candidates(), audit_store, user_id="owner")
    names = [c.name for c in result.candidates]
    assert names == sorted(names)


def test_batch_size_truncates_result():
    from src.storage.audit_store import AuditStore
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        store = AuditStore(Path(d) / "audit.jsonl")
        rs = RequirementSet(
            requirement_set_id="rs1",
            requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
            batch_size=1,
        )
        result = run_search(rs, all_candidates(), store, user_id="owner")
        assert len(result.candidates) == 1
