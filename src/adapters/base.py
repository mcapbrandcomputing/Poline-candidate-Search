"""Source adapter interface (S1T2). See neshama/context/requirements.md CR-9.

Everything outside src/adapters/ depends only on this interface — adding or removing an
adapter must never require touching the matching engine, schema, or UI.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.candidate import Candidate


class SourceAdapter(ABC):
    """One integration to an external candidate source."""

    @abstractmethod
    def fetch_candidates(self, query: str) -> list[Candidate]:
        """Return Candidate records matching `query`. Must raise, not return partial/invalid
        records, on unexpected source structure."""
        raise NotImplementedError
