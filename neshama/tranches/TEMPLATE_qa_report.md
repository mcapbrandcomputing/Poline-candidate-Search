<!-- Neshama template: edit with project specifics. -->
# Tranche {TRANCHE_ID} — QA REPORT

Status: {PASS | FAIL}
QA Agent: {AGENT_ID}
Reviewed: {DATE}

---

## Verdict

**{PASS | FAIL}**

---

## Requirements Coverage

| Requirement ID | Addressed in code? | Test result | Notes |
|---|---|---|---|
| REQ-1 | Yes / No / Partial | Pass / Fail / N/A | |

---

## Test Execution

### Commands Run

```text
# exact commands here
```

### Raw Output

```text
# full unedited output here
```

---

## Stub Audit

| Area Reviewed | Real code exercised? | Stub / mock / placeholder found? | Impact on verdict | Follow-up / removal plan |
|---|---|---|---|---|
| Example component | Yes / No / Partial | None / describe exact stub | Pass / Fail / Needs follow-up | SprintNN / issue / none |

List every stub, mock, fake, placeholder, or no-op implementation encountered during QA that affects the evidence. If none were used, say so explicitly.

---

## Findings

### Passing Items

- ...

### Failing Items (if any)

- REQ-X: [explain what is missing or wrong]
- Test Y: [exact failure message]

### Stub Findings

- [State clearly whether any tests relied on stubs and what that means for confidence]
