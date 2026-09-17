"""Audit log entry schema (S1T1). See neshama/context/requirements.md CR-11."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AuditLogEntry:
    """One immutable record of a search or a suppression/deletion action (CR-11, CR-10).

    `requirement_set_id` is an opaque reference — S1T3 owns the RequirementSet schema.
    `internal_scores` holds candidate_id -> score, used by S3T7; never rendered to a recruiter
    (CR-4). `event_type` distinguishes a search event from a suppression/deletion event so both
    can share one append-only log without inventing a second mechanism (see S4T9).
    """

    entry_id: str
    event_type: str  # "search" | "suppression" | "deletion"
    requirement_set_id: Optional[str]
    candidate_ids: tuple[str, ...]
    reasons_shown: dict
    internal_scores: dict
    timestamp: datetime
    user_id: str
