from datetime import datetime

from src.domain.audit_log import AuditLogEntry


def make_entry(**overrides) -> AuditLogEntry:
    defaults = dict(
        entry_id="a1",
        event_type="search",
        requirement_set_id="rs1",
        candidate_ids=("c1", "c2"),
        reasons_shown={"c1": ["matched python"], "c2": ["matched python"]},
        internal_scores={"c1": 0.91, "c2": 0.77},
        timestamp=datetime(2026, 9, 17, 12, 0, 0),
        user_id="owner",
    )
    defaults.update(overrides)
    return AuditLogEntry(**defaults)


def test_audit_log_entry_holds_full_search_substrate():
    entry = make_entry()
    assert entry.requirement_set_id == "rs1"
    assert entry.candidate_ids == ("c1", "c2")
    assert entry.internal_scores["c1"] == 0.91


def test_audit_log_entry_supports_non_search_event_types():
    entry = make_entry(event_type="suppression", requirement_set_id=None, candidate_ids=("c1",))
    assert entry.event_type == "suppression"
    assert entry.requirement_set_id is None
