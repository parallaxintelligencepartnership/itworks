# 1.0.1 release qualification

Released 2026-10-11 from candidate `20c1b057f074fd3e8ee7c4e609d2a93d8019ec37`
(tree `5ec24be2cc29944c0ebbcb89923ae2223e6c1444`). The release commit adds only
release-state wording to README.md, CHANGELOG.md, docs/releases/1.0.1.md,
tests/host/README.md and this record. No runtime, skill, script or test file
changed after the candidate was frozen.

The full candidate evidence bundle (archive, Git bundle, gate matrix, benchmark
samples, superseded candidates) is kept outside the repository so it is not
copied into plugin installs.

## Results

| Gate | Result | Notes |
|---|---|---|
| Identity | PASS | 369 files and modes independently verified against the candidate archive |
| Unit, macOS | PASS | 97 tests, 0 failures |
| Integration, macOS | PASS | 92 tests, 0 failures |
| Release commit, macOS | PASS | 97 unit and 92 integration on the release commit. A first integration run under host load average ~360 took 576s and hit 6 errors in `test_state_recovery`; those 39 tests passed alone and the full rerun passed in 95s. Treat that module as load-sensitive |
| Unit, Linux | PASS | 97 tests, 0 failures. Debian bookworm container on an x86_64 Ubuntu 24.04 host; bash 5.2.15, mawk, Python 3.12.15, Go 1.23.12, non-root user |
| Integration, Linux | PASS | 92 tests, 0 failures, same container |
| Shell syntax | PASS | macOS /bin/bash 3.2 and Linux bash 5.2 |
| Installed upgrade, cached | PASS | Claude Code 2.1.296, isolated config dir, local Git marketplace. Installed 1.0.0 (66 files byte-identical to `v1.0.0`), then marketplace update and plugin update to 1.0.1 (369 files byte-identical to the candidate). Old 1.0.0 cache directory retained |
| Installed lint on compatibility fixtures | PASS | All 19 fixtures linted read-only (fixture hashes unchanged). 8 corrupt or malformed states that 1.0.0 passed now fail; valid and legacy states still pass |
| Installed upgrade, local directory marketplace | PASS | Maintainer's own install updated 1.0.0 to 1.0.1 |
| Live session canary | PASS | Fresh `claude -p` session (Sonnet) in a copy of the `v3-critical-star` fixture. Session start reported `itworks v1.0.1`; the resume skill ran the lint, reported `E_FINDING_SYNTAX` at `REVIEWS.md:5`, kept the CRITICAL severity and asked before any repair. 9 turns, $0.18 |
| Performance, macOS | PASS | 1050 trials with wall and child CPU timing, no regression trigger |
| Performance, Linux | NOT RUN | Developer benchmark only; no Linux performance claim is made |
| Pressure-harness live scenarios | NOT RUN | Independently judged multi-scenario model runs were not repeated for this patch; no new model reliability claim is made |

## Process deviation

P06 and P07 were not built regression-first as the plan required. The
regressions were added and pass, and the deviation stays recorded in the
implementation log. Accepted for this release.
