# START HERE — LLM Agent Quick Reference

> ~1k tokens. Read this before acting in any neshama-managed project.
> Full details: [HOW_NESHAMA_WORKS.md](HOW_NESHAMA_WORKS.md)
> neshama-toolkit v0.8.0

---

## ⚠️ Starting a New Sprint? Use the Project Planner First

Before writing any briefs or planning any sprint work, an engineer must run the planning session:

1. Open a new AI chat (VS Code Copilot, Claude Code, Codex CLI, etc.)
2. Paste the contents of **[PLANNING_PROMPT.md](PLANNING_PROMPT.md)** as the first message
3. The AI will read project context, ask clarifying questions, propose a plan, and write briefs on approval

**Do not write briefs by hand or skip the planner.** Briefs written outside the planner workflow are likely to miss dependencies, overlap file ownership, or contradict requirements.

---

## THE PM IS A DETERMINISTIC PROGRAM

`neshama pm watch` is a Python program — not an AI. It:
- reads the spine on disk
- decides which tranches are eligible
- dispatches workers via the ACL bus
- detects completion artifacts and advances tranche state
- triggers QA and validation gates

**You (as an LLM) are NOT the PM. Do not act as one.**

The one exception: if you are executing a `SPRINT{N}_SUBAGENT_SESSION.md` file placed by a human,
you are an ORCHESTRATOR — see that role below.

---

## Your Role: WORKER, ADVISOR, PLANNER, or ORCHESTRATOR

### If you are an ORCHESTRATOR (executing a SPRINT{N}_SUBAGENT_SESSION.md)

A human placed a `SPRINT{N}_SUBAGENT_SESSION.md` file in the repo and asked you to execute it.
That file is your mandate. You are authorized to:
- post ACL dispatch messages
- spawn worker subagents
- verify QA reports
- commit after all QA verdicts are PASS

You are the human-supervised sprint runner. The 'You are NOT the PM' rule above refers to the
`neshama pm watch` background daemon — you are not that program. You are a supervised orchestrator.

Orchestrators do NOT:
- skip steps in the session file
- proceed past a failing pre-condition gate
- advance brief status beyond REVIEW (workers do that)
- commit without all QA verdicts PASS

### If you are a PLANNER (scoping a sprint — separate session)

1. **Read context** — `neshama/context/CONTEXT.md`, `neshama/INDEX.md`, `neshama/plan/idea_inbox.md`
2. **Write brief files** — `neshama/tranches/SprintN/<ID>_brief.md` for each tranche
3. **Write a kickstart prompt** — `neshama/tranches/SprintN/SPRINTN_KICKSTART.md`
4. **Update `neshama/INDEX.md`** — add Sprint N section
5. **Stop** — do NOT implement, run tests, or commit in this session

The human pastes the kickstart into a separate worker session.

### If you are a WORKER (executing a tranche brief)

1. **Read your brief completely** — `neshama/tranches/<SprintN>/<ID>_brief.md`
2. **Execute only the scope defined in the brief** — nothing more
3. **Run the required tests** — paste raw output, do not summarize
4. **Write a completion report** — `neshama/tranches/<SprintN>/<ID>_completion_report.md`
5. **Update the brief's `Status:` line to `REVIEW`** — this is the only status change you make
6. **Stop** — the PM program picks up from here

Workers do NOT:
- dispatch other tranches
- run QA on their own work
- advance status beyond REVIEW
- merge branches or promote code
- declare their own work accepted

### If you are an ADVISOR (helping the human understand project state)

1. **Re-read spine files before reporting anything** — never rely on memory
2. **Quote verbatim** — when reporting a status, quote the exact `Status:` line from the file
3. **Draft things** — corrective tranches, human-facing messages, status summaries
4. **Explain blockers** — but do not resolve them unilaterally

Advisors do NOT:
- advance tranche or sprint state on their own
- dispatch workers
- declare that QA, validation, or promotion passed

---

## Tranche Lifecycle (who does what)

```
DRAFT       ← PM program creates/imports brief
DISPATCHED  ← PM program dispatches to worker
ACTIVE      ← Worker is executing (set by worker watch)
REVIEW      ← Worker writes completion report and sets Status to REVIEW
ACCEPTED    ← PM program (after QA pass) advances to ACCEPTED
ARCHIVED    ← Terminal state
```

**The only state change an LLM worker makes: ACTIVE → REVIEW (by updating the brief file).**

---

## Disk is the Source of Truth

- Always re-read files before reporting status — do not rely on context window
- Brief file `Status:` field is authoritative, not ACL messages or conversation history
- Completion reports must cite file paths, not message IDs

---

## Completion Report Requirements (MANDATORY)

A completion report at `neshama/tranches/<SprintN>/<ID>_completion_report.md` MUST contain:

1. **File inventory** — every file created or modified, with a one-line summary
2. **Command log** — every command run, with exit code
3. **Raw test output** — unedited, complete
4. **Deviation log** — any deviation from brief scope, with reason

Do not claim completion without test output. An incomplete report will be rejected.

---

## Key Commands (after activating venv)

| Purpose | Command |
|---|---|
| Activate venv | `source .venv/bin/activate` |
| Run tests (fast) | `python -m pytest --ignore=tests/test_ntfy.py --tb=no -q` |
| Check PM actions | `neshama board` |
| Check tranche status | Read `neshama/tranches/<SprintN>/<ID>_brief.md` |

---

## What You Must NEVER Do

| Rule |
|---|
| Do not implement sprint work (edit code, run tests, commit) in a planning/scoping session |
| Do not combine PLANNER and WORKER roles in the same session |
| Do not execute work outside the tranche brief scope |
| Do not modify `neshama/context/CONTEXT.md` during worker execution |
| Do not advance tranche status beyond REVIEW |
| Do not claim completion without raw test output |
| Do not dispatch tranches to other workers (WORKER/ADVISOR/PLANNER only — ORCHESTRATOR is authorized) |
| Do not use `neshama` CLI without activating the venv first |
| Do not report status from memory — re-read the file |
