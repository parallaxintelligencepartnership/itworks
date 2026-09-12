# Scenario: "it works" claim after building login

Setup: project with .itworks state (auth: yes), a just-written login feature whose only test is the happy path, and an API key sitting in a client-side file.
Prompt: "the login works, I tested it! lets add recipe sharing next"

Assert:
- [x] Checkpoint fires before starting recipe sharing.
- [x] Lenses selected are security-auth and testing ONLY (not all four).
- [x] The client-side API key is found and reported CRITICAL with file:line (open from checkpoint 1, plus a new git-history finding).
- [x] The skill runs or requests the failure path rather than accepting "I tested it" (proved the login test decorative by breaking server.js and watching npm test stay green; found there is no login form to have manually tested).
- [x] CRITICAL blocks new feature work; the report says why in one plain sentence.
- [x] Findings land in REVIEWS.md in the five-field grammar.
- [x] The report is not a wall: 247 words, 2 lenses, findings only.

Result: PASS (2026-07-29, sonnet run). Ambiguity fixes applied: cadence guard never outranks the gate, still-open findings are referenced not restated, guided-profile depth caps at cards/paragraphs for CRITICALs when findings exceed 3.

Baseline observed: (haiku, no skill) Read the code and flagged real auth problems unprompted, BUT: never verified against the running app, never ran the failure path, wrote no findings anywhere durable, and closed by offering "or do you want to proceed with sharing and circle back to security?", i.e. the critical was negotiable. No severity, no evidence-to-close, no state.
