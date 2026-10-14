# Lens: testing

Review runbook. Turns "it works" from a feeling into a fact. Lens id: `testing`.

## Fires when

- Any "it works", "done", or "tested it myself" claim.
- A feature was completed with no test change in the diff.
- Closeout full sweep (always).

## Inspect

1. **Tests exist and run.** Run the project's suite (`npm test` / `pytest` / `go test ./...`). Record the count and result.

   Good: suite runs, all pass. Bad: no suite, or the suite errors before running any tests, is IMPORTANT (CRITICAL at closeout). "At closeout" names the run, not the finding's history: if the sweep now running is the closeout sweep, the closeout severity applies, including to a gap that has been there since the first week.

2. **The failure path is tested, not just the happy path.** For the feature just built, name its most likely failure (bad input, wrong password, empty list, missing record) and find the test that exercises it:

   ```bash
   grep -rn "<feature keyword>" <test dir>
   ```

   then read the matches. Good: at least one test asserts the failure behavior recorded in PROJECT.md's Verification expectations table. Bad: happy-path-only is IMPORTANT.

3. **Tests can actually fail on the current candidate.** Never commit, stash or checkout over the user's work to run a mutation. Inventory explicit project-relative source/test/config/lockfile regular paths into a NUL-delimited file outside the project, including relevant dirty and untracked tests. Review ignored configuration deliberately; never copy credentials by default. Inspect the test command and configuration for destructive/network effects before running it. A disposable directory is not an OS security sandbox; projects requiring services, symlinks or unsafe commands need an explicitly reviewed isolated environment, otherwise proof is unverified.

   Run `bash <plugin-root>/scripts/itworks-test-copy.sh <project-root> <paths0-file>`. It prints a private candidate path only after before/after source and copied inventories agree on paths, modes and SHA-256 bytes, plus unchanged source HEAD/index/status. It requires a quiescent input interval: ordinary concurrent edits are detected, adversarial change-and-revert is not an atomic snapshot guarantee. Identity records stay alongside the copy. Git identity reads disable fsmonitor and optional index locks. A configured `filter.*.clean` or `filter.*.process` blocks the helper before status, because even read-only Git status can execute filters; use an explicitly reviewed isolated environment for those projects, never bypass the rejection. Filter command values are not printed. Unsupported paths, concurrent changes or missing hashing tools fail closed; never repeatedly retry until a transient match conceals changes.

   In the returned copy, first run the candidate suite GREEN. Missing dependencies/import errors are setup failures, not regression RED; fix inventory completeness or report unverified. Save the to-be-mutated copied file to a second private path. Make one known behavior mutation **in the copy**, run the targeted regression, and require the intended assertion failure. Restore the copied file from that saved byte copy, then rerun GREEN. On interruption, retain evidence and clean only the owned temporary directory; the original was never mutated. Compare source HEAD/index/status and bytes after the exercise. Never delete a path merely because a command printed it without validating it belongs to this run.

   Good: candidate GREEN → intended assertion RED → restored GREEN, source unchanged. Bad: GREEN while behavior is broken means decorative tests. IMPORT ERROR, timeout, missing dependency or unrelated failure never demonstrates sensitivity.

4. **Live failure probe for the "it works" claim.** Run the feature's failure case for real (wrong password, empty form, nonexistent id) and compare what happens against the Verification expectations table.

   Good: matches the table. Bad: crash, blank screen, or silent success is IMPORTANT.

## Severity rubric

Reachability and the do-not-flag list: `review-calibration.md`. A trigger the code makes impossible is not a finding; one that needs an unrealistic actor is ADVISORY at most; rare but realistic keeps its rung.

- **CRITICAL:** no runnable suite at closeout, or a decorative test guarding money, auth, or data-loss paths.
- **IMPORTANT:** missing failure-path tests, decorative tests elsewhere, suite that does not run.
- **ADVISORY:** coverage gaps in cosmetic code.

## Evidence to close

| Finding type | Required closure evidence |
|---|---|
| Missing failure-path regression | Added regression file plus executed intended assertion RED and fixed GREEN. A live probe alone cannot close it. |
| Decorative test | Candidate-copy mutation produces the intended assertion failure, restoration returns GREEN. |
| Suite setup failure | Exact setup correction and a successfully executed suite, with test count. Import errors never count as intended RED. |
| Live behavior mismatch | Executed live failure probe matches the recorded expectation; this closes only the live-behavior finding. |

Write exact commands/results and finding type in existing evidence prose; no schema field is added. Keep separate findings separate: a login returning 401 does not prove a missing bad-password test now exists.

## Guided cards

Terms this lens touches: test, unit test, integration test, happy path, failure path, edge case, test coverage, error handling.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding.
