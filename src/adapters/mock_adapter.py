"""Mock source adapter (S1T2). Synthetic fixture data — no network access."""
from __future__ import annotations

from datetime import datetime

from src.adapters.base import SourceAdapter
from src.domain.candidate import Candidate, CollectionBasis

_FIXTURE_CANDIDATES = [
    dict(
        candidate_id="mock-1",
        name="Alex Rivera",
        headline="Senior Backend Engineer",
        current_employer="Acme Corp",
        location="Austin, TX",
        skills=("python", "distributed systems", "postgres"),
    ),
    dict(
        candidate_id="mock-2",
        name="Jordan Lee",
        headline="Staff Software Engineer",
        current_employer="Globex Inc",
        location="Remote",
        skills=("python", "kubernetes", "aws"),
    ),
    dict(
        candidate_id="mock-3",
        name="Sam Patel",
        headline="Engineering Manager",
        current_employer="Initech",
        location="New York, NY",
        skills=("leadership", "python", "system design"),
    ),
    dict(
        candidate_id="mock-4",
        name="Taylor Nguyen",
        headline="Frontend Engineer",
        current_employer="Acme Corp",
        location="Austin, TX",
        skills=("typescript", "react"),
    ),
    dict(
        candidate_id="mock-5",
        name="Morgan Chen",
        headline="Data Engineer",
        current_employer="Umbrella LLC",
        location="Seattle, WA",
        skills=("python", "airflow", "spark"),
    ),
    dict(
        candidate_id="mock-6",
        name="Casey Kim",
        headline="Site Reliability Engineer",
        current_employer="Soylent Corp",
        location="Remote",
        skills=("python", "terraform", "kubernetes"),
    ),
]


class MockSourceAdapter(SourceAdapter):
    """Returns a fixed synthetic candidate set. `query` is accepted but ignored — this adapter
    exists to exercise the matching engine's plumbing, not to simulate search relevance."""

    def fetch_candidates(self, query: str) -> list[Candidate]:
        collected_at = datetime(2026, 9, 17, 12, 0, 0)
        return [
            Candidate(
                source_url=f"https://mock.example/profile/{fixture['candidate_id']}",
                source_name="mock",
                collected_at=collected_at,
                collection_basis=CollectionBasis.PUBLIC_PERMISSIBLE,
                **fixture,
            )
            for fixture in _FIXTURE_CANDIDATES
        ]
