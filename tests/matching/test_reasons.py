from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.matching.reasons import build_reasons


def get_candidate(candidate_id: str):
    return next(c for c in MockSourceAdapter().fetch_candidates("x") if c.candidate_id == candidate_id)


def test_reason_generated_for_matching_skill_requirement():
    candidate = get_candidate("mock-1")  # skills: python, distributed systems, postgres
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="5+ years python", type=RequirementType.DISQUALIFYING),),
    )
    reasons = build_reasons(candidate, rs)
    assert len(reasons) == 1
    assert "python" in reasons[0].lower()


def test_no_reason_when_no_requirement_matches():
    candidate = get_candidate("mock-4")  # skills: typescript, react
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="5+ years python", type=RequirementType.DISQUALIFYING),),
    )
    reasons = build_reasons(candidate, rs)
    assert reasons == []


def test_reason_generated_for_source_company_match():
    candidate = get_candidate("mock-1")  # current_employer: Acme Corp
    rs = RequirementSet(requirement_set_id="rs1", source_companies=("Acme Corp",))
    reasons = build_reasons(candidate, rs)
    assert any("Acme Corp" in r for r in reasons)


def test_reason_generated_for_title_equivalent_match():
    candidate = get_candidate("mock-3")  # headline: Engineering Manager
    rs = RequirementSet(requirement_set_id="rs1", title_equivalents=("Engineering Manager",))
    reasons = build_reasons(candidate, rs)
    assert any("Engineering Manager" in r for r in reasons)
