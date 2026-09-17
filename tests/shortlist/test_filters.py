from datetime import datetime

from src.adapters.mock_adapter import MockSourceAdapter
from src.shortlist.filters import apply_ats_dedupe, apply_freshness_floor


def all_candidates():
    return MockSourceAdapter().fetch_candidates("x")


def test_ats_dedupe_exclude_removes_matching_candidates():
    candidates = all_candidates()
    shown, flagged = apply_ats_dedupe(candidates, {"mock-1", "mock-2"}, "exclude")
    shown_ids = {c.candidate_id for c in shown}
    assert "mock-1" not in shown_ids
    assert "mock-2" not in shown_ids
    assert flagged == set()


def test_ats_dedupe_flag_marks_without_removing():
    candidates = all_candidates()
    shown, flagged = apply_ats_dedupe(candidates, {"mock-1"}, "flag")
    assert len(shown) == len(candidates)
    assert flagged == {"mock-1"}


def test_ats_dedupe_include_passes_through_unchanged():
    candidates = all_candidates()
    shown, flagged = apply_ats_dedupe(candidates, {"mock-1"}, "include")
    assert len(shown) == len(candidates)
    assert flagged == set()


def test_ats_dedupe_unset_policy_defaults_to_include():
    candidates = all_candidates()
    shown, flagged = apply_ats_dedupe(candidates, {"mock-1"}, None)
    assert len(shown) == len(candidates)


def test_freshness_floor_excludes_stale_candidate():
    candidates = all_candidates()  # all collected_at = 2026-09-17 12:00:00
    floor = datetime(2026, 9, 18)
    result = apply_freshness_floor(candidates, floor)
    assert result == []


def test_freshness_floor_retains_fresh_candidate():
    candidates = all_candidates()
    floor = datetime(2026, 9, 1)
    result = apply_freshness_floor(candidates, floor)
    assert len(result) == len(candidates)


def test_no_freshness_floor_means_no_filtering():
    candidates = all_candidates()
    result = apply_freshness_floor(candidates, None)
    assert len(result) == len(candidates)
