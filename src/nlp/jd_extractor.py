"""JD -> draft RequirementSet extraction (S2T4). Deterministic, local, no network calls.

See neshama/context/requirements.md CR-6, CR-7, and neshama/context/decisions.md D-05: the JD
is a seed, never a trusted input. Every Block A field is either populated from the JD or set to
the NOT_FOUND_IN_JD sentinel — never silently left blank or guessed.
"""
from __future__ import annotations

import re
import uuid

from src.domain.requirement import NOT_FOUND_IN_JD, Requirement, RequirementSet, RequirementType

_BULLET_LINE = re.compile(r"^\s*[-*•]\s*(.+)$")

_WORK_AUTH_PATTERN = re.compile(
    r"(authorized to work|work authorization|visa sponsorship|will sponsor|"
    r"require sponsorship)",
    re.IGNORECASE,
)
_SPONSOR_PATTERN = re.compile(r"(will sponsor|sponsorship (is|available))", re.IGNORECASE)

_REMOTE_PATTERN = re.compile(r"\bremote\b", re.IGNORECASE)
_HYBRID_PATTERN = re.compile(r"\bhybrid\b", re.IGNORECASE)
_ONSITE_PATTERN = re.compile(r"\b(onsite|on-site|in[- ]office)\b", re.IGNORECASE)
_HYBRID_DAYS_PATTERN = re.compile(r"(\d+)\s*days?\s*(?:per|/|a)\s*week", re.IGNORECASE)

_COMP_RANGE_PATTERN = re.compile(
    r"\$\s?[\d,]+(?:k|,000)?\s*(?:-|to|–)\s*\$?\s?[\d,]+(?:k|,000)?", re.IGNORECASE
)

_GEO_US_PATTERN = re.compile(r"\b(united states|u\.s\.|\bUS\b|anywhere in the us)\b", re.IGNORECASE)

_CREDENTIAL_PATTERN = re.compile(
    r"(security clearance|licen[cs]e (?:is )?required|certification (?:is )?required)",
    re.IGNORECASE,
)

_EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*years?", re.IGNORECASE)

_REQUIREMENTS_SECTION = re.compile(
    r"(?:requirements|what you'?ll need|qualifications)\s*:?\s*\n(.*?)(?:\n\s*\n|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def extract_draft_requirement_set(jd_text: str, requirement_set_id: str | None = None) -> RequirementSet:
    """Given raw JD text, return a draft (unconfirmed) RequirementSet. Every Block A field is
    either extracted or explicitly NOT_FOUND_IN_JD (CR-7) -- never None/blank."""
    requirement_set_id = requirement_set_id or str(uuid.uuid4())

    requirements = _extract_requirements(jd_text)
    work_authorization = _extract_work_authorization(jd_text)
    credentials = _extract_credentials(jd_text)
    location_policy, worksite = _extract_location_policy(jd_text)
    geo_scope = _extract_geo_scope(jd_text)
    comp_band = _extract_comp_band(jd_text)
    experience_semantics = _extract_experience_semantics(jd_text)

    return RequirementSet(
        requirement_set_id=requirement_set_id,
        requirements=tuple(requirements),
        work_authorization=work_authorization,
        credentials=credentials,
        location_policy=location_policy,
        worksite=worksite,
        geo_scope=geo_scope,
        comp_band=comp_band,
        excluded_employers=(),  # never present in a JD; always requires recruiter input
        experience_semantics=experience_semantics,
        confirmed=False,
    )


def _extract_requirements(jd_text: str) -> list[Requirement]:
    """Every requirement-shaped bullet defaults to DISQUALIFYING (CR-1's note that JDs list
    ten and usually two are real means the recruiter must actively downgrade, not the other
    way around)."""
    match = _REQUIREMENTS_SECTION.search(jd_text)
    if not match:
        return []
    section = match.group(1)
    requirements = []
    for line in section.splitlines():
        bullet = _BULLET_LINE.match(line)
        if bullet:
            requirements.append(
                Requirement(text=bullet.group(1).strip(), type=RequirementType.DISQUALIFYING)
            )
    return requirements


def _extract_work_authorization(jd_text: str) -> str:
    if not _WORK_AUTH_PATTERN.search(jd_text):
        return NOT_FOUND_IN_JD
    if _SPONSOR_PATTERN.search(jd_text):
        return "authorization required; sponsorship available per JD"
    return "authorization required; sponsorship not mentioned in JD"


def _extract_credentials(jd_text: str) -> tuple[str, ...]:
    """Empty tuple means 'not found in JD' for list-typed fields -- RequirementSet's own
    readiness check already treats an empty tuple as unset (see requirement.py), so list
    fields use () rather than wrapping the NOT_FOUND_IN_JD string sentinel."""
    matches = _CREDENTIAL_PATTERN.findall(jd_text)
    return tuple(sorted(set(m.lower() for m in matches)))


def _extract_location_policy(jd_text: str) -> tuple[str, str]:
    if _REMOTE_PATTERN.search(jd_text):
        return "remote", "remote"
    if _HYBRID_PATTERN.search(jd_text):
        days_match = _HYBRID_DAYS_PATTERN.search(jd_text)
        worksite = f"hybrid, {days_match.group(1)} days/week" if days_match else "hybrid"
        return "hybrid", worksite
    if _ONSITE_PATTERN.search(jd_text):
        return "onsite", "onsite"
    return NOT_FOUND_IN_JD, NOT_FOUND_IN_JD


def _extract_geo_scope(jd_text: str) -> str:
    if _GEO_US_PATTERN.search(jd_text):
        return "United States"
    return NOT_FOUND_IN_JD


def _extract_comp_band(jd_text: str) -> str:
    match = _COMP_RANGE_PATTERN.search(jd_text)
    if not match:
        return NOT_FOUND_IN_JD
    return match.group(0)


def _extract_experience_semantics(jd_text: str) -> str:
    match = _EXPERIENCE_PATTERN.search(jd_text)
    if not match:
        return NOT_FOUND_IN_JD
    return f"JD states {match.group(0)} — recruiter must confirm real floor vs. shorthand (CR per Block C)"
