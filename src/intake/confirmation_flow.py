"""Recruiter intake confirmation flow (S2T5). CLI walkthrough over a draft RequirementSet.

CR-6: cannot reach confirmed=True while any Block A field is unset/NOT_FOUND_IN_JD. This
module never bypasses that -- it calls RequirementSet's own constructor/`with_confirmed`,
which raises RequirementSetNotReadyError if the caller tries to skip ahead (see
requirement.py). C-4: the flow should be answerable in 3-5 minutes; `answers` is expected to
be pre-collected (e.g. from a CLI prompt loop in a real terminal) and passed in as a plain
dict, so this module is trivially testable non-interactively.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable

from src.domain.requirement import NOT_FOUND_IN_JD, RequirementSet, RequirementSetNotReadyError
from src.storage.requirement_store import RequirementStore

BLOCK_A_FIELDS = (
    "work_authorization",
    "credentials",
    "location_policy",
    "worksite",
    "geo_scope",
    "comp_band",
    "excluded_employers",
)

ALL_INTAKE_FIELDS = BLOCK_A_FIELDS + (
    "role_outcomes",
    "seat_history",
    "prior_search_failure",
    "scope_level",
    "environment",
    "positive_exemplars",
    "negative_exemplar",
    "source_companies",
    "title_equivalents",
    "experience_semantics",
    "batch_size",
    "ats_dedupe_policy",
    "freshness_floor",
)


TUPLE_FIELDS = frozenset(
    {
        "credentials",
        "excluded_employers",
        "environment",
        "positive_exemplars",
        "source_companies",
        "title_equivalents",
    }
)


class IntakeIncompleteError(ValueError):
    """Raised when confirm_and_save is called while a Block A field is still unanswered."""


def field_is_unanswered(value) -> bool:
    return value is None or value == () or value == NOT_FOUND_IN_JD


def pending_block_a_fields(draft: RequirementSet) -> list[str]:
    """Fields CR-6 still requires an explicit answer for."""
    return [f for f in BLOCK_A_FIELDS if field_is_unanswered(getattr(draft, f))]


def render_field_for_review(draft: RequirementSet, field_name: str) -> str:
    """Recruiter-facing rendering of one field's current (possibly extracted) value -- makes
    the NOT_FOUND_IN_JD sentinel visible as an explicit prompt, per CR-7."""
    value = getattr(draft, field_name)
    if field_is_unanswered(value):
        return f"{field_name}: not found in JD — please provide"
    return f"{field_name}: {value} (confirm or correct)"


def _coerce_answer(field_name: str, value):
    """CLI answers arrive as strings; tuple-typed fields need splitting on comma so the
    RequirementSet's own tuple/() unset-check behaves correctly."""
    if field_name in TUPLE_FIELDS and isinstance(value, str):
        return tuple(part.strip() for part in value.split(",") if part.strip())
    return value


def apply_answers(draft: RequirementSet, answers: dict) -> RequirementSet:
    """Merge recruiter-supplied answers into the draft. Only fields present in `answers` are
    overwritten; anything not answered keeps its extracted/blank value."""
    updates = {
        k: _coerce_answer(k, v) for k, v in answers.items() if k in ALL_INTAKE_FIELDS
    }
    return replace(draft, **updates)


def confirm_and_save(
    draft: RequirementSet,
    answers: dict,
    store: RequirementStore,
) -> RequirementSet:
    """Apply answers, then attempt to mark the result confirmed and persist it.

    Raises IntakeIncompleteError (not RequirementSetNotReadyError directly) if a Block A field
    is still unanswered after applying `answers` -- CR-6 has no bypass path, flag/env var, or
    "skip" shortcut.
    """
    updated = apply_answers(draft, answers)
    pending = pending_block_a_fields(updated)
    if pending:
        raise IntakeIncompleteError(
            "Cannot confirm intake -- Block A fields still unanswered: " + ", ".join(pending)
        )
    try:
        confirmed = updated.with_confirmed()
    except RequirementSetNotReadyError as exc:
        # Defensive: pending_block_a_fields should already have caught this.
        raise IntakeIncompleteError(str(exc)) from exc
    store.write(confirmed)
    return confirmed


def run_cli_walkthrough(
    draft: RequirementSet,
    store: RequirementStore,
    prompt_fn: Callable[[str], str],
) -> RequirementSet:
    """Interactive walkthrough for a real terminal. `prompt_fn` is injected so this function is
    unit-testable (tests pass a canned prompt_fn instead of real stdin)."""
    answers: dict = {}
    for field_name in ALL_INTAKE_FIELDS:
        review_line = render_field_for_review(draft, field_name)
        response = prompt_fn(review_line)
        if response.strip():
            answers[field_name] = response
    return confirm_and_save(draft, answers, store)
