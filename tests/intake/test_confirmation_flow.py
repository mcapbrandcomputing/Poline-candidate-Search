import time
from pathlib import Path

import pytest

from src.domain.requirement import RequirementSetNotReadyError
from src.intake.confirmation_flow import (
    IntakeIncompleteError,
    confirm_and_save,
    pending_block_a_fields,
    run_cli_walkthrough,
)
from src.nlp.jd_extractor import extract_draft_requirement_set
from src.storage.requirement_store import RequirementStore

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_jds"


@pytest.fixture
def store(tmp_path: Path) -> RequirementStore:
    return RequirementStore(tmp_path / "requirements.jsonl")


@pytest.fixture
def technical_draft():
    jd_text = (FIXTURES_DIR / "technical_role.txt").read_text()
    return extract_draft_requirement_set(jd_text, requirement_set_id="rs-technical")


@pytest.fixture
def sparse_draft():
    jd_text = (FIXTURES_DIR / "sparse_role.txt").read_text()
    return extract_draft_requirement_set(jd_text, requirement_set_id="rs-sparse")


def test_confirm_refuses_when_block_a_field_left_unanswered(sparse_draft, store):
    """Sparse JD leaves nearly every Block A field NOT_FOUND_IN_JD; providing answers for only
    some of them must still refuse to confirm."""
    partial_answers = {"work_authorization": "US citizen required, no sponsorship"}
    with pytest.raises(IntakeIncompleteError):
        confirm_and_save(sparse_draft, partial_answers, store)
    assert store.get("rs-sparse") is None


def test_confirm_succeeds_when_every_block_a_field_answered(sparse_draft, store):
    full_answers = {
        "work_authorization": "US citizen required, no sponsorship",
        "credentials": "none",
        "location_policy": "remote",
        "worksite": "remote",
        "geo_scope": "United States",
        "comp_band": "80-100k",
        "excluded_employers": "Current Employer Inc",
    }
    result = confirm_and_save(sparse_draft, full_answers, store)
    assert result.confirmed is True
    saved = store.get("rs-sparse")
    assert saved is not None
    assert saved.confirmed is True
    assert saved.credentials == ("none",)


def test_confirm_does_not_require_block_b_c_d_answers(technical_draft, store):
    """Technical JD already extracted comp_band/geo_scope/location_policy/work_authorization;
    only credentials and excluded_employers need recruiter input for Block A to be complete."""
    answers = {
        "credentials": "none",
        "excluded_employers": "",
    }
    # excluded_employers left blank is legitimate ("no exclusions") -- but per CR-6 the
    # recruiter must actively say so, so an empty answer for this field is still "answered"
    # here via an explicit sentinel-free non-empty marker.
    answers["excluded_employers"] = "none"
    result = confirm_and_save(technical_draft, answers, store)
    assert result.confirmed is True
    assert result.role_outcomes is None  # Block B untouched, and that's fine


def test_no_bypass_flag_exists_on_public_api(technical_draft, store):
    """CR-6 has no exception path -- confirm_and_save's signature takes no force/skip kwarg."""
    import inspect

    sig = inspect.signature(confirm_and_save)
    assert "force" not in sig.parameters
    assert "skip" not in sig.parameters


def test_run_cli_walkthrough_end_to_end_with_scripted_prompt(technical_draft, store):
    """Scripted prompt_fn simulates a full recruiter answer pass."""
    answers_queue = {
        "credentials": "none",
        "excluded_employers": "none",
    }

    def scripted_prompt(review_line: str) -> str:
        for field_name, answer in answers_queue.items():
            if review_line.startswith(field_name + ":"):
                return answer
        return ""  # accept extracted value as-is

    result = run_cli_walkthrough(technical_draft, store, scripted_prompt)
    assert result.confirmed is True


def test_timed_walkthrough_diagnostic_against_fixture_jd(technical_draft, store):
    """Diagnostic only (not a pass/fail gate on C-4's 3-5 min target) -- reports elapsed time
    for a scripted run-through so the completion report can cite a real number."""
    answers_queue = {"credentials": "none", "excluded_employers": "none"}

    def scripted_prompt(review_line: str) -> str:
        for field_name, answer in answers_queue.items():
            if review_line.startswith(field_name + ":"):
                return answer
        return ""

    start = time.perf_counter()
    result = run_cli_walkthrough(technical_draft, store, scripted_prompt)
    elapsed = time.perf_counter() - start

    assert result.confirmed is True
    print(f"\nScripted walkthrough elapsed: {elapsed:.4f}s (diagnostic only, not a gate)")
