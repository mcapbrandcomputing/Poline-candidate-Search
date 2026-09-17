"""Per-candidate reasons[] generation (S3T7). See requirements.md CR-3: each element names one
intake requirement and the specific evidence in the candidate's profile satisfying it. A
candidate with zero populated reasons must not be returned by the caller (enforced in
search.py, not here -- this module only produces the reasons list)."""
from __future__ import annotations

from src.domain.candidate import Candidate
from src.domain.requirement import RequirementSet


def build_reasons(candidate: Candidate, rs: RequirementSet) -> list[str]:
    """Returns one entry per requirement the candidate demonstrably satisfies. Only claims
    supportable by a concrete field on the candidate are included -- no evidence, no reason."""
    reasons: list[str] = []
    candidate_skills_lower = {s.lower() for s in candidate.skills}

    for requirement in rs.requirements:
        text_lower = requirement.text.lower()
        matched_skill = next(
            (skill for skill in candidate.skills if skill.lower() in text_lower), None
        )
        if matched_skill:
            reasons.append(
                f"{requirement.text} — evidenced by skill '{matched_skill}' on profile"
            )

    for company in rs.source_companies:
        if candidate.current_employer.strip().lower() == company.strip().lower():
            reasons.append(
                f"Sourced from a target company ({company}) — currently at {candidate.current_employer}"
            )

    for title in rs.title_equivalents:
        if title.strip().lower() in candidate.headline.strip().lower():
            reasons.append(
                f"Title equivalent match ('{title}') — headline reads '{candidate.headline}'"
            )

    return reasons
