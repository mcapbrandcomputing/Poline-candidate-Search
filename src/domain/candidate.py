"""Candidate record schema (S1T1). See neshama/context/requirements.md CR-8, CR-10."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import Optional


class CollectionBasis(str, Enum):
    """Legal/source basis under which a candidate record was collected (CR-8)."""

    LICENSED = "licensed"
    PUBLIC_PERMISSIBLE = "public-permissible"
    CANDIDATE_SUBMITTED = "candidate-submitted"
    PERSONAL_USE_SCRAPE = "personal-use-scrape"


class MissingCollectionBasisError(ValueError):
    """Raised when a Candidate is constructed without a collection_basis (CR-8)."""


@dataclass(frozen=True)
class Candidate:
    """A sourced candidate profile. Immutable; use `with_suppressed`/`with_deleted` to update.

    CR-8 fields (source_url, source_name, collected_at, collection_basis) are mandatory.
    `suppressed`/`deleted_at` support S4T9's suppression/deletion pipeline (CR-10).
    """

    candidate_id: str
    name: str
    headline: str
    current_employer: str
    location: str
    skills: tuple[str, ...]
    source_url: str
    source_name: str
    collected_at: datetime
    collection_basis: CollectionBasis
    suppressed: bool = False
    deleted_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.collection_basis is None:
            raise MissingCollectionBasisError(
                f"Candidate {self.candidate_id!r} is missing collection_basis (CR-8)"
            )
        if not isinstance(self.collection_basis, CollectionBasis):
            raise MissingCollectionBasisError(
                f"Candidate {self.candidate_id!r} has invalid collection_basis: "
                f"{self.collection_basis!r}"
            )
        if not self.source_url:
            raise MissingCollectionBasisError(
                f"Candidate {self.candidate_id!r} is missing source_url (CR-8)"
            )
        if not self.source_name:
            raise MissingCollectionBasisError(
                f"Candidate {self.candidate_id!r} is missing source_name (CR-8)"
            )
        if self.collected_at is None:
            raise MissingCollectionBasisError(
                f"Candidate {self.candidate_id!r} is missing collected_at (CR-8)"
            )

    def is_visible(self) -> bool:
        """False if suppressed or deleted — the store's read helpers must honor this (CR-10)."""
        return not self.suppressed and self.deleted_at is None

    def with_suppressed(self, suppressed: bool = True) -> "Candidate":
        return replace(self, suppressed=suppressed)

    def with_deleted(self, deleted_at: datetime) -> "Candidate":
        return replace(self, deleted_at=deleted_at)
