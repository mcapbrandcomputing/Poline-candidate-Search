"""LinkedIn session/credential loading (S5T10). Credentials are never hard-coded in source.

Reads from environment variables first, falling back to a git-ignored local JSON file. See
docs/linkedin_adapter_setup.md for how to obtain these values from your own logged-in browser
session (li_at cookie + JSESSIONID) -- this uses YOUR OWN account's session, not a shared or
third-party credential.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "poline_candidate_search" / "linkedin_session.json"

ENV_LI_AT = "LINKEDIN_LI_AT"
ENV_JSESSIONID = "LINKEDIN_JSESSIONID"


class MissingLinkedInSessionError(RuntimeError):
    pass


@dataclass(frozen=True)
class LinkedInSession:
    li_at: str
    jsessionid: str

    @property
    def csrf_token(self) -> str:
        """LinkedIn's voyager API expects the csrf-token header to equal the JSESSIONID
        cookie value, quotes stripped."""
        return self.jsessionid.strip('"')


def load_session(config_path: Optional[Path] = None) -> LinkedInSession:
    """Env vars take precedence; falls back to a local JSON file (never committed -- see
    .gitignore). Raises MissingLinkedInSessionError with a clear remediation message if
    neither source has both required values. `config_path` defaults to the module-level
    DEFAULT_CONFIG_PATH, looked up dynamically (not bound at def time) so tests can override it
    via monkeypatch."""
    resolved_path = config_path or DEFAULT_CONFIG_PATH
    li_at = os.environ.get(ENV_LI_AT)
    jsessionid = os.environ.get(ENV_JSESSIONID)

    if not (li_at and jsessionid) and resolved_path.exists():
        data = json.loads(resolved_path.read_text())
        li_at = li_at or data.get("li_at")
        jsessionid = jsessionid or data.get("jsessionid")

    if not li_at or not jsessionid:
        raise MissingLinkedInSessionError(
            f"LinkedIn session not found. Set {ENV_LI_AT} and {ENV_JSESSIONID} environment "
            f"variables, or create {resolved_path} with {{\"li_at\": ..., \"jsessionid\": ...}}. "
            "See docs/linkedin_adapter_setup.md."
        )
    return LinkedInSession(li_at=li_at, jsessionid=jsessionid)
