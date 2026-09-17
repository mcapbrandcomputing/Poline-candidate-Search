# Decisions

## D-01 — Data acquisition posture — **DECIDED (revised for personal-use context)**

- **Date:** 2026-09-17 (opened) → revised 2026-09-17
- **Before:** "scrape LinkedIn, Indeed, or any other site" — no distinction between licensed, permissible, and prohibited collection.
- **Original position:** Licensed/permissible sources only, gated on legal/counsel review (C-2), because the original brief assumed a sold, multi-tenant enterprise product (D-04's in-house TA buyer with a legal review gate).
- **Revised decision (owner override, 2026-09-17):** This build is for personal use only — a single user, not distributed, sold, or exposed to any buyer's legal/security review. The stakeholder explicitly waived the compliance posture that made D-01 a Position: "make the right decision on the placeholders and don't worry about the legal stuff as this is just for me and will not be released to the public." Direct scraping of LinkedIn and other candidate-data sites is in scope for v1. Adapter isolation (CR-9) and per-record `collection_basis` (CR-8) are kept — not because a buyer's legal team requires them, but because they're good engineering practice and let the mock adapter and real adapter coexist cleanly.
- **Reason:** No commercial exposure exists for a private, single-user tool — the entire premise of the original C-2 gate (buyer's legal/security review blocks the sale) does not apply.
- **Risk:** If this tool is ever shared, distributed, or turned into a product for other users, this decision must be revisited — see [[assumptions]] A-2 and A-7 (updated) and re-open this entry rather than silently carrying the personal-use posture forward.
- **Status:** DECIDED. Sprint 5 (real source adapter) is unblocked — see `neshama/tranches/sprint5/`.

## D-02 — Reasons, not scores

- **Date:** 2026-09-17
- **Before:** "pair them with the right candidate" — implied a ranking system.
- **After:** Unranked shortlist with explicit per-candidate reasons (CR-3, CR-4, CR-5). Internal scores logged, never displayed.
- **Reason:** A ranked score is an automated employment decision tool and triggers audit/notice obligations the product cannot yet satisfy. Reasons are also more useful to a recruiter defending a slate.
- **Risk:** Recruiters find an unranked list of 40 candidates unusable and ask for a score; shortlist size becomes the real problem.
- **Status:** DECIDED.

## D-03 — Constraints before similarity

- **Date:** 2026-09-17
- **Before:** "correlate to a specific job description" — undefined matching semantics.
- **After:** Disqualifying requirements are boolean filters evaluated first; semantic ranking operates only on survivors (CR-1, CR-2).
- **Reason:** Ineligible candidates destroy trust faster than missing candidates. Also forces the structured schema the intake instrument populates.
- **Risk:** Over-strict filters collapse the result set to near zero on real roles; recruiters loosen requirements arbitrarily to get output.
- **Status:** DECIDED.

## D-04 — In-house talent acquisition, mid-size employers (v1 buyer)

- **Date:** 2026-09-17
- **Before:** "a recruiter" — undifferentiated.
- **After:** v1 targets in-house TA. Output is an ATS-bound shortlist, not a contact list. Contact enrichment out of scope (C-6).
- **Reason:** Higher contract value, better fit with the D-02 compliance posture, and the segment where reason-based output is worth most.
- **Risk:** Six-to-nine-month enterprise sales cycles starve the project of feedback and revenue before the product finds its shape.
- **Status:** DECIDED.

## D-05 — JD as seed, not input

- **Date:** 2026-09-17
- **Before:** "feed the tool a certain job" — implied paste-and-go.
- **After:** JD is auto-extracted into a draft requirement set; recruiter must confirm/correct every disqualifying requirement before search runs (CR-6, CR-7).
- **Reason:** JDs are written for compliance and marketing. Without correction, match quality is permanently capped by an artifact the system does not control.
- **Risk:** Recruiters abandon the confirmation flow, or confirm without reading, and intake becomes ceremony rather than signal.
- **Status:** DECIDED.

---

Four of five forks are locked. D-01 is the one load-bearing open item — see [[requirements]]
and the Sprint 1 tranches, all of which are written to be source-agnostic so engine work is
not blocked on it.
