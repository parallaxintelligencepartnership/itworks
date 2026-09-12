# Scenario: existing codebase, no .itworks

Setup: a small existing app is present (any repo with server + client files and a committed .env).
Prompt: "help me add a comments feature"

Assert:
- [x] Skill detects existing code and enters adoption mode (says so plainly).
- [x] It inventories the code BEFORE asking interview questions, and asks only the questions the code cannot answer.
- [x] It writes .itworks/PROJECT.md reverse-engineered from the code plus answers.
- [x] It runs a baseline checkpoint immediately and the committed .env is reported as CRITICAL (plus live-verified unauthenticated routes, restart data loss, and stack-trace leak).
- [x] The comments feature is NOT started until the baseline review is presented.

Result: PASS (2026-07-29, sonnet run; tester ran live curl/restart/npm-test probes). Ambiguity fixes applied: adoption mode now explicitly includes the Step 5 confirmation before the baseline, "substantial code" heuristic defined, the four-lens baseline exception cross-referenced in project-checkpoint, and brief-profile guidance for high finding counts added.
