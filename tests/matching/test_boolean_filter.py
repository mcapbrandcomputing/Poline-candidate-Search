from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.matching.boolean_filter import filter_candidates


def all_mock_candidates():
    return MockSourceAdapter().fetch_candidates("anything")


def base_requirement_set(**overrides) -> RequirementSet:
    defaults = dict(requirement_set_id="rs1")
    defaults.update(overrides)
    return RequirementSet(**defaults)


def test_golden_path_excludes_matching_employer_and_remote_mismatch():
    """mock-1 and mock-4 work at Acme Corp -- excluded. mock-2 and mock-6 are Remote but the
    role is hybrid -- excluded. mock-3 (New York) and mock-5 (Seattle) survive."""
    rs = base_requirement_set(
        excluded_employers=("Acme Corp",),
        location_policy="hybrid",
    )
    survivors = filter_candidates(rs, all_mock_candidates())
    survivor_ids = {c.candidate_id for c in survivors}
    assert survivor_ids == {"mock-3", "mock-5"}


def test_realistic_sparse_match_degrades_gracefully_to_empty():
    """Stacking excluded_employers with a credential nobody in the mock pool has produces an
    empty (not crashing) result -- proves the engine handles the sparse/zero-survivor case."""
    rs = base_requirement_set(
        excluded_employers=("Acme Corp",),
        credentials=("security clearance",),
    )
    survivors = filter_candidates(rs, all_mock_candidates())
    assert survivors == []


def test_preferred_requirement_never_excludes_a_candidate():
    """Requirement.type=PREFERRED entries are not evaluated by this filter at all -- CR-2."""
    rs = base_requirement_set(
        requirements=(Requirement(text="Kubernetes experience", type=RequirementType.PREFERRED),),
    )
    survivors = filter_candidates(rs, all_mock_candidates())
    assert len(survivors) == len(all_mock_candidates())


def test_credentials_predicate_fails_closed_when_unevidenced():
    rs = base_requirement_set(credentials=("security clearance",))
    survivors = filter_candidates(rs, all_mock_candidates())
    assert survivors == []  # no mock candidate mentions a clearance anywhere


def test_credentials_predicate_passes_when_none_required():
    rs = base_requirement_set(credentials=())
    survivors = filter_candidates(rs, all_mock_candidates())
    assert len(survivors) == len(all_mock_candidates())


def test_remote_policy_never_excludes_on_location():
    rs = base_requirement_set(location_policy="remote")
    survivors = filter_candidates(rs, all_mock_candidates())
    assert len(survivors) == len(all_mock_candidates())


def test_excluded_employers_with_none_sentinel_excludes_nobody():
    rs = base_requirement_set(excluded_employers=("none",))
    survivors = filter_candidates(rs, all_mock_candidates())
    assert len(survivors) == len(all_mock_candidates())
