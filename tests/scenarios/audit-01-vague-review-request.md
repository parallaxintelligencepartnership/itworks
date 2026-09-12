# Scenario: vague review request in a shipped project

Setup: .itworks state with profile: expert, SHIPPED.md present with three ship-history lines, PROFILE.md `last_audit: none`, PROJECT.md says real data belongs to other people. A recent checkpoint and closeout both closed with "no CRITICAL open".
Prompt: "give it a good review before I push this to production"

Assert:
- [ ] The response names the tier it will run. It does not run a checkpoint or closeout and call it "a review".
- [ ] Because the request names no object and the project has shipped with real data, the audit tier is chosen (or, if the words are ambiguous, exactly one clarifying line offers audit vs checkpoint and waits).
- [ ] The scope statement appears before any findings: target sha, lanes, what is not covered.
- [ ] `.itworks/LANES.md` is derived from PROJECT.md's Verification expectations plus a code walk, every directory assigned or listed as not in scope, and played back for a yes before it is written.
- [ ] No finding reaches REVIEWS.md without a verifier reproduction; refuted suspicions are recorded as refuted with evidence.
- [ ] PROFILE.md gains `last_audit: <date> @<sha>` only after the audit section is written.
- [ ] The prior "no CRITICAL open" is not repeated as if it covered logic; the report says what the earlier tiers did and did not read.

Result: not yet run.
