# Assumptions

Assumptions from the stated constraints (C-1..C-6) that must stay valid for the plan to hold.
If any of these breaks, re-open the affected decision in [[decisions]] before continuing.

- **A-1.** No candidate in the index has consented to being there — deletion/suppression
  (CR-10) must work even under a legal regime that grants candidates notice/access/deletion
  rights. Breaks D-04, C-1 if violated.
- **A-2. [SUPERSEDED 2026-09-17]** ~~The buyer (v1 = in-house TA, mid-size employer) runs every
  purchase through legal and security review...~~ Owner has confirmed this is a personal,
  single-user tool, not sold or distributed — the legal/security-review gate does not apply.
  If this tool is ever shared with, sold to, or used by anyone other than the owner, this
  assumption must be reinstated and D-01/C-2 re-opened before that happens.
- **A-3.** No single data source is load-bearing — the product must retrieve usable candidates
  even if any one source adapter is disabled. Breaks CR-9, C-3 if violated.
- **A-4.** Recruiter intake (Blocks A–D) completes in 3–5 minutes for a typical role. If real
  usage runs materially longer, C-4 is violated and the intake UX (not the schema) needs
  rework — do not respond by cutting required fields.
- **A-5.** All output surfaces (shortlist, reasons, UI copy) can be shown to counsel without a
  ranking, score, or hire/reject framing appearing anywhere. Breaks D-02, C-5 if violated.
- **A-6.** Contact enrichment (phone/email discovery) is out of scope for v1 — recruiters
  already have an ATS + outreach channel. Breaks C-6 if a design choice implicitly requires it.
- **A-7. [RESOLVED 2026-09-17]** D-01 is decided: personal use, direct scraping in scope,
  LinkedIn named explicitly as a target source (see Sprint 5). Engine/schema/UI (Sprints 1–4)
  remain source-agnostic regardless — that design choice is good practice independent of D-01,
  not a hedge against it. Sprint 5 implements the real LinkedIn adapter behind the S1T2
  interface.
