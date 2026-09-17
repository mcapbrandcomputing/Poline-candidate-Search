# How Neshama Works — Architecture Reference

> Quick reference: [START_HERE.md](START_HERE.md)

---

## Core Split

Neshama has two distinct layers. Understanding this split prevents agents from overstepping.

### 1. Deterministic Workflow Controller (`neshama pm watch`)

The workflow authority. A Python program, not an AI.

**What it does:**
- Reads sprint and tranche state from disk on every cycle
- Decides tranche eligibility based on dependencies and policy
- Dispatches workers via ACL messages
- Enforces max parallel tranche limits
- Detects completion artifacts (completion reports) and advances state
- Triggers QA when execution is complete
- Records issue events and inserts corrective tranches
- Triggers validation handoff after QA pass
- Tracks promotion outcome
- Requires retrospective artifact before final sprint closure

**What it does NOT do:**
- Infer missing policy from prompts
- Advance state based on conversational judgment
- Act as a code reviewer or merge engine

**Start it:** `neshama pm watch --project <id> --interval 30 --app-root .`

---

### 2. AI PM Advisor (LLM in VS Code chat or elsewhere)

An advisory layer. Not the workflow authority.

**What it does:**
- Summarizes status for humans
- Diagnoses issues and explains blockers
- Drafts corrective tranches
- Drafts human-facing messages and validation requests
- Interprets ambiguous worker or QA output
- Helps plan upcoming sprint work

**What it does NOT do:**
- Dispatch work autonomously
- Advance tranche or sprint state on its own
- Decide that QA, validation, or promotion passed

---

## Daemon Stack

| Daemon | Command | Role |
|---|---|---|
| ACL bus | `neshama acl start` | Message bus — all agents communicate through it |
| PM watch | `neshama pm watch --project <id> --interval 30 --app-root .` | Workflow controller — dispatch, state transitions, QA triggers |
| Dispatcher | `neshama dispatcher run --acl-base-url <url> --spine-path neshama/` | Routes `tranche.dispatch` ACL messages to available workers |
| Worker watch | `neshama worker watch` | Polls ACL, spawns subprocess workers |
| Worker run | `neshama worker run --brief <path> --agent-id <id>` | Executes a single tranche |
| Portal | `neshama portal serve --spine . --port 8080` | Web dashboard |

ACL port is stored in `neshama/.acl_port`. Health: `curl http://localhost:$(cat neshama/.acl_port)/health`

---

## Tranche Lifecycle — Who Does What

```
DRAFT
  │ PM program imports/creates brief
  ▼
DISPATCHED
  │ PM program posts tranche.dispatch ACL message
  │ Dispatcher routes it to worker
  ▼
ACTIVE
  │ Worker is executing
  │ LLM agent reads brief, implements scope
  ▼
REVIEW         ← Worker writes completion_report.md + sets Status: REVIEW in brief
  │ PM program detects REVIEW, triggers QA agent
  ▼
ACCEPTED       ← PM program advances after QA pass
  │
  ▼
ARCHIVED       (terminal)
```

**Branch states:** `ACTIVE → BLOCKED` (external dependency), `DISPATCHED → DRAFT` (recall)

---

## How a VS Code LLM Worker Operates

When a human (or PM program) gives an agent a tranche brief to execute:

1. **Read the brief** at `neshama/tranches/<SprintN>/<ID>_brief.md`
   - Scope section defines what to build — exactly that, nothing more
   - Inputs to Read section lists prerequisite files — read them all before starting

2. **Implement the scope**
   - Modify only files listed in Outputs Expected
   - Follow Implementation Patterns; avoid anti-patterns

3. **Run the required tests**
   - Use the exact test command(s) from the brief's Acceptance Criteria
   - Capture raw, unedited output

4. **Write the completion report**
   - Path: `neshama/tranches/<SprintN>/<ID>_completion_report.md`
   - Template: `neshama/tranches/TEMPLATE_completion_report.md`
   - Must include: file inventory, command log, raw test output, deviation log

5. **Update the brief's Status to REVIEW**
   - Edit the `Status:` line in the brief file to `Status: REVIEW`
   - This is the trigger the PM program watches for

6. **Stop** — do not do QA, do not merge, do not dispatch follow-up work

---

## Running a Sprint With VS Code Worker Agents

The AI PM advisor (in VS Code chat) can coordinate a sprint using VS Code agents as workers. The engineer is the bridge between the AI PM and the worker chat windows.

### Engineer checklist before starting workers

1. **Verify `neshama pm watch` is running** — this is mandatory; without it tranche state never advances past REVIEW
   ```bash
   # Check if already running
   neshama acl status
   # Start if not running
   source .venv/bin/activate
   neshama pm watch --project <id> --interval 30 --app-root .
   ```
2. **Verify the ACL bus is running** — `neshama pm watch` depends on it
   ```bash
   curl http://localhost:$(cat neshama/.acl_port)/health
   ```
3. **Ask the AI PM to prepare the sprint** — prompt: *"You are the PM for Sprint N. Prepare it for VS Code workers."*
4. **AI PM will output** — one kickstart prompt per parallel tranche + engineer instructions
5. **Open one VS Code chat per tranche** — paste the kickstart prompt
6. **Minimal worker prompt format**: `You are worker_<ID>. Check your ACL inbox and execute your assigned tranche.`
7. **Tell the AI PM "continue"** after each wave of workers completes — it re-reads the spine and generates prompts for the next eligible tranches

### What the AI PM does at each step

| Step | AI PM action |
|---|---|
| Sprint start | Reads all briefs, maps dependencies, identifies parallel tranches |
| Per tranche | Calls `neshama dispatch <ID>` — sets status ACTIVE + sends ACL message |
| Engineer opens worker | Worker checks ACL inbox, reads brief, executes |
| Worker sets REVIEW | `neshama pm watch` detects it, triggers QA, advances to ACCEPTED |
| Engineer says "continue" | AI PM re-reads spine, identifies next eligible tranches, generates prompts |

### Why `neshama pm watch` cannot be skipped

The AI PM advisor does not watch files between turns. `neshama pm watch` is the only component that:
- detects `Status: REVIEW` reliably
- triggers QA
- advances status to ACCEPTED
- unblocks dependent tranches

Without it the sprint stalls permanently at REVIEW after each tranche completes.

---

## Spine Map (Full Reference)

| Path | Purpose |
|---|---|
| `neshama/INDEX.md` | Canonical tranche registry — one stem per tranche |
| `neshama/context/CONTEXT.md` | Living project memory — status, open work, decisions |
| `neshama/context/requirements.md` | Functional requirements |
| `neshama/context/decisions.md` | Architectural decisions with rationale |
| `neshama/context/CONVENTIONS.md` | Tranche naming, status lifecycle, worker rules |
| `neshama/context/glossary.md` | Term definitions |
| `neshama/pm/START_HERE.md` | LLM agent quick reference — mandatory read |
| `neshama/pm/HOW_NESHAMA_WORKS.md` | Full architecture reference |
| `neshama/tranches/` | All brief and completion report files |
| `neshama/tranches/<SprintN>/_workflow_state.yaml` | Controller state for that sprint |
| `neshama/logs/pm_decisions.jsonl` | PM autonomous decision journal |
| `neshama/NESHAMA_VERSION.md` | Neshama toolkit version installed in this project |
