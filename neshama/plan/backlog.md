# Backlog

Open questions from the requirements doc that are genuinely deferrable (not yet assigned to a
sprint). Each carries its resolution trigger and cost of deferral from the source doc.

| Item | Resolution trigger | Cost of deferral | Notes |
|---|---|---|---|
| ~~Which specific sources are in the v1 adapter set, and on what basis is each collected?~~ | Resolved 2026-09-17 | — | This was D-01 — **RESOLVED**: personal-use tool, direct scraping in scope, LinkedIn is the named v1 source. See [[decisions]] and `neshama/tranches/sprint5/`. |
| **Do candidate profiles persist in an index, or are they retrieved per query and discarded?** | First deletion request, or first crawl-cost estimate | Medium — reshapes the data layer | Structurally load-bearing alongside D-01. S1T1's schema should stay agnostic to this until decided. |
| Which ATS integrates first (Greenhouse, Lever, Ashby, Workday)? | First design-partner commitment | Low — output layer only | Deferred past v1 engine work. |
| What is the recrawl cadence, and how is staleness surfaced to the recruiter? | First recruiter complaint about a moved candidate | Low — additive | Depends on `freshness_floor` (Block D) already being captured. |
| Does the system learn from recruiter feedback on shortlists? | 200+ searches with outcome data captured | Low — CR-11 already logs the substrate | No action needed until volume threshold hit. |
| Is coverage US-only for v1? | First non-US prospect | Low if decided before schema freeze | Decide before `geo_scope`/`comp_band` schema (S1T3) freezes if a non-US prospect appears first. |
| ~~Suppression/deletion SLA — what is the specific turnaround time for CR-10?~~ | Resolved 2026-09-17 | — | **RESOLVED**: suppression takes effect synchronously (next read excludes it); hard deletion purges within 24 hours. See S4T9 brief. |

## Real gap found during Sprint 3 implementation (2026-09-17)

`src/domain/candidate.py` (S1T1) has no `work_authorization`, `comp_band`, or country/geo field
— these three Block A predicates in `src/matching/boolean_filter.py` are structurally
fail-open (documented in that module's docstring). Not urgent: fail-open just means the tool
under-filters on these three dimensions rather than crashing or over-filtering. Revisit if/when
Sprint 5's `LinkedInAdapter` turns out to expose any of this data on real profiles.

## Deferred (not yet scheduled)

- Contact enrichment (explicitly out of scope for v1 per C-6) — do not backlog as near-term work.
- Bias audit tooling on top of the CR-11 substrate — no action until real search volume exists.
- Re-opening the legal/compliance posture (D-01/C-2) if this tool is ever shared, distributed,
  or used by anyone other than the owner — see `neshama/context/decisions.md`.
