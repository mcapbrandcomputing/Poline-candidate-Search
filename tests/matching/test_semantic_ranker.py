from src.adapters.mock_adapter import MockSourceAdapter
from src.domain.requirement import Requirement, RequirementSet, RequirementType
from src.matching.semantic_ranker import score_candidates


def test_candidate_with_more_overlapping_terms_scores_higher():
    candidates = MockSourceAdapter().fetch_candidates("x")
    rs = RequirementSet(
        requirement_set_id="rs1",
        requirements=(Requirement(text="python kubernetes", type=RequirementType.DISQUALIFYING),),
    )
    scores = score_candidates(candidates, rs)
    # mock-2 has python + kubernetes; mock-4 has neither
    assert scores["mock-2"] > scores["mock-4"]


def test_no_signal_terms_yields_zero_scores():
    candidates = MockSourceAdapter().fetch_candidates("x")
    rs = RequirementSet(requirement_set_id="rs1")
    scores = score_candidates(candidates, rs)
    assert all(score == 0.0 for score in scores.values())


def test_score_covers_every_input_candidate():
    candidates = MockSourceAdapter().fetch_candidates("x")
    rs = RequirementSet(requirement_set_id="rs1")
    scores = score_candidates(candidates, rs)
    assert set(scores.keys()) == {c.candidate_id for c in candidates}
