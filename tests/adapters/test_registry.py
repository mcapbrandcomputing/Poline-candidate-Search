from datetime import datetime

from src.adapters.base import SourceAdapter
from src.adapters.registry import all_names, get, register
from src.domain.candidate import Candidate, CollectionBasis


class _FakeAdapter(SourceAdapter):
    def fetch_candidates(self, query: str) -> list[Candidate]:
        return [
            Candidate(
                candidate_id="fake-1",
                name="Fake Person",
                headline="Fake Role",
                current_employer="Fake Co",
                location="Nowhere",
                skills=("fake-skill",),
                source_url="https://fake.example/1",
                source_name="fake",
                collected_at=datetime(2026, 9, 17),
                collection_basis=CollectionBasis.PUBLIC_PERMISSIBLE,
            )
        ]


def test_mock_adapter_registered_by_default():
    assert "mock" in all_names()
    adapter = get("mock")
    assert adapter.fetch_candidates("x")


def test_get_unknown_adapter_raises():
    import pytest

    with pytest.raises(KeyError):
        get("does-not-exist")


def test_register_adds_new_adapter_without_editing_base_or_mock():
    """Proves a second adapter can be added purely by calling register() — no changes to
    base.py, mock_adapter.py, or src/domain/ are needed (CR-9)."""
    register("fake", _FakeAdapter())
    assert "fake" in all_names()
    candidates = get("fake").fetch_candidates("anything")
    assert candidates[0].candidate_id == "fake-1"
