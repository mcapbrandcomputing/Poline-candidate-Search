# Neshama Toolkit — VS Code Copilot Agent Instructions

## THE PM IS A DETERMINISTIC PROGRAM — NOT AN AI

`neshama pm watch` is a Python program. It dispatches tranches, advances tranche state, and triggers QA.
**You (as an LLM agent) are NOT the PM.** Your role is WORKER or ADVISOR — see `neshama/pm/START_HERE.md`.

> ⚡ **Read `neshama/pm/START_HERE.md` before doing any sprint work in this repo.**

---

## Session startup — mandatory

1. **Read `neshama/pm/START_HERE.md` to understand your role.**
2. **Read `neshama/context/CONTEXT.md` before taking any action in this repo.**
3. **Read `neshama/INDEX.md` to confirm the current sprint and active tranche before planning or dispatching work.**
4. **For sprint coding sessions: follow `.github/instructions/neshama-sprint-session.instructions.md` — run bookend commands at session start and end.**

### Sprint session bookends (required)

At the **start** of every session involving sprint work:
```bash
source .venv/bin/activate
neshama sprint vs-session-begin --sprint <SprintN> --path . --title "<what this session will do>"
```

At the **end** of every session (after tests pass, before commit):
```bash
neshama sprint vs-session-end --sprint <SprintN> --path .
```
Read the printed summary — it contains specific `neshama/context/CONTEXT.md` update suggestions.

If the begin marker was missed, use `neshama sprint reconcile --sprint <SprintN> --path . --apply` to catch up.

---

## Your Role as an LLM Agent

You are either a **WORKER** or an **ADVISOR** or a **PLANNER**. Never more than one at once.

| Role | When | What you do |
|---|---|---|
| PLANNER | Scoping a sprint (this session) | Read context → write briefs → write kickstart prompt → **STOP** |
| WORKER | Executing a tranche brief (separate session) | Read brief → implement scope → run tests → write completion report → set Status: REVIEW |
| ADVISOR | Helping human understand state | Re-read files → quote verbatim → draft things → explain blockers |

### PLANNER sessions end at the kickstart prompt

When the human asks to scope or plan a sprint, your output is:
1. Tranche brief files in `neshama/tranches/SprintN/`
2. A kickstart prompt (`SPRINTN_KICKSTART.md`) for the worker session
3. Updated `neshama/INDEX.md` and `neshama/plan/idea_inbox.md`

**Then stop.** Do NOT proceed to implement, run tests, or commit code in the same session.
The human will open a separate session (Cursor, Claude Code, another Copilot chat) and
paste the kickstart. That session is the worker.

**The only status change a worker makes: set `Status: REVIEW` in the brief file. Nothing else.**
The PM program (`neshama pm watch`) handles all other state transitions.

Full role guide: `neshama/pm/START_HERE.md`

---

## Maintaining CONTEXT.md

`CONTEXT.md` has two machine-managed sections (`## Current Sprint` and `## Capabilities Landed`) that must be updated via `neshama sprint context-update --sprint SprintN --path .` — **never edited by hand or by an agent writing directly to the file**. All other sections may be edited by the context-update agent after each ACCEPTED tranche.

Format rules (for context-update agent use):
- Tables and bullets only — no prose paragraphs
- No history: decisions older than the current sprint belong in tranche completion reports
- Do not duplicate content from `requirements.md`, `assumptions.md`, or `glossary.md`
- Keep it under ~120 lines

---

## Spine map

| Path | Purpose |
|---|---|
| `neshama/pm/START_HERE.md` | **Agent quick reference** — roles, rules, completion requirements |
| `neshama/pm/HOW_NESHAMA_WORKS.md` | Full architecture — deterministic controller + AI advisor split |
| `neshama/INDEX.md` | Tranche registry — one entry per tranche stem |
| `neshama/context/CONTEXT.md` | **Living project memory** — status, open work, decisions (read every session) |
| `neshama/context/requirements.md` | Functional requirements |
| `neshama/context/decisions.md` | Architectural decisions with dates and rationale |
| `neshama/context/CONVENTIONS.md` | Worker behavior rules, tranche status lifecycle, naming, git discipline |
| `neshama/context/glossary.md` | Term definitions |
| `neshama/tranches/` | All brief and completion report files |
| `neshama/logs/pm_decisions.jsonl` | PM autonomous decision journal |

---

## Key conventions

| Topic | Rule |
|---|---|
| Python | 3.11+ · venv at `.venv/` — activate before using `neshama` CLI |
| Tests | `python -m pytest --ignore=tests/test_ntfy.py --tb=no -q` — never run full suite synchronously |
| Tranche lifecycle | DRAFT → DISPATCHED → ACTIVE → REVIEW → ACCEPTED |
| First action | Re-read `neshama/context/CONTEXT.md` and `neshama/INDEX.md` before writing any brief |
| Commit shape | One commit per tranche: `S{n}T{n}: <short description>` |
| Spine path | `neshama/` (NOT `neshama/neshama/`) |
| Context files | Workers read context — they do not write it (except the context-update agent) |
| Evidence standard | Completion reports must cite file paths, not message IDs or conversation references |

---

## Forbidden behavior

| Rule |
|---|
| Do not act as the PM — `neshama pm watch` is the workflow authority |
| **Do not implement sprint work (edit `src/`, run tests, commit) in a planning/scoping session** |
| **Do not combine PLANNER and WORKER roles in the same session** |
| Do not advance tranche status beyond REVIEW |
| Do not dispatch tranches to other workers |
| Do not run QA on your own completed work |
| Do not invent requirements not in the brief |
| Do not refactor code outside tranche scope |
| Do not claim completion without raw test output |
| Do not write to `neshama/context/CONTEXT.md` directly. To update it, run `neshama sprint context-update --sprint SprintN --path .` in a terminal, or ask the human to run it. |
| Do not use `neshama` CLI without activating the venv first |
| Do not report status from memory — re-read the file |
