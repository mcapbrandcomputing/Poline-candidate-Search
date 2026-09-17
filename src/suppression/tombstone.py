"""Deletion tombstone guard (S4T9). See requirements.md CR-10: deletion must not be reversed
by a subsequent crawl. A separate append-only tombstone file (not the candidate store itself)
survives even if a re-ingestion write would otherwise recreate the candidate row."""
from __future__ import annotations

import json
from pathlib import Path


class TombstoneStore:
    """Append-only set of permanently-deleted candidate_ids."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def add(self, candidate_id: str) -> None:
        if candidate_id in self.all_ids():
            return
        with self.path.open("a") as f:
            f.write(json.dumps({"candidate_id": candidate_id}) + "\n")

    def all_ids(self) -> set[str]:
        ids = set()
        for line in self.path.read_text().splitlines():
            if line.strip():
                ids.add(json.loads(line)["candidate_id"])
        return ids

    def is_deleted(self, candidate_id: str) -> bool:
        return candidate_id in self.all_ids()


def guard_ingested_candidates(candidates: list, tombstones: TombstoneStore) -> list:
    """Drops any adapter-ingested candidate whose id is tombstoned. Call this on every
    adapter fetch before writing results into candidate_store.py (CR-10)."""
    return [c for c in candidates if not tombstones.is_deleted(c.candidate_id)]


def ingest_and_store(adapter, query: str, candidate_store, tombstones: TombstoneStore) -> list:
    """The one sanctioned ingestion path: fetch from an adapter, drop tombstoned ids, then
    write survivors to candidate_store. Any code that writes adapter output into
    candidate_store without going through this function (or an equivalent tombstone check)
    violates CR-10 -- a re-crawl must never resurrect a deleted candidate."""
    fetched = adapter.fetch_candidates(query)
    guarded = guard_ingested_candidates(fetched, tombstones)
    for candidate in guarded:
        candidate_store.write(candidate)
    return guarded
