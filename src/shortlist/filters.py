"""Block D search-behavior filters (S4T8): ats_dedupe_policy, freshness_floor.
batch_size is already applied in src/matching/search.py -- not duplicated here."""
from __future__ import annotations

from datetime import datetime

from src.domain.candidate import Candidate


def apply_ats_dedupe(
    candidates: list[Candidate], already_in_ats: set[str], policy: str | None
) -> tuple[list[Candidate], set[str]]:
    """Returns (candidates_to_show, flagged_ids). `policy` is one of "exclude"/"flag"/"include".
    Unset/unknown policy defaults to "include" (fail-open -- do not silently hide candidates)."""
    if policy == "exclude":
        return [c for c in candidates if c.candidate_id not in already_in_ats], set()
    if policy == "flag":
        flagged = {c.candidate_id for c in candidates if c.candidate_id in already_in_ats}
        return list(candidates), flagged
    return list(candidates), set()  # "include" or unset


def apply_freshness_floor(candidates: list[Candidate], floor: datetime | None) -> list[Candidate]:
    """Excludes candidates whose collected_at predates `floor`. No floor means no filtering."""
    if floor is None:
        return list(candidates)
    return [c for c in candidates if c.collected_at >= floor]
