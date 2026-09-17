from pathlib import Path

import pytest

from src.domain.requirement import NOT_FOUND_IN_JD, RequirementType
from src.nlp.jd_extractor import extract_draft_requirement_set

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_jds"

_BLOCK_A_FIELD_NAMES = [
    "work_authorization",
    "location_policy",
    "worksite",
    "geo_scope",
    "comp_band",
]


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


@pytest.mark.parametrize(
    "fixture_name", ["technical_role.txt", "nontechnical_role.txt", "sparse_role.txt"]
)
def test_every_block_a_scalar_field_is_populated_or_explicitly_not_found(fixture_name):
    jd_text = load_fixture(fixture_name)
    rs = extract_draft_requirement_set(jd_text)
    for field_name in _BLOCK_A_FIELD_NAMES:
        value = getattr(rs, field_name)
        assert value is not None, f"{field_name} was None, must be a value or NOT_FOUND_IN_JD"
        assert value != "", f"{field_name} was empty string, must be a value or NOT_FOUND_IN_JD"


def test_extraction_result_is_never_confirmed():
    rs = extract_draft_requirement_set(load_fixture("technical_role.txt"))
    assert rs.confirmed is False


def test_extracted_requirements_default_to_disqualifying():
    rs = extract_draft_requirement_set(load_fixture("technical_role.txt"))
    assert len(rs.requirements) > 0
    assert all(r.type == RequirementType.DISQUALIFYING for r in rs.requirements)


def test_technical_role_extracts_hybrid_and_comp_and_geo():
    rs = extract_draft_requirement_set(load_fixture("technical_role.txt"))
    assert rs.location_policy == "hybrid"
    assert "3 days" in rs.worksite
    assert rs.geo_scope == "United States"
    assert rs.comp_band != NOT_FOUND_IN_JD
    assert rs.work_authorization != NOT_FOUND_IN_JD


def test_nontechnical_role_extracts_remote_and_comp():
    rs = extract_draft_requirement_set(load_fixture("nontechnical_role.txt"))
    assert rs.location_policy == "remote"
    assert rs.comp_band != NOT_FOUND_IN_JD


def test_sparse_jd_does_not_crash_and_produces_valid_draft():
    jd_text = load_fixture("sparse_role.txt")
    rs = extract_draft_requirement_set(jd_text)
    assert rs is not None
    assert rs.confirmed is False
    # A sparse JD legitimately yields mostly NOT_FOUND_IN_JD -- the point is it doesn't crash
    # and every field still holds an explicit value.
    for field_name in _BLOCK_A_FIELD_NAMES:
        assert getattr(rs, field_name) is not None
