# LinkedIn adapter setup

`LinkedInAdapter` (`src/adapters/linkedin_adapter.py`) uses your own logged-in LinkedIn session
— the same one your browser already has — rather than a username/password. This is for
personal use only (see `neshama/context/decisions.md`, D-01).

## Getting your session values

1. Log into linkedin.com in your browser.
2. Open DevTools → Application (Chrome) or Storage (Firefox) → Cookies → `https://www.linkedin.com`.
3. Copy the value of the `li_at` cookie.
4. Copy the value of the `JSESSIONID` cookie (it includes surrounding quotes — keep them).

## Providing them to the adapter

**Option A — environment variables** (simplest for a one-off run):

```bash
export LINKEDIN_LI_AT="paste-your-li_at-value-here"
export LINKEDIN_JSESSIONID='"paste-your-jsessionid-value-here"'
```

**Option B — a local config file** (if you don't want to export env vars each session):

Create `~/.config/poline_candidate_search/linkedin_session.json`:

```json
{
  "li_at": "paste-your-li_at-value-here",
  "jsessionid": "\"paste-your-jsessionid-value-here\""
}
```

This path is outside the project directory and is never read by `.gitignore`-tracked project
files, so it can't accidentally get committed. If you'd rather keep it inside the project,
create it under a `secrets/` directory and confirm that directory is in `.gitignore` first.

## Session values expire

`li_at` and `JSESSIONID` are session cookies — they expire (typically after a period of
inactivity or a password change). If the adapter starts raising `LinkedInParsingError` or an
HTTP 401/403, re-extract fresh values using the steps above.

## Running it

`LinkedInAdapter` is not registered by default (importing the adapter module shouldn't require
credentials to be present). Register it explicitly once your session is configured:

```python
from src.adapters.registry import register_linkedin_adapter, get

register_linkedin_adapter()
adapter = get("linkedin")
candidates = adapter.fetch_candidates("backend engineer")
```

## Important: this has not been run against live LinkedIn from this session

The adapter's parsing logic (`_parse_search_response` in `linkedin_adapter.py`) was written and
unit-tested against a fixture response shaped like documented examples of LinkedIn's internal
search API from other open-source personal-use tools — it has not been verified against a real,
live LinkedIn response. The first real run should be done by you, manually, watching the
output, in case the actual response shape differs (LinkedIn can change this without notice —
see C-3 in `neshama/context/requirements.md`). If it does, `_parse_search_response` is the only
function that should need updating.
