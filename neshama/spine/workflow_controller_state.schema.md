# Workflow Controller State Schema

Schema version: 1.0
Status: Draft

## Purpose

Define the minimal on-disk source of truth for the deterministic workflow
controller.

This state file should capture runtime workflow state that is currently spread
across briefs, progress reports, completion reports, QA reports, validation
reports, and operational messages.

## File Location

Per-sprint controller state file:

```text
neshama/tranches/Sprint{N}/_workflow_state.yaml
```

## Design Rules

- Disk is the source of truth.
- This file records controller decisions and workflow state only.
- Detailed evidence remains in dedicated artifacts such as completion, QA,
  validation, and retrospective reports.
- The controller may rebuild parts of this file from artifacts if needed.
- The file must remain human-readable and diff-friendly.

## Top-Level Keys

| Key | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | Yes | Schema version for compatibility checks |
| `project_id` | string | Yes | Project identifier |
| `sprint_id` | string | Yes | Sprint identifier, e.g. `Sprint20` |
| `sprint_state` | string | Yes | Current sprint state |
| `max_parallel_tranches` | integer | Yes | Active-tranche cap enforced by controller |
| `tranches` | list | Yes | Runtime state for tracked tranches |
| `qa` | mapping | No | QA workflow state |
| `validation` | mapping | No | Validation workflow state |
| `retrospective` | mapping | No | Retrospective closeout state |
| `event_log` | list | No | Append-only recent workflow events |
| `updated_at` | string | Yes | UTC ISO-8601 timestamp of last controller write |

## Sprint States

Allowed `sprint_state` values:

- `PLANNED`
- `EXECUTING`
- `QA_PENDING`
- `QA_ACTIVE`
- `QA_FAILED`
- `READY_FOR_VALIDATION`
- `IN_VALIDATION`
- `VALIDATION_FAILED`
- `APPROVED_FOR_PROMOTION`
- `PROMOTED`
- `RETROSPECTIVE_PENDING`
- `CLOSED`

## Tranche Entry Keys

Each item in `tranches` should contain:

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Tranche ID, e.g. `S20T9` or `S20T9c1` |
| `state` | string | Yes | Current tranche state |
| `depends_on` | list[string] | No | Tranche IDs that must be `DONE` first |
| `corrective_of` | string | No | Parent tranche ID if this is corrective work |
| `assigned_to` | string | No | Current worker / agent ID |
| `priority` | integer | No | Relative scheduling priority |
| `blocked_reason` | string | No | Human-readable blocker summary |
| `brief_path` | string | Yes | Path to the brief artifact |
| `progress_path` | string | No | Path to progress artifact |
| `completion_path` | string | No | Path to completion artifact |
| `qa_status` | string | No | QA outcome for this tranche if tracked individually |
| `last_event` | string | No | Last workflow event affecting this tranche |
| `updated_at` | string | Yes | UTC ISO-8601 timestamp |

## Tranche States

Allowed `state` values:

- `DRAFT`
- `READY`
- `DISPATCHED`
- `ACTIVE`
- `REVIEW`
- `CORRECTIVE_REQUIRED`
- `DONE`
- `BLOCKED`
- `CANCELLED`

## QA Block

Example keys for the `qa` mapping:

| Key | Type | Required | Description |
|---|---|---|---|
| `state` | string | No | `PENDING`, `ACTIVE`, `PASSED`, `FAILED` |
| `qa_report_path` | string | No | Path to sprint QA report |
| `last_run_at` | string | No | UTC ISO-8601 timestamp |
| `failure_summary` | string | No | Short failure description |

## Validation Block

Example keys for the `validation` mapping:

| Key | Type | Required | Description |
|---|---|---|---|
| `state` | string | No | `PENDING`, `ACTIVE`, `PASSED`, `FAILED` |
| `branch` | string | No | Sprint branch under validation |
| `provider` | string | No | `github`, `gitlab`, or `manual` |
| `review_ref` | string | No | PR / MR number or external reference |
| `validation_report_path` | string | No | Path to validation artifact |
| `requested_at` | string | No | UTC ISO-8601 timestamp |
| `completed_at` | string | No | UTC ISO-8601 timestamp |

## Retrospective Block

Example keys for the `retrospective` mapping:

| Key | Type | Required | Description |
|---|---|---|---|
| `state` | string | No | `PENDING` or `RECORDED` |
| `report_path` | string | No | Path to retrospective artifact |
| `recorded_at` | string | No | UTC ISO-8601 timestamp |

## Event Log Entry Keys

Each item in `event_log` should contain:

| Key | Type | Required | Description |
|---|---|---|---|
| `at` | string | Yes | UTC ISO-8601 timestamp |
| `event` | string | Yes | Workflow event name |
| `entity_type` | string | Yes | `sprint` or `tranche` |
| `entity_id` | string | Yes | Sprint ID or tranche ID |
| `note` | string | No | Short human-readable detail |

## Example

```yaml
schema_version: "1"
project_id: neshama-toolkit
sprint_id: Sprint20
sprint_state: READY_FOR_VALIDATION
max_parallel_tranches: 2
tranches:
  - id: S20T8
    state: DONE
    depends_on: []
    brief_path: neshama/tranches/Sprint20/S20T8_brief.md
    progress_path: neshama/tranches/Sprint20/S20T8_progress.md
    completion_path: neshama/tranches/Sprint20/S20T8_completion_report.md
    last_event: worker_submitted_completion
    updated_at: 2026-04-24T17:10:00Z
  - id: S20T9c1
    state: DONE
    corrective_of: S20T9
    depends_on: [S20T9]
    brief_path: neshama/tranches/Sprint20/S20T9c1_brief.md
    progress_path: neshama/tranches/Sprint20/S20T9c1_progress.md
    completion_path: neshama/tranches/Sprint20/S20T9c1_completion_report.md
    last_event: corrective_tranche_done
    updated_at: 2026-04-24T17:25:00Z
qa:
  state: PASSED
  qa_report_path: neshama/tranches/Sprint20/_qa_report.md
  last_run_at: 2026-04-24T17:30:00Z
validation:
  state: PENDING
  branch: sprint20
  provider: github
  validation_report_path: neshama/tranches/Sprint20/_validation_report.md
  requested_at: 2026-04-24T17:35:00Z
retrospective:
  state: PENDING
  report_path: neshama/tranches/Sprint20/_retrospective.md
event_log:
  - at: 2026-04-24T17:35:00Z
    event: validation_requested
    entity_type: sprint
    entity_id: Sprint20
updated_at: 2026-04-24T17:35:00Z
```

## Validation Rules

- `schema_version`, `project_id`, `sprint_id`, `sprint_state`, `tranches`, and
  `updated_at` are required.
- `tranches` must be a list and every tranche entry must contain `id`, `state`,
  `brief_path`, and `updated_at`.
- The controller must reject unknown `sprint_state` and tranche `state` values.
- Missing evidence paths should not corrupt the state file; they should instead
  keep the workflow from advancing.