from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.domain.candidate import Candidate, CollectionBasis
from src.storage.audit_store import AuditStore
from src.storage.candidate_store import CandidateStore
from src.suppression.pipeline import CandidateNotFoundError, delete_candidate, suppress_candidate
from src.suppression.tombstone import TombstoneStore


def make_candidate(candidate_id="c1") -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        name="Jane Example",
        headline="Engineer",
        current_employer="Acme Corp",
        location="Remote",
        skills=("python",),
        source_url="https://example.com/profile/jane",
        source_name="mock",
        collected_at=datetime(2026, 9, 17),
        collection_basis=CollectionBasis.PUBLIC_PERMISSIBLE,
    )


@pytest.fixture
def stores(tmp_path: Path):
    return (
        CandidateStore(tmp_path / "candidates.jsonl"),
        AuditStore(tmp_path / "audit.jsonl"),
        TombstoneStore(tmp_path / "tombstones.jsonl"),
    )


def test_suppress_excludes_candidate_immediately(stores):
    candidate_store, audit_store, _ = stores
    candidate_store.write(make_candidate())

    suppress_candidate("c1", candidate_store, audit_store, requested_by="owner")

    assert candidate_store.get("c1") is None  # synchronous -- no polling needed


def test_suppress_retains_underlying_record(stores):
    candidate_store, audit_store, _ = stores
    candidate_store.write(make_candidate())
    suppress_candidate("c1", candidate_store, audit_store, requested_by="owner")

    assert candidate_store.get_including_hidden("c1") is not None


def test_suppress_missing_candidate_raises(stores):
    candidate_store, audit_store, _ = stores
    with pytest.raises(CandidateNotFoundError):
        suppress_candidate("does-not-exist", candidate_store, audit_store, requested_by="owner")


def test_delete_purges_within_24_hours(stores):
    """This build's deletion is synchronous, so the purge timestamp is <= now -- trivially
    within the 24h bound. If a background purge job is introduced later, this test's bound
    (deleted_at - request_time <= 24h) is what must still hold."""
    candidate_store, audit_store, tombstone_store = stores
    candidate_store.write(make_candidate())

    request_time = datetime.utcnow()
    delete_candidate("c1", candidate_store, audit_store, tombstone_store, requested_by="owner")

    deleted_record = candidate_store.get_including_hidden("c1")
    assert deleted_record.deleted_at is not None
    assert deleted_record.deleted_at - request_time <= timedelta(hours=24)


def test_delete_is_permanent_and_excluded_from_reads(stores):
    candidate_store, audit_store, tombstone_store = stores
    candidate_store.write(make_candidate())
    delete_candidate("c1", candidate_store, audit_store, tombstone_store, requested_by="owner")

    assert candidate_store.get("c1") is None


def test_every_suppression_and_deletion_is_recorded_in_audit_log(stores):
    candidate_store, audit_store, tombstone_store = stores
    candidate_store.write(make_candidate("c1"))
    candidate_store.write(make_candidate("c2"))

    suppress_candidate("c1", candidate_store, audit_store, requested_by="owner")
    delete_candidate("c2", candidate_store, audit_store, tombstone_store, requested_by="owner")

    entries = list(audit_store.read_all())
    event_types = {e.event_type for e in entries}
    assert event_types == {"suppression", "deletion"}
    for entry in entries:
        assert entry.user_id == "owner"
        assert entry.timestamp is not None
