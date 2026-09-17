"""Boolean disqualifying-filter engine (S3T6). See requirements.md CR-1, CR-2 and
decisions.md D-03: disqualifying requirements are boolean filters evaluated before any
semantic operation; preferred requirements never affect this filter's output membership.

Missing-data policy (documented per predicate, per the S3T6 brief -- Candidate (S1T1) does not
carry every field a real recruiter would ask about, since most of it is invisible on a scraped
profile):

| Predicate            | Behavior when candidate data is insufficient to evaluate | Why |
|----------------------|------------------------------------------------------------|-----|
| work_authorization    | fail-open (never excludes)                                  | No field on Candidate carries this; almost never stated on a public profile. Tracked as a real gap -- see plan/backlog.md. |
| credentials           | fail-closed if RequirementSet lists any required credential and none appears in the candidate's skills/headline | A legally-required credential that isn't evidenced anywhere on the profile is the closest signal available; recruiter still reviews manually. |
| geo_scope             | fail-open (never excludes)                                  | Candidate.location is a free-text city/state string with no country field; cannot reliably check "United States" membership from it. |
| location_policy       | fail-closed only when policy is hybrid/onsite AND the candidate's location text says "remote"; otherwise fail-open | The one signal a scraped location string can support: a self-described remote worker cannot fill an explicitly onsite/hybrid seat. |
| comp_band             | fail-open (never excludes)                                  | No compensation-expectation field exists on Candidate; not present on scraped profiles. |
| excluded_employers    | fail-closed if candidate.current_employer matches an excluded employer | Fully supported by Candidate.current_employer; this is a real, precise signal. |
"""
from __future__ import annotations

from src.domain.candidate import Candidate
from src.domain.requirement import RequirementSet


def _fails_excluded_employers(candidate: Candidate, rs: RequirementSet) -> bool:
    if not rs.excluded_employers:
        return False
    excluded_lower = {e.strip().lower() for e in rs.excluded_employers if e.strip().lower() != "none"}
    return candidate.current_employer.strip().lower() in excluded_lower


def _fails_credentials(candidate: Candidate, rs: RequirementSet) -> bool:
    required = {c.strip().lower() for c in rs.credentials if c.strip().lower() != "none"}
    if not required:
        return False
    haystack = " ".join([candidate.headline, *candidate.skills]).lower()
    return not any(credential in haystack for credential in required)


def _fails_location_policy(candidate: Candidate, rs: RequirementSet) -> bool:
    if rs.location_policy not in ("hybrid", "onsite"):
        return False
    return "remote" in candidate.location.strip().lower()


def _fails_work_authorization(candidate: Candidate, rs: RequirementSet) -> bool:
    return False  # fail-open -- see module docstring table


def _fails_geo_scope(candidate: Candidate, rs: RequirementSet) -> bool:
    return False  # fail-open -- see module docstring table


def _fails_comp_band(candidate: Candidate, rs: RequirementSet) -> bool:
    return False  # fail-open -- see module docstring table


_PREDICATES = (
    _fails_excluded_employers,
    _fails_credentials,
    _fails_location_policy,
    _fails_work_authorization,
    _fails_geo_scope,
    _fails_comp_band,
)


def _fails_any_disqualifying_requirement(candidate: Candidate, rs: RequirementSet) -> bool:
    return any(predicate(candidate, rs) for predicate in _PREDICATES)


def filter_candidates(rs: RequirementSet, candidates: list[Candidate]) -> list[Candidate]:
    """Return the subset of `candidates` that fail zero disqualifying requirements (CR-1).

    `Requirement`s typed PREFERRED never affect membership here (CR-2) -- only the dedicated
    Block A predicates above (all of which correspond to disqualifying-by-definition intake
    fields) are evaluated. Free-text `requirements[]` entries typed DISQUALIFYING are not yet
    machine-evaluable (no structured field to check them against) and are intentionally not
    applied as a filter here -- flagged as a known limitation, not silently ignored.
    """
    return [c for c in candidates if not _fails_any_disqualifying_requirement(c, rs)]
