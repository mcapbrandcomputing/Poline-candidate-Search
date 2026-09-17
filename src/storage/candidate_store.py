"""Candidate persistence primitives (S1T1). File-based JSON store, one record per line."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator

from src.domain.candidate import Candidate, CollectionBasis


class CandidateStore:
    """Append-oriented JSONL store for Candidate records.

    Writing a candidate with an id that already exists overwrites the prior record (used for
    suppression/deletion state changes and adapter re-ingestion). Read helpers exclude any
    record where `is_visible()` is False, per CR-10 — suppressed/deleted candidates never come
    back through the standard read path.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def _read_all_raw(self) -> dict[str, Candidate]:
        records: dict[str, Candidate] = {}
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            candidate = _candidate_from_dict(json.loads(line))
            records[candidate.candidate_id] = candidate
        return records

    def write(self, candidate: Candidate) -> None:
        """Upsert a candidate record by candidate_id."""
        records = self._read_all_raw()
        records[candidate.candidate_id] = candidate
        self._write_all(records)

    def _write_all(self, records: dict[str, Candidate]) -> None:
        lines = [json.dumps(_candidate_to_dict(c)) for c in records.values()]
        self.path.write_text("\n".join(lines) + ("\n" if lines else ""))

    def get(self, candidate_id: str) -> Candidate | None:
        """Returns None if absent OR if the record is suppressed/deleted (CR-10)."""
        record = self._read_all_raw().get(candidate_id)
        if record is None or not record.is_visible():
            return None
        return record

    def get_including_hidden(self, candidate_id: str) -> Candidate | None:
        """Bypasses the CR-10 visibility filter — for suppression/deletion pipeline use only."""
        return self._read_all_raw().get(candidate_id)

    def list_visible(self) -> Iterator[Candidate]:
        """Standard read path — excludes suppressed/deleted records (CR-10)."""
        for record in self._read_all_raw().values():
            if record.is_visible():
                yield record


def _candidate_to_dict(candidate: Candidate) -> dict:
    data = asdict(candidate)
    data["collection_basis"] = candidate.collection_basis.value
    data["collected_at"] = candidate.collected_at.isoformat()
    data["deleted_at"] = candidate.deleted_at.isoformat() if candidate.deleted_at else None
    data["skills"] = list(candidate.skills)
    return data


def _candidate_from_dict(data: dict) -> Candidate:
    return Candidate(
        candidate_id=data["candidate_id"],
        name=data["name"],
        headline=data["headline"],
        current_employer=data["current_employer"],
        location=data["location"],
        skills=tuple(data["skills"]),
        source_url=data["source_url"],
        source_name=data["source_name"],
        collected_at=datetime.fromisoformat(data["collected_at"]),
        collection_basis=CollectionBasis(data["collection_basis"]),
        suppressed=data.get("suppressed", False),
        deleted_at=datetime.fromisoformat(data["deleted_at"]) if data.get("deleted_at") else None,
    )
