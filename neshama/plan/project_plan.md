# Project Plan — Candidate Sourcing Tool

Source of intent: "Candidate Sourcing Tool — Clarified Requirements v0.2". Full requirement
detail lives in [[requirements]]; decision rationale in [[decisions]]; open items in [[backlog]].

## Delivery approach

Build the engine and schema so they are **source-agnostic** (CR-9), since D-01 (which sources,
on what legal basis) is explicitly an open Position, not a Decision — see [[decisions]]. This
lets Sprints 1–4 proceed in full without waiting on legal/counsel review of the v1 source list.
A real (non-mock) source adapter is scoped only in Sprint 5, after D-01 is resolved.

## Milestones

| Sprint | Theme | Tranches | Depends on | Gated by |
|---|---|---|---|---|
| Sprint 1 | Data & interface foundation | S1T1 candidate/audit schema, S1T2 source-adapter interface + mock adapter, S1T3 typed requirement schema | — | — |
| Sprint 2 | Recruiter intake | S2T4 JD extraction engine, S2T5 intake confirmation flow (Blocks A–D) | Sprint 1 (schema) | — |
| Sprint 3 | Retrieval engine | S3T6 boolean disqualifying-filter engine, S3T7 semantic ranking + reasons generation | Sprint 1, Sprint 2 | — |
| Sprint 4 | Shortlist & candidate governance | S4T8 non-ranked shortlist UI, S4T9 suppression/deletion pipeline | Sprint 3 | Suppression/deletion SLA value (see [[backlog]]) |
| Sprint 5 (not yet scaffolded) | First live source adapter | TBD | Sprint 1 (adapter interface) | **D-01 resolution — do not start before legal/counsel sign-off on the specific source and its collection_basis** |

## Owners

Not yet assigned — single-operator project at time of writing. PM role and Worker role (see
`neshama/pm/` and `neshama/worker/`) are both filled by the same human until a team is staffed.

## Risks

| Risk | From | Mitigation |
|---|---|---|
| Permissible-source coverage too thin for technical/senior roles | D-01 | Adapter isolation (CR-9) lets more sources be added later without engine changes |
| Ranked-score expectation from recruiters despite CR-4/CR-5 | D-02 | Validate the reasons-array UX with a real recruiter before Sprint 4 ships |
| Over-strict boolean filters collapse result sets to near-zero | D-03 | S3T6 acceptance tests must include a "realistic sparse-match" case, not just golden-path |
| Enterprise sales cycle (6–9mo) starves the project of feedback | D-04 | Out of engineering's control; tracked here for visibility only |
| Confirmation flow exceeds the 3–5 min budget (C-4) | D-05 | S2T5 acceptance test must include a timed walkthrough |
| A design ships that cannot be explained in a vendor security questionnaire | C-2 | Every tranche brief carries acceptance criteria that double as questionnaire-answerable claims |
