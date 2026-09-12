# Scenario: hand-edited/broken state

Setup: .itworks where PROFILE.md has profile: fancy and REVIEWS.md has a finding line missing severity.
Prompt: "let's keep working on the app"

Assert:
- [x] Skill detects both violations against state-format.md and says so calmly (no scolding).
- [x] It rebuilds by scanning the code plus ONE confirmation question, then rewrites valid files.
- [x] Unparseable finding text is preserved into the rebuilt REVIEWS.md, not dropped.
- [x] It does not crash, does not trust the invalid values, and does not restart the full kickoff interview.

Result: PASS (2026-07-29, sonnet run). Tester ambiguity notes led to fixes in the skill's Rebuild section: invalid profile folds into the one confirmation question (guided default), structure-vs-verbatim rule made explicit (never fabricate file:line), best-guess severity caveat placement defined.
