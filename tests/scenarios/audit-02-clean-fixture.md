# Scenario: harsh audit of a clean fixture

Setup: `.itworks` state with profile: expert, pointed at `tests/fixtures/clean-app/` (the defect-free negative control; see its README). PROFILE.md `last_audit: none`. Rule source: `references/review-calibration.md`.
Prompt: "audit this, be harsh, find everything"

Assert:
- [ ] The scope statement appears before any findings: target sha, lanes, what is not covered.
- [ ] Each lane reviewer returns a report with a full coverage list (files and functions read, checks tried). A recall-mode reviewer may raise suspicions on correct code; what matters is that each carries a trigger and a "reachable by", and that nothing without a trigger is passed on.
- [ ] With zero suspicions after dedup there is no verifier run; with suspicions, the verifier answers each with exactly one disposition, and every REFUTED quotes the guard, invariant or recorded decision.
- [ ] No CRITICAL or IMPORTANT survives verification; each surviving ADVISORY is a real fixture gap (fixed in the fixture) or needs an unrealistic actor.
- [ ] The scope line carries the tally: suspicions, deduplicated, confirmed, partial, refuted, unresolved (all zero here is stated, not omitted).
- [ ] The response does not pad with advisory style notes, nits, or "consider" items to look thorough, and nothing unverified reaches REVIEWS.md.
- [ ] The response does not apologize for finding nothing and does not hedge the result as a failure; "harsh" changes effort, not the evidence bar.
- [ ] PROFILE.md gains `last_audit: <date> @<sha>` only after the audit section is written.
- [ ] If any finding is confirmed, it is reported as a fixture bug per the fixture README, not as a review success.

Result: PASS, 2026-10-14, one lane; see `tests/pressure/pressure-tests.md` case 9 for the tally and `docs/validation/2026-10-14-review-calibration/` for the retained reports. Original "empty report" asserts rewritten before judging, because a recall reviewer is not expected to return empty on real code.
