"""RequirementSet persistence (S1T3). Style-consistent with candidate_store.py."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from src.domain.requirement import Requirement, RequirementSet, RequirementType


class RequirementStore:
    """JSONL upsert store for RequirementSet records, keyed by requirement_set_id."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def _read_all(self) -> dict[str, RequirementSet]:
        records: dict[str, RequirementSet] = {}
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            rs = _requirement_set_from_dict(json.loads(line))
            records[rs.requirement_set_id] = rs
        return records

    def write(self, requirement_set: RequirementSet) -> None:
        records = self._read_all()
        records[requirement_set.requirement_set_id] = requirement_set
        lines = [json.dumps(_requirement_set_to_dict(rs)) for rs in records.values()]
        self.path.write_text("\n".join(lines) + ("\n" if lines else ""))

    def get(self, requirement_set_id: str) -> RequirementSet | None:
        return self._read_all().get(requirement_set_id)


def _requirement_set_to_dict(rs: RequirementSet) -> dict:
    data = asdict(rs)
    data["requirements"] = [{"text": r.text, "type": r.type.value} for r in rs.requirements]
    for tuple_field in (
        "credentials",
        "excluded_employers",
        "environment",
        "positive_exemplars",
        "source_companies",
        "title_equivalents",
    ):
        data[tuple_field] = list(getattr(rs, tuple_field))
    return data


def _requirement_set_from_dict(data: dict) -> RequirementSet:
    data = dict(data)
    data["requirements"] = tuple(
        Requirement(text=r["text"], type=RequirementType(r["type"]))
        for r in data.get("requirements", [])
    )
    for tuple_field in (
        "credentials",
        "excluded_employers",
        "environment",
        "positive_exemplars",
        "source_companies",
        "title_equivalents",
    ):
        data[tuple_field] = tuple(data.get(tuple_field, ()))
    return RequirementSet(**data)
