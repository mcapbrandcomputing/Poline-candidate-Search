# PM Resources

This directory contains guidance for agents and humans interacting with the Neshama PM system.

> ⚡ **LLM Agents**: The PM is a **deterministic program** — not an AI. Read [START_HERE.md](START_HERE.md) first.

---

## Documents

### For LLM Agents (Start Here)
- **[START_HERE.md](START_HERE.md)** — Quick reference (~1k tokens): your role, what you can and cannot do, how to complete work

### For Full Architecture Understanding
- **[HOW_NESHAMA_WORKS.md](HOW_NESHAMA_WORKS.md)** — Deterministic controller vs AI advisor split, end-to-end tranche lifecycle, who does what at each step

---

## Role Selector

| If you are... | Read |
|---|---|
| An LLM agent scoping/planning a sprint | [START_HERE.md](START_HERE.md) — PLANNER rules apply |
| An LLM agent about to execute a tranche | [START_HERE.md](START_HERE.md) first, then your brief |
| An LLM agent helping the human understand project state | [START_HERE.md](START_HERE.md) — ADVISOR rules apply |
| A human wanting to understand the full system | [HOW_NESHAMA_WORKS.md](HOW_NESHAMA_WORKS.md) |
| The PM program (`neshama pm watch`) | N/A — you are the deterministic controller |

---

## Key Principle

```
PM program = workflow authority (dispatches, advances state, triggers QA)
LLM agent  = worker or advisor (executes briefs, explains state — never controls workflow)
```
