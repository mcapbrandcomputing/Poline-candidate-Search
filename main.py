"""End-to-end CLI entry point tying Sprints 1-5 together: JD text -> extraction -> recruiter
confirmation -> source adapter -> boolean filter + ranking -> non-ranked shortlist.

Usage:
    .venv/bin/python main.py path/to/jd.txt                  # interactive confirmation
    .venv/bin/python main.py path/to/jd.txt --auto            # non-interactive demo mode
    .venv/bin/python main.py path/to/jd.txt --source linkedin # real LinkedIn adapter (needs
                                                                # credentials, see
                                                                # docs/linkedin_adapter_setup.md)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.adapters.registry import get, register_linkedin_adapter
from src.domain.requirement import NOT_FOUND_IN_JD
from src.intake.confirmation_flow import confirm_and_save, pending_block_a_fields, run_cli_walkthrough
from src.matching.search import run_search
from src.nlp.jd_extractor import extract_draft_requirement_set
from src.shortlist.render import render_shortlist
from src.storage.audit_store import AuditStore
from src.storage.requirement_store import RequirementStore

DATA_DIR = Path("data")

_AUTO_DEMO_ANSWERS = {
    "work_authorization": "US citizen or authorized, no sponsorship",
    "credentials": "none",
    "location_policy": "remote",
    "worksite": "remote",
    "geo_scope": "United States",
    "comp_band": "not specified",
    "excluded_employers": "none",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Candidate sourcing tool -- end-to-end demo run.")
    parser.add_argument("jd_file", type=Path, help="Path to a job description text file.")
    parser.add_argument(
        "--source", default="mock", help="Registered source adapter name (default: mock)."
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Non-interactive demo mode: auto-fills any still-missing Block A field with a "
        "placeholder answer instead of prompting. For a real run, omit this flag.",
    )
    args = parser.parse_args()

    jd_text = args.jd_file.read_text()
    draft = extract_draft_requirement_set(jd_text)

    DATA_DIR.mkdir(exist_ok=True)
    requirement_store = RequirementStore(DATA_DIR / "requirements.jsonl")
    audit_store = AuditStore(DATA_DIR / "audit.jsonl")

    if args.source == "linkedin":
        register_linkedin_adapter()

    if args.auto:
        pending = pending_block_a_fields(draft)
        answers = {f: _AUTO_DEMO_ANSWERS.get(f, "not specified") for f in pending}
        print(f"[--auto] Auto-filling {len(pending)} still-missing Block A field(s): {pending}")
        confirmed = confirm_and_save(draft, answers, requirement_store)
    else:
        def prompt(review_line: str) -> str:
            return input(review_line + "\n> ")

        confirmed = run_cli_walkthrough(draft, requirement_store, prompt)

    query = " ".join(r.text for r in confirmed.requirements) or "candidate"
    adapter = get(args.source)
    candidates = adapter.fetch_candidates(query)

    result = run_search(confirmed, candidates, audit_store, user_id="owner")
    print()
    print(render_shortlist(result))


if __name__ == "__main__":
    main()
