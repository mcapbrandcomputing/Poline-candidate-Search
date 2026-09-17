from datetime import datetime
from pathlib import Path

import pytest

from src.domain.candidate import Candidate, CollectionBasis
from src.storage.candidate_store import CandidateStore


def make_candidate(candidate_id="c1", **overrides) -> Candidate:
    defaults = dict(
        candidate_id=candidate_id,
        name="Jane Example",
        headline="Senior Engineer",
        current_employer="Acme Corp",
        location="Remote",
        skills=("python",),
        source_url="https://example.com/profile/jane",
        source_name="linkedin",
        collected_at=datetime(2026, 9, 17, 12, 0, 0),
        collection_basis=CollectionBasis.PERSONAL_USE_SCRAPE,
    )
    defaults.update(overrides)
    return Candidate(**defaults)


@pytest.fixture
def store(tmp_path: Path) -> CandidateStore:
    return CandidateStore(tmp_path / "candidates.jsonl")


def test_write_and_get_round_trip(store: CandidateStore):
    candidate = make_candidate()
    store.write(candidate)
    result = store.get("c1")
    assert result is not None
    assert result.name == "Jane Example"
    assert result.collection_basis == CollectionBasis.PERSONAL_USE_SCRAPE


def test_write_upserts_by_candidate_id(store: CandidateStore):
    store.write(make_candidate(name="Original"))
    store.write(make_candidate(name="Updated"))
    assert store.get("c1").name == "Updated"
    assert len(list(store.list_visible())) == 1


def test_get_returns_none_for_suppressed_candidate(store: CandidateStore):
    store.write(make_candidate().with_suppressed(True))
    assert store.get("c1") is None


def test_get_returns_none_for_deleted_candidate(store: CandidateStore):
    store.write(make_candidate().with_deleted(datetime(2026, 9, 18)))
    assert store.get("c1") is None


def test_list_visible_excludes_suppressed_and_deleted(store: CandidateStore):
    store.write(make_candidate(candidate_id="visible"))
    store.write(make_candidate(candidate_id="suppressed").with_suppressed(True))
    store.write(make_candidate(candidate_id="deleted").with_deleted(datetime(2026, 9, 18)))

    visible_ids = {c.candidate_id for c in store.list_visible()}
    assert visible_ids == {"visible"}


def test_get_including_hidden_bypasses_visibility_filter(store: CandidateStore):
    store.write(make_candidate().with_suppressed(True))
    result = store.get_including_hidden("c1")
    assert result is not None
    assert result.suppressed is True


def test_deletion_persists_across_reload(tmp_path: Path):
    path = tmp_path / "candidates.jsonl"
    store1 = CandidateStore(path)
    store1.write(make_candidate().with_deleted(datetime(2026, 9, 18)))

    store2 = CandidateStore(path)
    assert store2.get("c1") is None
    assert store2.get_including_hidden("c1").deleted_at is not None
