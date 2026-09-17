"""Requirement / RequirementSet schema (S1T3). See neshama/context/requirements.md CR-1,
CR-6, CR-7, and the recruiter intake instrument table (Blocks A-D)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional

NOT_FOUND_IN_JD = "__NOT_FOUND_IN_JD__"
"""Sentinel distinguishing 'JD said nothing here' from an empty/unset value (CR-7)."""


class RequirementType(str, Enum):
    DISQUALIFYING = "disqualifying"
    PREFERRED = "preferred"


class InvalidRequirementTypeError(ValueError):
    pass


class RequirementSetNotReadyError(ValueError):
    """Raised when a RequirementSet is marked ready/confirmed with an unset Block A field."""


@dataclass(frozen=True)
class Requirement:
    """One requirement extracted from, or added to, a requisition."""

    text: str
    type: RequirementType

    def __post_init__(self) -> None:
        if not isinstance(self.type, RequirementType):
            raise InvalidRequirementTypeError(
                f"Requirement.type must be a RequirementType, got {self.type!r}"
            )


# Block A fields (CR-1's disqualifying filters) — every one must be set before a
# RequirementSet can be marked ready/confirmed (CR-6).
_BLOCK_A_FIELDS = (
    "work_authorization",
    "credentials",
    "location_policy",
    "worksite",
    "geo_scope",
    "comp_band",
    "excluded_employers",
)


@dataclass(frozen=True)
class RequirementSet:
    """One requisition's full intake state — Blocks A-D. See requirements.md for field
    provenance. `confirmed=True` may only be set once every Block A field is populated
    (not None and not NOT_FOUND_IN_JD) — the data-layer half of CR-6/CR-7."""

    requirement_set_id: str
    requirements: tuple[Requirement, ...] = ()

    # Block A — disqualifying filters
    work_authorization: Optional[str] = None
    credentials: tuple[str, ...] = ()
    location_policy: Optional[str] = None
    worksite: Optional[str] = None
    geo_scope: Optional[str] = None
    comp_band: Optional[str] = None
    excluded_employers: tuple[str, ...] = ()

    # Block B — what the role actually is
    role_outcomes: Optional[str] = None
    seat_history: Optional[str] = None
    prior_search_failure: Optional[str] = None
    scope_level: Optional[str] = None
    environment: tuple[str, ...] = ()

    # Block C — calibration
    positive_exemplars: tuple[str, ...] = ()
    negative_exemplar: Optional[str] = None
    source_companies: tuple[str, ...] = ()
    title_equivalents: tuple[str, ...] = ()
    experience_semantics: Optional[str] = None

    # Block D — search behavior
    batch_size: Optional[int] = None
    ats_dedupe_policy: Optional[str] = None
    freshness_floor: Optional[str] = None

    confirmed: bool = False

    def __post_init__(self) -> None:
        if self.confirmed:
            unset = self._unset_block_a_fields()
            if unset:
                raise RequirementSetNotReadyError(
                    "Cannot mark RequirementSet confirmed=True while Block A fields are "
                    f"unset: {', '.join(unset)} (CR-6)"
                )

    def _unset_block_a_fields(self) -> list[str]:
        unset = []
        for field_name in _BLOCK_A_FIELDS:
            value = getattr(self, field_name)
            if value is None or value == () or value == NOT_FOUND_IN_JD:
                unset.append(field_name)
        return unset

    def is_ready_for_search(self) -> bool:
        return self.confirmed and not self._unset_block_a_fields()

    def with_confirmed(self) -> "RequirementSet":
        return replace(self, confirmed=True)
