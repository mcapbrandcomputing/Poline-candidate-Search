---
description: "Use when starting, ending, or resuming work on a neshama-managed sprint in VS Code. Covers session bookend commands (vs-session-begin, vs-session-end), the reconcile command for catching up after missing bookends, and CONTEXT.md update discipline. Load this when beginning a coding session, wrapping up a session, or asked to update sprint state."
---

# Neshama Sprint — VS Code Session Discipline

## At the START of every sprint session

Before writing any code or reading any files, run:

```bash
source .venv/bin/activate
neshama sprint vs-session-begin \
  --sprint <SprintN> \
  --path . \
  --title "<one-line description of what this session will do>"
```

Add `--create-brief` if this session introduces new work not covered by an existing tranche.

This records the git HEAD SHA. The end command uses it to infer exactly what changed.

---

## At the END of every sprint session

After tests pass and before committing, run:

```bash
neshama sprint vs-session-end --sprint <SprintN> --path .
```

This will:
1. Write `{sprint_dir}/_vs_session_summary.md` with commits, changed files, and a CONTEXT.md update prompt
2. Refresh `_workflow_state.yaml` via `write_controller_state`
3. Refresh the project-wide `neshama/artifacts/data/wip_status.yaml`
4. Trigger a neshstat scan

**Read the printed summary.** It contains specific suggestions for updating `neshama/context/CONTEXT.md`. Apply any that are accurate — especially tranche status changes and key decisions.

---

## If you MISSED the begin marker (session already in progress)

Run the reconcile command to infer drift from git log:

```bash
# Dry-run first — see what changed
neshama sprint reconcile --sprint <SprintN> --path .

# Then apply — writes refreshed state + triggers neshstat
neshama sprint reconcile --sprint <SprintN> --path . --apply
```

---

## CONTEXT.md update rules

After `vs-session-end`, update `neshama/context/CONTEXT.md` if:

| Condition | What to update |
|---|---|
| A tranche status changed | `Tranche Status` table |
| A new tranche was created | Add row to `Tranche Status` + entry in `neshama/INDEX.md` |
| A new architectural decision was made | `Key Decisions` table (current sprint only) |
| A daemon was started or stopped | `System State` table |

Do **not** update CONTEXT.md for routine code changes that don't affect sprint state.

---

## Sprint / tranche identification

- Current sprint is in `neshama/context/CONTEXT.md` → `## Current Sprint`
- All tranches are in `neshama/INDEX.md`
- Active `_workflow_state.yaml` is at `neshama/tranches/<SprintN>/_workflow_state.yaml`
- If `_workflow_state.yaml` doesn't exist yet, run `neshama sprint inspect --sprint <SprintN> --path . --write-state`

---

## Quick reference

| Command | When |
|---|---|
| `neshama sprint vs-session-begin --sprint S --title "..."` | Session start |
| `neshama sprint vs-session-end --sprint S` | Session end |
| `neshama sprint reconcile --sprint S` | Catch-up (dry-run) |
| `neshama sprint reconcile --sprint S --apply` | Catch-up (write state) |
| `neshama sprint refresh-wip` | Regenerate project snapshot without a full session |
| `neshama sprint inspect --sprint S --write-state` | Force-write state from current artifacts |
