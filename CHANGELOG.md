# Changelog

## Unreleased

**Model requirement**

- Closeout and audit are pinned to Opus, and the plugin says so at install and at runtime.

**Publish**

- Publishing is rewritten around the pull request mechanism: an entry is one `entries/<id>.json` file submitted as a pull request to `parallaxintelligencepartnership/itworks-site`, and the site owner's merge is the approval.
- Added the `critical_accepted` field, so an accepted CRITICAL keeps the badge red instead of publishing as a clean record.
- The derivation rules for every published field are validated against the site's own receiving contract (`internal/entry/entry.go` and `docs/SPEC.md`).

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
