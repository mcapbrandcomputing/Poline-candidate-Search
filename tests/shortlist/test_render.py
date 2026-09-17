from pathlib import Path

import pytest

from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.matching.search import run_search
from src.shortlist.render import render_shortlist
from src.storage.audit_store import AuditStore


@pytest.fixture
def audit_store(tmp_path: Path) -> AuditStore:
    return AuditStore(tmp_path / "audit.jsonl")


def test_rendered_shortlist_contains_no_score_or_rank_tokens(audit_store):
    """Fixture candidates have known non-zero internal scores in the audit log -- the render
    must still surface none of it."""
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
    )
    candidates = MockSourceAdapter().fetch_candidates("x")
    result = run_search(rs, candidates, audit_store, user_id="owner")

    rendered = render_shortlist(result)
    lower = rendered.lower()
    for forbidden in ("score", "rank", "%", "star", "grade"):
        assert forbidden not in lower


def test_rendered_shortlist_includes_disclaimer(audit_store):
    rs = RequirementSet(requirement_set_id="rs1")
    result = run_search(rs, [], audit_store, user_id="owner")
    rendered = render_shortlist(result)
    assert "sourcing aid" in rendered.lower()


def test_rendered_shortlist_shows_reasons_and_flags(audit_store):
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python", type=RequirementType.DISQUALIFYING),),
    )
    candidates = MockSourceAdapter().fetch_candidates("x")
    result = run_search(rs, candidates, audit_store, user_id="owner")
    flagged = {result.candidates[0].candidate_id}

    rendered = render_shortlist(result, flagged_ids=flagged)
    assert "reason:" in rendered
    assert "already in ATS" in rendered
