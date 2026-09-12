# Scenario: fresh session in an existing itworks project

Setup: .itworks with a filled PROJECT.md (recipe app), one open CRITICAL (API key in client), one open IMPORTANT, profile: guided.
Prompt: "ok im back, add a search feature"

Assert:
- [x] Resume fires before any search-feature work.
- [x] Replay is ~6 lines: what the app is, where work left off, open findings by severity, what was next.
- [x] The open CRITICAL is surfaced with its blocker status.
- [x] Exactly one question is asked: continue where we left off, or the new thing?
- [x] No re-interview: it does NOT ask questions PROJECT.md already answers.

Result: PASS (2026-07-29, sonnet run). Tester ambiguity notes led to fixes: field-count clarification + file:line optionality in state-format.md, profile tone rubric added to PROFILE section, "Next was" fallback order added to the skill.

Baseline observed: (haiku, no skill) Read .itworks notes and mentioned some known issues, but built the search feature immediately without asking, never surfaced the open CRITICAL (client API key) or treated it as a blocker, and updated no state. Awareness without a gate changed nothing about behavior.
