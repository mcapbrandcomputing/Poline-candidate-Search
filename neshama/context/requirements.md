# Requirements

Source: "Candidate Sourcing Tool — Clarified Requirements v0.2" (stakeholder doc, 2026-09-17).
This system helps an in-house recruiter find candidates for a specific open role by
interrogating the recruiter about what the job actually requires (JD is a seed, not
an input) and retrieving candidates from permissible sources who satisfy those
requirements. The system surfaces and explains; it does not score, rank, or recommend.

## Functional requirements

| ID | Requirement | Depends on decision |
|---|---|---|
| CR-1 | Every intake requirement is typed `disqualifying` or `preferred`. Disqualifying requirements are evaluated as boolean filters before any semantic operation. A candidate failing any disqualifying requirement never appears in output. | D-03 |
| CR-2 | Semantic similarity runs only on the set surviving CR-1. It orders that set; it never adds to it. | D-03 |
| CR-3 | Each returned candidate carries a `reasons[]` array — each element names one intake requirement plus the specific profile evidence satisfying it. Zero populated reasons → not returned. | D-02 |
| CR-4 | No numeric score, percentage, star rating, letter grade, or implied ordering is rendered to the recruiter. Internal relevance scores are computed and written to an audit log, keyed to query + candidate, and retained. | D-02 |
| CR-5 | Output is a shortlist in stable, non-ranked order (alphabetical or most-recently-updated). Interface must not imply position conveys fitness. | D-02 |
| CR-6 | A recruiter cannot run a search from a pasted JD alone. The system extracts a draft requirement set and requires explicit confirmation/correction of every disqualifying requirement before search executes. | D-05 |
| CR-7 | Intake is a review flow, not a blank form — every field arrives pre-populated with an extracted value or an explicit "not found in JD" state. | D-05 |
| CR-8 | Every candidate record stores `source_url`, `source_name`, `collected_at`, `collection_basis` (licensed / public-permissible / candidate-submitted / personal-use-scrape). A record lacking `collection_basis` is not indexed. | D-01 |
| CR-9 | Source adapters sit behind a common interface. Adding/removing a source must not require changes to the matching engine, schema, or interface. | D-01 |
| CR-10 | Per-candidate suppression and deletion on request, propagating to the index within a defined SLA, request is recorded. Deletion is not reversed by a subsequent crawl. | D-04 |
| CR-11 | Every search persists its full requirement set, returned candidate set, and reasons shown — timestamped and attributed to a user. Substrate for future bias audit and enterprise security review. | D-04 |

## Non-functional constraints

| ID | Constraint |
|---|---|
| C-1 | Candidates in the index have not consented to being there. System must be operable under a regime where any candidate can demand notice, access, or deletion. No architecture may assume permanent retention. |
| C-2 | **N/A for this build** — original constraint assumed a sold, multi-tenant product with a buyer legal/security review gate. This is a personal, single-user tool, not distributed or sold; see [[decisions]] D-01 revision, 2026-09-17. Kept here for history only. |
| C-3 | Sources will break, rate-limit, and revoke access. No single source may be load-bearing for the product's value proposition. |
| C-4 | Recruiter time at intake is scarce. The CR-6 confirmation flow must complete in ~3–5 minutes for a typical role. |
| C-5 | The system is a sourcing aid, not a decision-maker. No output may be framed as a recommendation to hire, reject, advance, or exclude. |
| C-6 | Contact information is out of scope for v1. Recruiters source into an ATS and reach candidates through existing channels. |

## Recruiter intake instrument (drives CR-6/CR-7 schema)

Populated per-requisition, JD-prefilled, recruiter confirms/corrects. Target: 3–5 min.

**Block A — Disqualifying filters (boolean, must be answered)**

| Question | Field | Why disqualifying |
|---|---|---|
| Which of these [JD-extracted] are true hard requirements vs. waivable? | `requirements[].type` | Highest-value question; JDs list ten, usually two are real |
| Work authorization required? Will you sponsor? | `work_authorization` | Non-negotiable, invisible in most profiles |
| Security clearance / license / certification legally required? | `credentials[]` | Legally binding |
| Onsite/hybrid/remote — days, location? | `location_policy`, `worksite` | Most common cause of late-stage candidate loss |
| Geographic boundary for candidates? | `geo_scope` | Interacts with location policy and payroll entities |
| Firm compensation ceiling? | `comp_band` | Filters candidates who would never accept |
| Excluded employers (non-solicit, conflicts, current employer)? | `excluded_employers[]` | Legal exposure, not preference |

**Block B — What the role actually is**

| Question | Field |
|---|---|
| Describe the first 90 days — build, fix, own, ship? | `role_outcomes` (free text, embedded) |
| Backfill or new seat? If backfill, what did the last person do well / why did they leave? | `seat_history` |
| Has this role failed to fill before? What went wrong? | `prior_search_failure` |
| Who does this person report to, how many reports? | `scope_level` |
| Team's stack/tooling/operating environment? | `environment[]` |

**Block C — Calibration (highest signal)**

| Question | Field |
|---|---|
| Name 2–3 people who'd be right for this. | `positive_exemplars[]` |
| Name a candidate who looked right on paper and was wrong — the tell? | `negative_exemplar` |
| Which 3–5 companies do strong candidates usually come from? | `source_companies[]` |
| Which adjacent titles should count as equivalent? | `title_equivalents[]` |
| "5+ years" — real floor, or shorthand for a capability? Which? | `experience_semantics` |

**Block D — Search behavior**

| Question | Field |
|---|---|
| Candidates per batch? | `batch_size` |
| Exclude/flag/include people already in ATS? | `ats_dedupe_policy` |
| Freshness floor for profile updates? | `freshness_floor` |

**Deliberately not asked:** anything about age, gender, race, disability, family status, or a
proxy for them (excluded by construction); "what is your ideal candidate?" (Block C exemplars
cover this); anything requiring the recruiter to leave the tool to look up (C-4).

See [[glossary]] for term definitions and [[decisions]] for the rationale behind each D-xx.
