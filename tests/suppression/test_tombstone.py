from datetime import datetime
from pathlib import Path

import pytest

from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.candidate import Candidate, CollectionBasis
from src.storage.audit_store import AuditStore
from src.storage.candidate_store import CandidateStore
from src.suppression.pipeline import delete_candidate
from src.suppression.tombstone import TombstoneStore, guard_ingested_candidates, ingest_and_store


@pytest.fixture
def stores(tmp_path: Path):
    return (
        CandidateStore(tmp_path / "candidates.jsonl"),
        AuditStore(tmp_path / "audit.jsonl"),
        TombstoneStore(tmp_path / "tombstones.jsonl"),
    )


def make_candidate(candidate_id="mock-1") -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        name="Alex Rivera",
        headline="Senior Backend Engineer",
        current_employer="Acme Corp",
        location="Austin, TX",
        skills=("python",),
        source_url="https://mock.example/profile/mock-1",
        source_name="mock",
        collected_at=datetime(2026, 9, 17),
        collection_basis=CollectionBasis.PUBLIC_PERMISSIBLE,
    )


def test_guard_drops_tombstoned_candidate(stores):
    _, _, tombstone_store = stores
    tombstone_store.add("mock-1")
    survivors = guard_ingested_candidates([make_candidate("mock-1"), make_candidate("mock-2")], tombstone_store)
    survivor_ids = {c.candidate_id for c in survivors}
    assert survivor_ids == {"mock-2"}


def test_guard_passes_through_non_tombstoned_candidates(stores):
    _, _, tombstone_store = stores
    survivors = guard_ingested_candidates([make_candidate("mock-1")], tombstone_store)
    assert len(survivors) == 1


def test_reingestion_after_deletion_does_not_resurrect_candidate(stores):
    """The end-to-end proof required by S4T9's brief: delete a candidate, then re-run
    MockSourceAdapter's ingestion for the same identifier -- it must stay absent from every
    read path (raw store here; S3T6/S3T7/S4T8 all read through candidate_store.py so this
    guard covers them transitively)."""
    candidate_store, audit_store, tombstone_store = stores
    candidate_store.write(make_candidate("mock-1"))
    delete_candidate("mock-1", candidate_store, audit_store, tombstone_store, requested_by="owner")
    assert candidate_store.get("mock-1") is None

    adapter = MockSourceAdapter()  # mock-1 is one of its fixture candidates
    ingest_and_store(adapter, "anything", candidate_store, tombstone_store)

    assert candidate_store.get("mock-1") is None  # deletion wins over the re-crawl
    other_ids = {c.candidate_id for c in candidate_store.list_visible()}
    assert "mock-2" in other_ids  # non-deleted candidates from the same crawl do come through
