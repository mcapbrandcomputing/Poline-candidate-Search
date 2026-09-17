from datetime import datetime
from pathlib import Path

import pytest

from src.domain.audit_log import AuditLogEntry
from src.storage.audit_store import AuditStore


def make_entry(entry_id="a1", **overrides) -> AuditLogEntry:
    defaults = dict(
        entry_id=entry_id,
        event_type="search",
        requirement_set_id="rs1",
        candidate_ids=("c1", "c2"),
        reasons_shown={"c1": ["matched python"]},
        internal_scores={"c1": 0.9},
        timestamp=datetime(2026, 9, 17, 12, 0, 0),
        user_id="owner",
    )
    defaults.update(overrides)
    return AuditLogEntry(**defaults)


@pytest.fixture
def store(tmp_path: Path) -> AuditStore:
    return AuditStore(tmp_path / "audit.jsonl")


def test_append_and_read_round_trip(store: AuditStore):
    store.append(make_entry())
    entries = list(store.read_all())
    assert len(entries) == 1
    assert entries[0].entry_id == "a1"
    assert entries[0].internal_scores == {"c1": 0.9}


def test_append_is_additive_not_overwriting(store: AuditStore):
    store.append(make_entry(entry_id="a1"))
    store.append(make_entry(entry_id="a2"))
    entries = list(store.read_all())
    assert {e.entry_id for e in entries} == {"a1", "a2"}


def test_audit_store_has_no_update_or_delete_method(store: AuditStore):
    assert not hasattr(store, "update")
    assert not hasattr(store, "delete")


def test_entries_persist_across_reload(tmp_path: Path):
    path = tmp_path / "audit.jsonl"
    store1 = AuditStore(path)
    store1.append(make_entry())

    store2 = AuditStore(path)
    entries = list(store2.read_all())
    assert len(entries) == 1
