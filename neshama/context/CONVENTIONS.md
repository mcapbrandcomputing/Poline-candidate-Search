# Neshama Tranche Naming Conventions

## Tranche ID Format

**Standard pattern:** `S{sprint}T{n}`

| Token | Meaning | Example |
|-------|---------|---------|
| `S{sprint}` | Sprint number | `S1`, `S2`, `S8` |
| `T{n}` | Globally sequential tranche number | `T1`, `T4`, `T12` |

The `T` number **never resets between sprints**. Each new tranche in a project gets the
next available integer, regardless of which sprint it belongs to.

```
S1T1  S1T2  S1T3        ← Sprint 1 (T1–T3)
S2T4  S2T5              ← Sprint 2 picks up at T4
S3T6  S3T7  S3T8        ← Sprint 3 picks up at T6
```

**Phase prefix (optional):** Some projects prepend a phase label when the work spans
multiple distinct phases (e.g. `P65S8T1` for Phase 6.5, Sprint 8, Tranche 1). Phase is
not a core Neshama concept — most projects use the standard `S{sprint}T{n}` form without
a phase prefix.

## Late Additions

When a tranche is added to a sprint after the sprint is already defined, it receives the
next available T number — even if that number is higher than the first tranche of a later
sprint. `INDEX.md` is the authoritative record of sprint membership, not the T number.

```
S2T4  S2T5  S2T10       ← T10 added late to Sprint 2
S3T6  S3T7  S3T8  S3T9  ← Sprint 3 unchanged
```

## File Naming

| Artifact | File |
|----------|------|
| Brief | `{ID}_brief.md` |
| Completion report | `{ID}_completion_report.md` |
| QA report | `{ID}_qa.md` (optional) |

All brief and completion report files live in `neshama/tranches/` or its sprint-level
subdirectories (e.g. `neshama/tranches/sprint10/`).

## INDEX.md Format

Sprint headings use the format:

```
## Sprint{N} — {Short description}
```

Entries under each heading list brief stem names (no `.md` extension):

```markdown
## Sprint1 — Worker Process

- S1T1_brief
- S1T2_brief
- S1T3_brief

## Sprint2 — Worker Launcher

- S2T4_brief
- S2T5_brief
```

The INDEX.md contains only **active** sprints. Legacy work is archived under
`neshama/archive/` and removed from INDEX.md.

## Status Lifecycle

Tranches move through the following states:

```
DRAFT → DISPATCHED → ACTIVE → BLOCKED → REVIEW → ACCEPTED → ARCHIVED
                               ↑__________↑   ↓_____↑
```

| Status | Meaning |
|--------|---------|
| `DRAFT` | Brief written; not yet dispatched to a worker |
| `DISPATCHED` | PM has sent the tranche to a worker via ACL; worker has not yet claimed it |
| `ACTIVE` | Worker has claimed the tranche and is working |
| `BLOCKED` | Worker is blocked; waiting on PM or external input |
| `REVIEW` | Worker completed work and submitted for PM/QA review |
| `ACCEPTED` | PM has reviewed and accepted the deliverables |
| `ARCHIVED` | Tranche is closed and moved to archive |

Transitions:
- `DISPATCHED → DRAFT`: PM recalled the dispatch
- `BLOCKED → ACTIVE`: PM unblocks the worker
- `REVIEW → ACTIVE`: PM sends back for rework

## Archive Layout

Legacy work is preserved under `neshama/archive/`:

```
neshama/archive/
  legacy_tranches/   ← pre-P6.5 sprint work (T001–T040)
  legacy_planning/
    sprints/         ← P2–P6 planning/sprints/
  legacy_pm/         ← P6 worker prompt files
```

All archive moves are performed with `git mv` to preserve history.

## Corrective Runs

| Topic | Rule |
|-------|------|
| Corrective tranche ID | Append `c{N}` to the original ID — e.g. `S19T2c1`, `S19T2c2`; `N` is computed by globbing, never from a counter file |
| SOT file location | `neshama/tranches/Sprint{N}/_corrective_sot.yaml` — one per sprint; schema at `neshama/spine/corrective_sot.schema.md` |
| Run manifest | `neshama/tranches/Sprint{N}/_runs.yaml` — append-only; records each run pass with timestamp, mode, tranche IDs, and outcomes |
| First-run isolation | Corrective-run workers MUST write only to `c{N}`-suffixed paths; any write to a non-suffixed path raises an internal assertion |
| Brief generation | `neshama sprint corrective-brief --sprint N --from-sot` reads the SOT and emits one brief per listed tranche; re-running increments `c{N}` |
| QA rerun | `neshama sprint qa-rerun --sprint N --tranches ID1,ID2` re-runs QA only, writes `{ID}_qa_report.rerun{N}.md`; original QA report is never modified |

---
