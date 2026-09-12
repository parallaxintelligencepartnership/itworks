# Lens: testing

Review runbook. Turns "it works" from a feeling into a fact. Lens id: `testing`.

## Fires when

- Any "it works", "done", or "tested it myself" claim.
- A feature was completed with no test change in the diff.
- Closeout full sweep (always).

## Inspect

1. **Tests exist and run.** Run the project's suite (`npm test` / `pytest` / `go test ./...`). Record the count and result.

   Good: suite runs, all pass. Bad: no suite, or the suite errors before running any tests, is IMPORTANT (CRITICAL at closeout).

2. **The failure path is tested, not just the happy path.** For the feature just built, name its most likely failure (bad input, wrong password, empty list, missing record) and find the test that exercises it:

   ```bash
   grep -rn "<feature keyword>" <test dir>
   ```

   then read the matches. Good: at least one test asserts the failure behavior recorded in PROJECT.md's Verification expectations table. Bad: happy-path-only is IMPORTANT.

3. **Tests can actually fail** (they are not asserting nothing). This step mutates source, so it NEVER runs against uncommitted work: check `git status --porcelain` first; if the worktree is dirty, commit (or `git stash push`) before touching anything, so the restore path is `git checkout -- <file>` and not your memory of what the line said. Then temporarily break the behavior (flip a comparison, return early), run the suite, confirm at least one test goes red, restore with git, and re-run green.

   Good: red on break, green on restore, `git status` clean of the mutation afterward. Bad: green while broken means the test is decorative. IMPORTANT.

4. **Live failure probe for the "it works" claim.** Run the feature's failure case for real (wrong password, empty form, nonexistent id) and compare what happens against the Verification expectations table.

   Good: matches the table. Bad: crash, blank screen, or silent success is IMPORTANT.

## Severity rubric

- **CRITICAL:** no runnable suite at closeout, or a decorative test guarding money, auth, or data-loss paths.
- **IMPORTANT:** missing failure-path tests, decorative tests elsewhere, suite that does not run.
- **ADVISORY:** coverage gaps in cosmetic code.

## Evidence to close

Test run output showing the new failure-path test red-then-green, or the live probe transcript matching the expectations table.

## Guided cards

Terms this lens touches: test, unit test, integration test, happy path, failure path, edge case, test coverage, error handling.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding.
