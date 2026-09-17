"""Suppression/deletion pipeline (S4T9). See requirements.md CR-10, decisions.md D-04.

SLA (owner decision, 2026-09-17): suppression is synchronous -- the call returns only after
the candidate store reflects it. Deletion also applies synchronously to the store (this
personal-use, single-operator build has no background job queue), which trivially satisfies
the 24-hour purge bound; if a slower/batched purge is added later, the 24h test in
tests/suppression/test_pipeline.py is the place to re-verify the bound.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.audit_log import AuditLogEntry
from src.storage.audit_store import AuditStore
from src.storage.candidate_store import CandidateStore
from src.suppression.tombstone import TombstoneStore


class CandidateNotFoundError(ValueError):
    pass


def suppress_candidate(
    candidate_id: str,
    candidate_store: CandidateStore,
    audit_store: AuditStore,
    requested_by: str,
) -> None:
    """Synchronous, temporary exclusion -- record retained, just hidden from reads (CR-10)."""
    candidate = candidate_store.get_including_hidden(candidate_id)
    if candidate is None:
        raise CandidateNotFoundError(candidate_id)

    candidate_store.write(candidate.with_suppressed(True))
    _log_action(audit_store, "suppression", candidate_id, requested_by)


def delete_candidate(
    candidate_id: str,
    candidate_store: CandidateStore,
    audit_store: AuditStore,
    tombstone_store: TombstoneStore,
    requested_by: str,
) -> None:
    """Permanent removal. Writes a tombstone FIRST so no re-ingestion can win a race against
    the store update, then marks the stored record deleted (CR-10)."""
    candidate = candidate_store.get_including_hidden(candidate_id)
    if candidate is None:
        raise CandidateNotFoundError(candidate_id)

    tombstone_store.add(candidate_id)
    candidate_store.write(candidate.with_deleted(datetime.utcnow()))
    _log_action(audit_store, "deletion", candidate_id, requested_by)


def _log_action(audit_store: AuditStore, event_type: str, candidate_id: str, requested_by: str) -> None:
    audit_store.append(
        AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            event_type=event_type,
            requirement_set_id=None,
            candidate_ids=(candidate_id,),
            reasons_shown={},
            internal_scores={},
            timestamp=datetime.utcnow(),
            user_id=requested_by,
        )
    )
