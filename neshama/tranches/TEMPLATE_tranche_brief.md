<!-- Neshama template: edit with project specifics. -->
# Tranche {TRANCHE_ID} - BRIEF

Status: DRAFT  
Owner: PM  
Created: {CREATED_AT}

---

> **Spine files are the single source of truth.** Always re-read spine files before acting — do not rely on remembered or cached state.

---

## Scope (REQUIRED)

Describe exactly what this tranche will accomplish.

- Use concrete tasks
- Reference existing requirements or plans
- Do NOT include speculative work

---

## Manifesto (REQUIRED for mechanism-change tranches)

Falsifiable prediction (B3). Non-mechanism tranches may instead state: `Manifesto: N/A (non-mechanism)`.

- **Failure evidence:** <observed failure motivating this change>
- **Root cause:** <the inferred mechanism gap>
- **Targeted fix:** <the specific change>
- **Predicted impact:** <falsifiable, measurable prediction>

---

## Inputs to Read (REQUIRED)

The worker must read and use the following files.

- [ ] relative/path/to/file1.md
- [ ] relative/path/to/file2.py

> All links must resolve. If a file does not exist, this tranche is invalid.

---

## Outputs Expected (REQUIRED)

List the concrete artifacts that must be produced.

Examples:
- Source files (paths)
- Tests (paths)
- Schemas or data files

---

## Acceptance Tests (REQUIRED)

Describe how correctness will be verified.

Examples:
- Specific test commands
- Expected behaviors
- Exit codes

---

## Forbidden Assumptions (REQUIRED)

Explicitly list what the worker must not assume.

Examples:
- No assumed data structures
- No inferred schemas
- No mock implementations
- No skipping tests

---

## Forbidden Files (include when this tranche precedes another in a dependency chain)

List any files that belong to a LATER tranche and must NOT be created here.
Be explicit — name every file. 'Do not implement X' is not enough; workers
need exact paths.

Example:
- Do NOT create `api/app/core/security.py` — belongs to the next tranche
- Do NOT create `api/app/routes/auth.py` — belongs to the next tranche

> Remove this section if there are no forbidden files for this tranche.

---

## Allowed Terminal Commands

Only the commands listed below may be run by the worker.
Any command not on this list requires PM approval via `tranche.question`.

**Conservative defaults (edit per tranche):**

- Test runners: `pytest`, `npm test`, `cargo test`, etc.
- Git inspection: `git status`, `git diff`, `git log`
- File reads: `cat`, `head`, `tail`, `grep`, `find`
- Build (read-only): `tsc --noEmit`, `python -m py_compile`

> **Explicitly NOT allowed unless added above:** `npm install`,
> `pip install`, `rm -rf node_modules`, any package-manager write,
> background processes, permission changes.

---

## Questions for PM

The worker may append clarification questions here before starting work.

---

## Completion Gate

See the Worker KICKSTART_PROMPT for full completion requirements.
Tests must be run locally with raw output pasted into the Completion Report.

---

## Delivery Format

Specify expectations clearly.

Examples:
- Code only, no markdown
- Tests required
- Documentation updates required

---

## Notes

Optional PM notes.

---

## PM Reminder: Dispatching to Worker

When this briefing is ready, present the following prompt to the human for a new worker conversation:

```
Read and apply neshama/worker/KICKSTART_PROMPT.md, then implement neshama/tranches/sprintX/{TRANCHE_ID}_brief.md

(If KICKSTART_PROMPT.md does not exist, first activate .venv and run: neshama worker kickstart)
```

Replace `sprintX` with the actual sprint number, or omit sprint folder for flat structure.

**Important**: The `neshama` command must be run from within the activated virtual environment (.venv).
