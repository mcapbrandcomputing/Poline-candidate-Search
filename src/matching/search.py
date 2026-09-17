"""Search orchestration (S3T7): boolean filter -> reasons -> internal scoring/audit -> a
recruiter-safe result. See requirements.md CR-2..CR-5, CR-11.

`SearchResult.candidates` and `.reasons` are the ONLY fields on the public return value --
there is no score/rank field anywhere on this type, by construction, so no caller can
accidentally forward one to a recruiter-facing surface (CR-4).

Recruiter-facing order (CR-5): candidates are sorted by name (stable, non-ranked) before being
returned. The internal semantic score exists only to (a) get written to the audit log, and
(b) decide which candidates are dropped for batch_size truncation *before* the final
alphabetical sort is applied -- i.e. batch_size selects the top-N by internal relevance, then
the selected N are re-sorted alphabetically for display. This keeps CR-2's "ranking orders,
never adds to" contract while still respecting CR-5's "no implied fitness from position" for
whatever the recruiter actually sees.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.audit_log import AuditLogEntry
from src.domain.candidate import Candidate
from src.domain.requirement import RequirementSet
from src.matching.boolean_filter import filter_candidates
from src.matching.reasons import build_reasons
from src.matching.semantic_ranker import score_candidates
from src.storage.audit_store import AuditStore


@dataclass(frozen=True)
class SearchResult:
    """Recruiter-safe search output. No score, rank, percentage, or grade field exists here."""

    candidates: tuple[Candidate, ...]
    reasons: dict = field(default_factory=dict)  # candidate_id -> list[str]


def run_search(
    rs: RequirementSet,
    candidates: list[Candidate],
    audit_store: AuditStore,
    user_id: str,
) -> SearchResult:
    survivors = filter_candidates(rs, candidates)

    reasons_by_id = {c.candidate_id: build_reasons(c, rs) for c in survivors}
    with_reasons = [c for c in survivors if reasons_by_id[c.candidate_id]]  # CR-3

    scores = score_candidates(with_reasons, rs)

    ranked = sorted(with_reasons, key=lambda c: scores[c.candidate_id], reverse=True)
    if rs.batch_size:
        ranked = ranked[: rs.batch_size]

    final_candidates = tuple(sorted(ranked, key=lambda c: c.name))  # CR-5: alphabetical, non-ranked
    final_reasons = {c.candidate_id: reasons_by_id[c.candidate_id] for c in final_candidates}
    final_scores = {c.candidate_id: scores[c.candidate_id] for c in final_candidates}

    audit_store.append(
        AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            event_type="search",
            requirement_set_id=rs.requirement_set_id,
            candidate_ids=tuple(c.candidate_id for c in final_candidates),
            reasons_shown=final_reasons,
            internal_scores=final_scores,
            timestamp=datetime.utcnow(),
            user_id=user_id,
        )
    )

    return SearchResult(candidates=final_candidates, reasons=final_reasons)
