import pytest

from src.domain.requirement import (
    NOT_FOUND_IN_JD,
    InvalidRequirementTypeError,
    Requirement,
    RequirementSet,
    RequirementSetNotReadyError,
    RequirementType,
)

_READY_BLOCK_A = dict(
    work_authorization="US citizen or authorized",
    credentials=("none",),
    location_policy="remote",
    worksite="remote",
    geo_scope="US",
    comp_band="150-180k",
    excluded_employers=("Current Employer Inc",),
)


def test_requirement_accepts_disqualifying_type():
    req = Requirement(text="5+ years Python", type=RequirementType.DISQUALIFYING)
    assert req.type == RequirementType.DISQUALIFYING


def test_requirement_accepts_preferred_type():
    req = Requirement(text="Kubernetes experience", type=RequirementType.PREFERRED)
    assert req.type == RequirementType.PREFERRED


def test_requirement_rejects_invalid_type_string():
    with pytest.raises(InvalidRequirementTypeError):
        Requirement(text="whatever", type="not-a-real-type")


def test_requirement_set_cannot_be_confirmed_with_unset_block_a_field():
    with pytest.raises(RequirementSetNotReadyError):
        RequirementSet(requirement_set_id="rs1", confirmed=True)


def test_requirement_set_cannot_be_confirmed_with_not_found_sentinel():
    with pytest.raises(RequirementSetNotReadyError):
        RequirementSet(
            requirement_set_id="rs1",
            confirmed=True,
            **{**_READY_BLOCK_A, "work_authorization": NOT_FOUND_IN_JD},
        )


def test_requirement_set_can_be_confirmed_when_block_a_fully_set():
    rs = RequirementSet(requirement_set_id="rs1", confirmed=True, **_READY_BLOCK_A)
    assert rs.confirmed is True
    assert rs.is_ready_for_search() is True


def test_requirement_set_ready_even_with_block_b_c_d_empty():
    """Block B/C/D fields are not disqualifying-gated per CR-6."""
    rs = RequirementSet(requirement_set_id="rs1", confirmed=True, **_READY_BLOCK_A)
    assert rs.role_outcomes is None
    assert rs.positive_exemplars == ()
    assert rs.is_ready_for_search() is True


def test_with_confirmed_helper():
    rs = RequirementSet(requirement_set_id="rs1", **_READY_BLOCK_A).with_confirmed()
    assert rs.confirmed is True
