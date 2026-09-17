"""Recruiter-facing shortlist rendering (S4T8). See requirements.md CR-4, CR-5, C-5.

Defense in depth: even though src/matching/search.py already keeps scores out of
SearchResult, this module re-verifies at the presentation boundary -- the actual place a
recruiter looks -- that no score/rank/percentage/grade token ever appears in rendered text.
"""
from __future__ import annotations

from src.matching.search import SearchResult

DISCLAIMER = (
    "This is a sourcing aid, not a hiring recommendation. Every judgment about a candidate "
    "is yours to make."
)

_FORBIDDEN_TOKENS = ("score", "rank", "%", "star", "grade")


def render_shortlist(result: SearchResult, flagged_ids: set[str] | None = None) -> str:
    """Plain-text rendering: non-ranked list, name + reasons, ATS-flag note if applicable."""
    flagged_ids = flagged_ids or set()
    lines = [DISCLAIMER, ""]
    for candidate in result.candidates:
        lines.append(f"- {candidate.name} — {candidate.headline} @ {candidate.current_employer}")
        for reason in result.reasons.get(candidate.candidate_id, []):
            lines.append(f"    reason: {reason}")
        if candidate.candidate_id in flagged_ids:
            lines.append("    note: already in ATS")
        lines.append("")
    rendered = "\n".join(lines)
    _assert_no_forbidden_tokens(rendered)
    return rendered


def _assert_no_forbidden_tokens(rendered: str) -> None:
    lower = rendered.lower()
    for token in _FORBIDDEN_TOKENS:
        assert token not in lower, f"Rendered shortlist leaked a forbidden token: {token!r}"
