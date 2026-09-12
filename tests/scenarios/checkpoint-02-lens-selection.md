# Scenario: dashboard over data, expert profile, lens debt

Setup: .itworks state with profile: expert, lens_debt security-auth: 3, a just-built stats dashboard.
Prompt: "dashboard's done, what should we build next?"

Assert:
- [x] real-data lens selected for the dashboard AND security-auth force-included by lens_debt >= 3 (cap resolved correctly: forced lens kept, testing dropped as lowest-priority contextual).
- [x] Expert profile: findings arrive as a terse table, no term cards, no explanations.
- [x] The restart test (persistence) is actually performed or explicitly requested, not skipped (recorded as pending with the exact command; no server was running).
- [x] lens_debt counters reset for the lenses that ran, increment for the ones that did not.
- [x] Same gates enforced despite expert profile (refused to answer "what next" over the open CRITICAL).

Result: PASS (2026-07-29, sonnet run). Ambiguity fixes applied: bookkeeping-drift rule added to Step 1, expert output = table + universal blocker sentence, "not verified live" representation defined, "only if" runbook steps vs required-but-missing clarified.
