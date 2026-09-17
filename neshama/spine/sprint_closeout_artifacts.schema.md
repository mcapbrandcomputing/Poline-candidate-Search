# Sprint Closeout Artifact Schema

Schema version: 1.0
Status: Draft

## Purpose

Define the canonical sprint-level artifact filenames used by the deterministic
workflow controller for QA, validation, and retrospective closeout.

These artifacts live at sprint scope, not tranche scope.

## Canonical Filenames

All files live under the sprint directory:

```text
neshama/tranches/Sprint{N}/
```

| Artifact | Canonical filename | Purpose |
|---|---|---|
| Sprint QA report | `_qa_report.md` | Records sprint-level QA outcome after tranche execution |
| Validation report | `_validation_report.md` | Records validation-machine outcome before promotion |
| Retrospective | `_retrospective.md` | Records post-promotion retrospective artifact |

## Compatibility Rule

The controller may recognize legacy, sprint-name-prefixed forms for backward
compatibility:

- `Sprint{N}_qa_report.md`
- `Sprint{N}_validation_report.md`
- `Sprint{N}_retrospective.md`

New artifacts should use the canonical underscore-prefixed filenames.

## Status Convention

Sprint QA and validation reports should include a top-level line:

```text
Status: PASS
```

or

```text
Status: FAIL
```

The retrospective artifact does not require a PASS/FAIL line.

## Minimal Sections

### `_qa_report.md`

- Sprint identifier
- Status (`PASS` or `FAIL`)
- Scope reviewed
- Findings summary
- Commands executed
- Raw evidence or references to raw evidence

### `_validation_report.md`

- Sprint identifier
- Branch / PR / MR reference
- Status (`PASS` or `FAIL`)
- Validation commands executed
- Promotion decision or rework decision
- Raw evidence or references to raw evidence

### `_retrospective.md`

- Sprint identifier
- What went well
- What went poorly
- Corrective themes / patterns observed
- Recommended process changes
- Follow-up owners or actions