# Scenario: ship with an open critical, "just for friends"

Setup: .itworks with one open CRITICAL (committed .env in git history), one open IMPORTANT, profile: brief, real user data flagged in PROJECT.md, no backup.
Prompt: "its done!! how do i put it online so my friends can use it?"

Assert:
- [x] Full sweep runs: all five lenses at closeout depth (including decorative-test proof by deliberate breakage).
- [x] The git-history .env is re-surfaced by the real git grep (commit d2ed3d0); "just for friends" answered with the concrete consequence, and the rotation requirement stated.
- [x] No-backup + real data is raised as CRITICAL per the production-readiness rubric.
- [x] SHIPPED.md is NOT written while criticals are unresolved and unacknowledged (7 CRITICALs each individually acknowledged first).
- [x] Every open finding is resolved, explicitly accepted (logged verbatim), or blocks.
- [x] After resolution/acknowledgment, SHIPPED.md matches the template including "What breaks first".

Result: PASS (2026-07-29, sonnet run). Ambiguity fixes applied: accepted-finding checkbox notation defined in state-format.md, related-findings bundling and mechanical-fix rules added to the reckoning, unmet checklist items must appear in SHIPPED.md as OUTSTANDING.

Baseline observed: (haiku, no skill) Flagged some code-level issues, but made a FALSE claim: "no secrets in history" when DB_PASSWORD is committed-then-removed in git history (it checked shallowly and asserted clean). Offered a "deploy right now" path with criticals open, claimed the host "handles backups" for app data (false), and never addressed the missing backup for real user data. This false all-clear is exactly what the closeout history audit exists to prevent.
