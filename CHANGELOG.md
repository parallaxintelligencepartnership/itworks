# Changelog

## Unreleased

## [1.1.0] - 2026-10-14

Review calibration. See the [release note](docs/releases/1.1.0.md). No state
format change; the five-field finding grammar and `format_version: 3` are unchanged.

- New `references/review-calibration.md`: the mode each tier runs in (precision
  for checkpoint and closeout, recall then precision for the audit), zero findings
  as a valid and complete result, a trigger and a "reachable by" on every finding,
  a do-not-flag list, the reachability rule, evidence hygiene, dedup, gap sweeps
  for re-reviews, and the spoken-report shape.
- Audit: reviewer briefs state the mode and the do-not-flag list; a dedup step
  runs between reviewer and verifier; verifiers answer with a fixed set that now
  includes PLAUSIBLE (mechanism traced, trigger realistic but not producible here,
  recorded as open with its settling probe, never blocks completion); refutations
  must quote the guard; fabricated references refute on the spot; the scope line
  carries a tally; re-audits of an unchanged target run a gap-sweep brief.
- Checkpoint and closeout: stated precision mode, a clean step is recorded as
  clean, the closeout sweep no longer "expects to find things", ADVISORY findings
  are a count in the spoken report with every line kept in REVIEWS.md, and a
  finding type seen at three checkpoints gets a proposed deterministic check.
- Lens rubrics point at the reachability rule; no severity values change.
- Pressure cases 9 (negative control on a defect-free fixture), 10 (re-review of
  an unchanged target) and 11 (reachability at checkpoint); `tests/fixtures/clean-app`
  is the negative control (69 tests after the case 9 fixes).

## [1.0.2] - 2026-10-13

Audit patch, from the first audit of an outside repo. See the
[release note](docs/releases/1.0.2.md). No state format change.

- The audit skill triggers on "audit this repo" or "audit <path>", including a
  repo with no `.itworks/`; the method file says to start the skill, not run it
  by hand.
- Outside-repo mode: state and reports live in an evidence folder next to the
  target, minimal state is written without an owner interview, and nothing is
  written into the target tree.
- Untrusted code is read, not run: reviewers only read, verifiers execute only in
  a sandbox with no network, and the report names the isolation used.
- Reviewers and verifiers append one finding at a time, word reproductions as
  tests rather than attack steps, and end each file with a completion line the
  orchestrator checks, so safety-filter cut-offs no longer lose a lane silently.
- An approved plan that holds the lane table counts as lane approval.
- A finding can carry its own lens; the lane's lens is the default.
- Every verification carries a passing control case, and a lane whose verifier
  refuted nothing gets a blind re-check of up to three confirmed items.
- CI runs the Go oracle fixture on Go 1.27, the current stable release (was 1.23, past end of life).

## [1.0.1] - 2026-10-11

Compatibility patch. Existing users should read the
[upgrade advisory](docs/releases/1.0.1.md) before their next deploy; the stricter
lint can report errors in state that 1.0.0 accepted.

- One read-only shell/awk parser now checks strict profiles/headings, alternate
  malformed findings, closure fields and individual acceptance linkage. Strict
  gate/counts cannot turn ambiguous critical acceptance into clearance.
- Lifetime publication counts share that parser; state versions 1–3 and the five
  lifecycle commands remain supported without a Python runtime dependency.
- Added historical artifact roundtrips, external backup/recovery operations,
  candidate-copy checks, task-only staging guidance and deterministic test CI.
- Corrected overtime arithmetic/rubrics; simulation artifacts are complete,
  separate from private model metadata, and fail closed without qualified host
  isolation. No new live model reliability result is claimed.
- Clarified secret exposure context, finding-specific closure evidence, overdue
  lens scheduling, completed-audit currency and closeout observation order.

The following prior Unreleased changes are included in the full tag-to-candidate
review; they were not present in the released `v1.0.0` artifact:


**Model requirement**

- Closeout and audit retain their Opus frontmatter preference. Historical simulations do not establish a universal model capability boundary.

**Publish**

- Publishing is rewritten around the pull request mechanism: an entry is one `entries/<id>.json` file submitted as a pull request to `parallaxintelligencepartnership/itworks-site`, and the site owner's merge is the approval.
- Added the `critical_accepted` field, so an accepted CRITICAL keeps the badge red instead of publishing as a clean record.
- The prior publishing work checked field derivation against the receiver's `internal/entry/entry.go` and `docs/SPEC.md` at that time. This candidate does not claim a fresh external receiver integration test.
- closeout publish target and badge URLs now point at itworks.build (was itworks.dev)

**Runbooks**

- Added the injection patterns file so the injection step actually matches injections.
- The secret grep now sweeps the whole working tree, not just client directories.
- Greps run from the project root, with every `--include` glob quoted so the step runs correctly under zsh.
- Four new secret patterns: DB connection strings, AWS secrets, Discord and Telegram tokens.

**Lint**

- The linter now reads the last line of a file even when it has no trailing newline.
- Findings are checked for state-format alignment, so an open checkbox with no severity is caught as a contract violation.

**Skills**

- Every skill points at `<plugin-root>/references/`, never a relative path.
- Closeout and audit can be deferred, never turned off.
- The adoption baseline is offered once in un-instrumented projects.
- The HARD-GATE on deployment steps is bound to the finished reckoning, not to the sweep.
- Resume never downgrades a severity a line still states, so it keeps unreadable CRITICALs.

**Tests**

- Added pressure-test harness cases 7 and 8.
- Fixed the scenario lens count, which still counted four lenses.

## 1.0.0 - 2026-09-12

First public release.

- Five lifecycle skills: kickoff (alignment interview before any code), checkpoint (evidence-backed review of what was just built), resume (replay saved state in a few lines), audit (whole-application adversarial review with independent verification), closeout (full sweep, reckoning, ship checklist, SHIPPED.md).
- Five review lenses (security and auth, LLM security, real data, testing, production readiness) plus dependency vetting.
- Project state in `.itworks/`: PROJECT, DECISIONS, REVIEWS, PROFILE, and MAP. MAP.md is the code map and gotcha list: how to run and test the project, where the important code lives, what the hosts actually are, and the corrections the project has already paid for. Written at kickoff, patched at every checkpoint, read whole at resume.
- Deterministic state linter (`scripts/itworks-lint.sh`), format version 3.
- Opt-in publishing of closeout summaries to itworks.dev, with the exact sent-field list in `references/publish.md`.
- Adversarial pressure-test harness with six cases and fixed user scripts.
