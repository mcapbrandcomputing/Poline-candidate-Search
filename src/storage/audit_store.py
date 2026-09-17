"""Audit log persistence (S1T1). Append-only JSONL — see CR-11. No update/delete function
exists on purpose; the audit trail must not be mutable."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator

from src.domain.audit_log import AuditLogEntry


class AuditStore:
    """Append-only store for AuditLogEntry records. Deliberately has no update/delete method."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def append(self, entry: AuditLogEntry) -> None:
        data = asdict(entry)
        data["timestamp"] = entry.timestamp.isoformat()
        data["candidate_ids"] = list(entry.candidate_ids)
        with self.path.open("a") as f:
            f.write(json.dumps(data) + "\n")

    def read_all(self) -> Iterator[AuditLogEntry]:
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            yield AuditLogEntry(
                entry_id=data["entry_id"],
                event_type=data["event_type"],
                requirement_set_id=data["requirement_set_id"],
                candidate_ids=tuple(data["candidate_ids"]),
                reasons_shown=data["reasons_shown"],
                internal_scores=data["internal_scores"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                user_id=data["user_id"],
            )
