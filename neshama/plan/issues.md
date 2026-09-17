<!-- Neshama template: edit with project specifics. -->
# Issues

Track non-sprint repo changes, follow-ups, and drift that should not be lost.

- If you change the repo outside a sprint-dispatched worker session, update this file.
- Promote sprint-sized work into `neshama/plan/backlog.md` when formal planning is needed.

## 2026-09-17 — Initial spine population (non-sprint, PM/setup session)

- Ran `neshama init` in this project (previously empty) to install the spine.
- Filled `context/requirements.md`, `context/decisions.md`, `context/assumptions.md`,
  `context/glossary.md`, `plan/project_plan.md`, `plan/backlog.md`, `plan/sprint_board.md`,
  `context/CONTEXT.md` from the stakeholder doc "Candidate Sourcing Tool — Clarified
  Requirements v0.2".
- Scaffolded and wrote 9 tranche briefs across 4 sprints (S1T1–S1T3, S2T4–S2T5, S3T6–S3T7,
  S4T8–S4T9); all pass `neshama tranche validate` except for the expected "completion report
  missing" (tranches are DRAFT, not yet dispatched).
- **Open item requiring a human before dispatch:** S4T9 (suppression/deletion pipeline) has a
  `{SLA_VALUE}` placeholder that must be set by a human before that brief can be dispatched —
  see the brief's own pre-dispatch warning and `plan/backlog.md`.
- **Open item requiring a human before Sprint 5 is scoped:** D-01 (data acquisition posture —
  which sources, on what legal basis) is an explicit open Position, not a Decision. Sprint 5
  (first live source adapter) must not be scaffolded until a human/counsel resolves it. See
  `context/decisions.md`.
- No source code was written in this session — Sprints 1–4 are ready to dispatch to workers.
