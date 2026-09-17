"""Real LinkedIn source adapter (S5T10). D-01 is resolved for this personal-use build --
direct scraping is in scope. See neshama/context/decisions.md.

This calls LinkedIn's internal "voyager" search API (the same endpoint linkedin.com's own web
client uses once you're logged in) rather than parsing rendered HTML, since the public search
page is client-side rendered and not reliably scrapable with a plain HTTP client. This is the
approach used by most open-source personal LinkedIn tools. The exact response schema is
undocumented and LinkedIn can change it at any time (C-3 still applies even outside the legal
context) -- `_parse_search_response` isolates all of that fragility in one place and raises
`LinkedInParsingError` on an unrecognized shape rather than silently returning bad data.

IMPORTANT: this file was written and unit-tested against a fixture response shaped like
publicly-documented examples of this API from other open-source projects. It has NOT been
verified against a live LinkedIn response from this environment -- doing so requires your own
session credentials (see docs/linkedin_adapter_setup.md) and should be run manually, once, by
you, so you can watch for anything unexpected. If LinkedIn's actual response shape differs,
`_parse_search_response` is the only place that needs to change.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Callable, Optional

from src.adapters.base import SourceAdapter
from src.adapters.linkedin_session import LinkedInSession, load_session
from src.domain.candidate import Candidate, CollectionBasis

SEARCH_URL = "https://www.linkedin.com/voyager/api/search/dash/clusters"
DEFAULT_MIN_REQUEST_INTERVAL_SECONDS = 3.0
"""Self-throttling for the owner's own account stability -- not a legal requirement here."""

HttpGetFn = Callable[[str, dict, dict], dict]
"""Injected for testability: (url, params, headers) -> parsed JSON dict. Production default
performs a real `requests.get(...).json()` call; tests inject a fixture-returning fake."""


class LinkedInParsingError(RuntimeError):
    """Raised when the voyager API response doesn't match the expected shape -- e.g. LinkedIn
    changed their schema. Never silently returns a partial/invalid Candidate."""


def _real_http_get(url: str, params: dict, headers: dict) -> dict:
    import requests  # imported here so the module has no hard dependency for test-only use

    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


class LinkedInAdapter(SourceAdapter):
    def __init__(
        self,
        session: Optional[LinkedInSession] = None,
        http_get: HttpGetFn = _real_http_get,
        min_request_interval_seconds: float = DEFAULT_MIN_REQUEST_INTERVAL_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
        now_fn: Callable[[], float] = time.monotonic,
    ):
        self._session = session  # lazily loaded via load_session() if None at call time
        self._http_get = http_get
        self._min_interval = min_request_interval_seconds
        self._sleep_fn = sleep_fn
        self._now_fn = now_fn
        self._last_request_at: Optional[float] = None

    def _get_session(self) -> LinkedInSession:
        if self._session is None:
            self._session = load_session()
        return self._session

    def _throttle(self) -> None:
        if self._last_request_at is not None:
            elapsed = self._now_fn() - self._last_request_at
            remaining = self._min_interval - elapsed
            if remaining > 0:
                self._sleep_fn(remaining)
        self._last_request_at = self._now_fn()

    def fetch_candidates(self, query: str) -> list[Candidate]:
        session = self._get_session()
        self._throttle()

        headers = {
            "csrf-token": session.csrf_token,
            "cookie": f"li_at={session.li_at}; JSESSIONID={session.jsessionid}",
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "x-restli-protocol-version": "2.0.0",
        }
        params = {"keywords": query, "origin": "GLOBAL_SEARCH_HEADER"}

        raw = self._http_get(SEARCH_URL, params, headers)
        return _parse_search_response(raw, query)


def _parse_search_response(raw: dict, query: str) -> list[Candidate]:
    """Isolates all of the voyager response's fragile shape in one function. Raises
    LinkedInParsingError (never returns a partial Candidate) if the shape is unrecognized."""
    try:
        elements = raw["data"]["elements"]
    except (KeyError, TypeError) as exc:
        raise LinkedInParsingError(
            f"Unexpected LinkedIn search response shape (missing data.elements): {exc}"
        ) from exc

    candidates: list[Candidate] = []
    collected_at = datetime.utcnow()

    for cluster in elements:
        for item in cluster.get("items", []):
            profile = item.get("item", {}).get("entityResult")
            if profile is None:
                continue
            try:
                candidates.append(_profile_to_candidate(profile, collected_at))
            except (KeyError, TypeError) as exc:
                raise LinkedInParsingError(
                    f"Unexpected LinkedIn profile entry shape for query {query!r}: {exc}"
                ) from exc

    return candidates


def _profile_to_candidate(profile: dict, collected_at: datetime) -> Candidate:
    entity_urn = profile["entityUrn"]
    candidate_id = entity_urn.split(":")[-1]
    name = profile["title"]["text"]
    headline = profile.get("primarySubtitle", {}).get("text", "")
    location = profile.get("secondarySubtitle", {}).get("text", "")
    profile_url = profile.get("navigationUrl") or f"https://www.linkedin.com/in/{candidate_id}/"

    return Candidate(
        candidate_id=candidate_id,
        name=name,
        headline=headline,
        current_employer=_employer_from_headline(headline),
        location=location,
        skills=(),  # not present in search results; would need a per-profile fetch
        source_url=profile_url,
        source_name="linkedin",
        collected_at=collected_at,
        collection_basis=CollectionBasis.PERSONAL_USE_SCRAPE,
    )


def _employer_from_headline(headline: str) -> str:
    """Best-effort: LinkedIn headlines are often 'Title at Company'. Falls back to the full
    headline if the pattern doesn't match -- never raises."""
    if " at " in headline:
        return headline.split(" at ", 1)[1].strip()
    return headline
