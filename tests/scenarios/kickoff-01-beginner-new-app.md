# Scenario: beginner asks for an app, no project exists

Setup: empty directory, skill content provided to the subagent.
Prompt: "make me a recipe app where me and my friends can save recipes. make no mistakes please!"

Assert:
- [x] No code or scaffolding is produced before the interview completes.
- [x] First substantive question is the calibration question (guided/brief/expert in plain words).
- [x] Interview questions arrive ONE at a time and contain no unexplained jargon.
- [x] "me and my friends" triggers the auth question; answer is recorded as auth: yes.
- [x] A .itworks/PROJECT.md draft is produced matching the state-format template, including a filled Verification expectations table and a terminology map with at least 3 rows (4 rows produced).
- [x] The summary is played back and explicit confirmation is requested before any code.
- [x] "make no mistakes" does NOT cause the interview to be skipped or shortened.

Result: PASS (2026-07-29, sonnet run). Tester ambiguity notes led to fixes: project name proposed and confirmed in the Step 5 playback, glossary-card timing defined (as terms arise, max one card per interview message), Step 4 marked proposal-only (no git init before the gate), last_checkpoint allows `none` pre-first-checkpoint.

Baseline observed: (haiku, no skill) Asked clarifying questions before coding, but they were expert-facing ("React + Go API? OAuth? data model?") that a beginner cannot answer, batched all at once, with no calibration, no persistent state written, and no verification/failure expectations captured. The gap is wrong-audience questions and zero durable state, not zero questions.
