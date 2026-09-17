import pytest

from src.adapters.linkedin_adapter import (
    DEFAULT_MIN_REQUEST_INTERVAL_SECONDS,
    LinkedInAdapter,
    LinkedInParsingError,
    _parse_search_response,
)
from src.adapters.linkedin_session import LinkedInSession
from src.domain.candidate import Candidate, CollectionBasis

FIXTURE_RESPONSE = {
    "data": {
        "elements": [
            {
                "items": [
                    {
                        "item": {
                            "entityResult": {
                                "entityUrn": "urn:li:fsd_entityResultViewModel:ACoAABc123",
                                "title": {"text": "Jamie Rivera"},
                                "primarySubtitle": {"text": "Senior Backend Engineer at Acme Corp"},
                                "secondarySubtitle": {"text": "Austin, Texas, United States"},
                                "navigationUrl": "https://www.linkedin.com/in/jamie-rivera-123/",
                            }
                        }
                    },
                    {
                        "item": {
                            "entityResult": {
                                "entityUrn": "urn:li:fsd_entityResultViewModel:ACoAABd456",
                                "title": {"text": "Morgan Lee"},
                                "primarySubtitle": {"text": "Staff Engineer"},
                                "secondarySubtitle": {"text": "Remote"},
                                "navigationUrl": None,
                            }
                        }
                    },
                ]
            }
        ]
    }
}

MALFORMED_RESPONSE = {"data": {"unexpected_key": []}}
MALFORMED_PROFILE_RESPONSE = {
    "data": {"elements": [{"items": [{"item": {"entityResult": {"title": {"text": "No URN Here"}}}}]}]}
}


def make_session() -> LinkedInSession:
    return LinkedInSession(li_at="fake-li-at-value", jsessionid='"fake-jsessionid-value"')


def fake_http_get_factory(response: dict):
    calls = []

    def fake_http_get(url: str, params: dict, headers: dict) -> dict:
        calls.append((url, params, headers))
        return response

    fake_http_get.calls = calls
    return fake_http_get


def test_parse_search_response_extracts_all_candidates():
    candidates = _parse_search_response(FIXTURE_RESPONSE, "backend engineer")
    assert len(candidates) == 2
    assert candidates[0].name == "Jamie Rivera"
    assert candidates[0].current_employer == "Acme Corp"
    assert candidates[1].name == "Morgan Lee"


def test_parse_search_response_falls_back_to_generated_url_when_navigation_url_missing():
    candidates = _parse_search_response(FIXTURE_RESPONSE, "x")
    morgan = next(c for c in candidates if c.name == "Morgan Lee")
    assert morgan.source_url.startswith("https://www.linkedin.com/in/")


def test_every_parsed_candidate_passes_cr8_validation():
    candidates = _parse_search_response(FIXTURE_RESPONSE, "backend engineer")
    for candidate in candidates:
        assert isinstance(candidate, Candidate)
        assert candidate.collection_basis == CollectionBasis.PERSONAL_USE_SCRAPE
        assert candidate.source_url
        assert candidate.source_name == "linkedin"
        assert candidate.collected_at is not None


def test_malformed_top_level_response_raises_typed_error():
    with pytest.raises(LinkedInParsingError):
        _parse_search_response(MALFORMED_RESPONSE, "x")


def test_malformed_profile_entry_raises_typed_error_not_partial_candidate():
    with pytest.raises(LinkedInParsingError):
        _parse_search_response(MALFORMED_PROFILE_RESPONSE, "x")


def test_adapter_fetch_candidates_uses_injected_http_client():
    fake_get = fake_http_get_factory(FIXTURE_RESPONSE)
    adapter = LinkedInAdapter(
        session=make_session(), http_get=fake_get, min_request_interval_seconds=0
    )
    candidates = adapter.fetch_candidates("backend engineer")
    assert len(candidates) == 2
    assert len(fake_get.calls) == 1
    _, params, headers = fake_get.calls[0]
    assert params["keywords"] == "backend engineer"
    assert "csrf-token" in headers
    assert "li_at=" in headers["cookie"]


def test_adapter_throttles_between_requests():
    fake_get = fake_http_get_factory(FIXTURE_RESPONSE)
    sleep_calls = []
    # _throttle() calls now_fn() once to set _last_request_at on the first call (no elapsed
    # check yet), then twice on the second call: once for the elapsed check, once to re-set
    # _last_request_at.
    fake_now = iter([0.0, 1.0, 1.0])

    adapter = LinkedInAdapter(
        session=make_session(),
        http_get=fake_get,
        min_request_interval_seconds=5.0,
        sleep_fn=lambda seconds: sleep_calls.append(seconds),
        now_fn=lambda: next(fake_now),
    )
    adapter.fetch_candidates("first query")
    adapter.fetch_candidates("second query")

    assert len(sleep_calls) == 1
    assert sleep_calls[0] == pytest.approx(4.0)  # 5.0 min interval - 1.0 elapsed


def test_no_credentials_raises_missing_session_error(monkeypatch, tmp_path):
    from src.adapters.linkedin_session import MissingLinkedInSessionError

    monkeypatch.delenv("LINKEDIN_LI_AT", raising=False)
    monkeypatch.delenv("LINKEDIN_JSESSIONID", raising=False)

    adapter = LinkedInAdapter(
        session=None,
        http_get=fake_http_get_factory(FIXTURE_RESPONSE),
        min_request_interval_seconds=0,
    )
    # Point the lazy loader at a config path that doesn't exist.
    import src.adapters.linkedin_session as session_module

    monkeypatch.setattr(session_module, "DEFAULT_CONFIG_PATH", tmp_path / "does-not-exist.json")

    with pytest.raises(MissingLinkedInSessionError):
        adapter.fetch_candidates("anything")
