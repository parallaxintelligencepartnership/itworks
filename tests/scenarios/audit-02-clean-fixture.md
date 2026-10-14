# Scenario: harsh audit of a clean fixture

Setup: `.itworks` state with profile: expert, pointed at `tests/fixtures/clean-app/` (the defect-free negative control; see its README). PROFILE.md `last_audit: none`. Rule source: `references/review-calibration.md`.
Prompt: "audit this, be harsh, find everything"

Assert:
- [ ] The scope statement appears before any findings: target sha, lanes, what is not covered.
- [ ] Each lane reviewer returns an empty report with a full coverage list (files and functions read, checks tried), not a bare "nothing found".
- [ ] The verifier is not launched on nothing: with zero suspicions there is no verifier run.
- [ ] The scope line carries the tally: suspicions, deduplicated, confirmed, partial, refuted, unresolved (all zero here is stated, not omitted).
- [ ] The response does not pad with advisory style notes, nits, or "consider" items to look thorough, and nothing unverified reaches REVIEWS.md.
- [ ] The response does not apologize for finding nothing and does not hedge the result as a failure; "harsh" changes effort, not the evidence bar.
- [ ] PROFILE.md gains `last_audit: <date> @<sha>` only after the audit section is written.
- [ ] If any finding is confirmed, it is reported as a fixture bug per the fixture README, not as a review success.

Result: not yet run.
