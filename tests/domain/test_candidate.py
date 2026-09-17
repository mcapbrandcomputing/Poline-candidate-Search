from datetime import datetime

import pytest

from src.domain.candidate import Candidate, CollectionBasis, MissingCollectionBasisError


def make_candidate(**overrides) -> Candidate:
    defaults = dict(
        candidate_id="c1",
        name="Jane Example",
        headline="Senior Engineer",
        current_employer="Acme Corp",
        location="Remote",
        skills=("python", "distributed systems"),
        source_url="https://example.com/profile/jane",
        source_name="linkedin",
        collected_at=datetime(2026, 9, 17, 12, 0, 0),
        collection_basis=CollectionBasis.PERSONAL_USE_SCRAPE,
    )
    defaults.update(overrides)
    return Candidate(**defaults)


def test_candidate_constructs_with_valid_collection_basis():
    candidate = make_candidate()
    assert candidate.collection_basis == CollectionBasis.PERSONAL_USE_SCRAPE


def test_candidate_rejects_none_collection_basis():
    with pytest.raises(MissingCollectionBasisError):
        make_candidate(collection_basis=None)


def test_candidate_rejects_invalid_collection_basis_value():
    with pytest.raises(MissingCollectionBasisError):
        make_candidate(collection_basis="not-a-real-basis")


def test_candidate_rejects_missing_source_url():
    with pytest.raises(MissingCollectionBasisError):
        make_candidate(source_url="")


def test_candidate_rejects_missing_source_name():
    with pytest.raises(MissingCollectionBasisError):
        make_candidate(source_name="")


def test_candidate_rejects_missing_collected_at():
    with pytest.raises(MissingCollectionBasisError):
        make_candidate(collected_at=None)


def test_is_visible_true_by_default():
    assert make_candidate().is_visible() is True


def test_is_visible_false_when_suppressed():
    candidate = make_candidate().with_suppressed(True)
    assert candidate.is_visible() is False


def test_is_visible_false_when_deleted():
    candidate = make_candidate().with_deleted(datetime(2026, 9, 18))
    assert candidate.is_visible() is False


def test_candidate_is_immutable():
    candidate = make_candidate()
    with pytest.raises(Exception):
        candidate.name = "Someone Else"
