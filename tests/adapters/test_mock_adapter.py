from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.candidate import Candidate


def test_mock_adapter_returns_multiple_candidates():
    adapter = MockSourceAdapter()
    candidates = adapter.fetch_candidates("backend engineer")
    assert len(candidates) >= 5


def test_every_mock_candidate_constructs_as_valid_candidate():
    adapter = MockSourceAdapter()
    candidates = adapter.fetch_candidates("anything")
    for candidate in candidates:
        assert isinstance(candidate, Candidate)
        assert candidate.source_url
        assert candidate.source_name
        assert candidate.collection_basis is not None


def test_mock_adapter_candidates_have_varied_fields():
    adapter = MockSourceAdapter()
    candidates = adapter.fetch_candidates("anything")
    employers = {c.current_employer for c in candidates}
    skills = {s for c in candidates for s in c.skills}
    assert len(employers) > 1
    assert len(skills) > 1
