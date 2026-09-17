from pathlib import Path

import pytest

from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.storage.requirement_store import RequirementStore

_READY_BLOCK_A = dict(
    work_authorization="US citizen or authorized",
    credentials=("none",),
    location_policy="remote",
    worksite="remote",
    geo_scope="US",
    comp_band="150-180k",
    excluded_employers=("Current Employer Inc",),
)


@pytest.fixture
def store(tmp_path: Path) -> RequirementStore:
    return RequirementStore(tmp_path / "requirements.jsonl")


def test_write_and_get_round_trip(store: RequirementStore):
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="Python", type=RequirementType.DISQUALIFYING),),
        confirmed=True,
        **_READY_BLOCK_A,
    )
    store.write(rs)
    result = store.get("rs1")
    assert result is not None
    assert result.confirmed is True
    assert result.requirements[0].text == "Python"
    assert result.requirements[0].type == RequirementType.DISQUALIFYING
    assert result.comp_band == "150-180k"


def test_write_upserts_by_id(store: RequirementStore):
    store.write(RequirementSet(requirement_set_id="rs1", comp_band="100k"))
    store.write(RequirementSet(requirement_set_id="rs1", comp_band="200k"))
    assert store.get("rs1").comp_band == "200k"


def test_get_missing_returns_none(store: RequirementStore):
    assert store.get("does-not-exist") is None


def test_persists_across_reload(tmp_path: Path):
    path = tmp_path / "requirements.jsonl"
    RequirementStore(path).write(RequirementSet(requirement_set_id="rs1", comp_band="100k"))
    reloaded = RequirementStore(path).get("rs1")
    assert reloaded.comp_band == "100k"
