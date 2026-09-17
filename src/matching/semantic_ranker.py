"""Internal relevance scoring (S3T7). See requirements.md CR-2, CR-4 and decisions.md D-02:
this module orders S3T6's survivors -- it never changes set membership -- and its score is
written ONLY to the audit log. Nothing in this module's public return value is a
recruiter-facing score; `score_candidates` returns id->score purely for internal/audit use,
and search.py (the orchestration layer) must not forward it to any recruiter-facing output.
"""
from __future__ import annotations

from src.domain.candidate import Candidate
from src.domain.requirement import RequirementSet


def _term_overlap_score(candidate: Candidate, rs: RequirementSet) -> float:
    """Simple bag-of-terms overlap between candidate skills/headline and the RequirementSet's
    free-text/preferred signal (role_outcomes, preferred requirements, title_equivalents,
    source_companies). Deterministic and dependency-free; swappable later for a real embedding
    model behind this same function signature without touching callers."""
    candidate_terms = {t.lower() for t in candidate.skills}
    candidate_terms |= set(candidate.headline.lower().split())

    signal_terms: set[str] = set()
    for requirement in rs.requirements:
        signal_terms |= set(requirement.text.lower().split())
    if rs.role_outcomes:
        signal_terms |= set(rs.role_outcomes.lower().split())
    for title in rs.title_equivalents:
        signal_terms |= set(title.lower().split())

    if not signal_terms:
        return 0.0
    overlap = candidate_terms & signal_terms
    return len(overlap) / len(signal_terms)


def score_candidates(candidates: list[Candidate], rs: RequirementSet) -> dict[str, float]:
    """Returns candidate_id -> internal relevance score. Callers must not surface this dict,
    or any value derived from it, in recruiter-facing output (CR-4)."""
    return {c.candidate_id: _term_overlap_score(c, rs) for c in candidates}
