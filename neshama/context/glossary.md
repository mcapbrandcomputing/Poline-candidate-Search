# Glossary

| Term | Definition |
|---|---|
| JD | Job description. Treated as a *seed* for extraction, not a trusted search input (D-05). |
| Disqualifying requirement | A requirement typed as a hard boolean filter (CR-1). Failing one removes a candidate from output entirely, at any position. |
| Preferred requirement | A requirement that only affects semantic ranking (CR-2), never a hard exclusion. |
| Reasons array (`reasons[]`) | Per-candidate list where each element names one intake requirement and the specific profile evidence satisfying it (CR-3). |
| Collection basis | One of `licensed`, `public-permissible`, `candidate-submitted` — the legal basis under which a candidate record was collected (CR-8). Records without one are not indexed. |
| Source adapter | An isolated integration to one external candidate source, implementing a common interface so sources can be added/removed without touching the matching engine (CR-9). |
| Shortlist | The non-ranked, stable-order set of candidates shown to the recruiter (CR-5). Never a ranked list. |
| Intake instrument | The structured Block A–D question set a recruiter completes per requisition (see [[requirements]]). |
| Exemplar (positive/negative) | A named real person used at intake to calibrate matching by example rather than description (Block C). |
| ATS | Applicant Tracking System — the recruiter's existing system of record; v1 output is ATS-bound, not a contact list (D-04, C-6). |
| SLA (suppression/deletion) | The defined turnaround time within which a suppression or deletion request must propagate to the index (CR-10). Value TBD — see [[backlog]]. |
| Freshness floor | Recruiter-set recency threshold; profiles updated before this are excluded from a search (Block D). |
| Position (decision class) | A decision explicitly held open pending a external trigger, as opposed to `Decision` (locked). D-01 is the only Position. |
