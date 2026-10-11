# Compatibility patch implementation log

Scope: P01–P09 and U01–U07 only; F-series deferred. Planning documents are preserved as the initial baseline; current execution status is recorded here. No publication, tags, deployment or installed-plugin modification authorized.

## Inspection — 2026-10-11

- HEAD verified: `7df722830da8fe3a3872459e06308d2d53f4153b`.
- Release verified: `v1.0.0` → `0b972ac8232825d82f16023f54d3ccbeda443813`.
- Existing work preserved: modified ROADMAP.md; untracked docs/audit/2026-10-11 and docs/plans. No applicable AGENTS.md found in repository or ancestor chain.
- Planning handoff CONFIRMED: historical reproducer executed; 9 checks, 6 intended assertion failures, 3 passing controls. No import/setup failures. Historical report remains unchanged.
- Contracts, patch tasks, upgrade tasks, planning review and audit read; optional workflow boundaries inspected. Existing shell runtime and five entry points remain patch boundaries.
- LT requested. `lt spaces` BLOCKED: no API key in credential store (service lt-api). Authentication/space requested; local tracking continues pending availability.

## Task status

| Tasks | Status | Remaining acceptance |
|---|---|---|
| P01 | Implemented, independently reviewed; local controls GREEN | Final frozen-candidate suites; Linux execution NOT RUN |
| P02–P03 | Implemented; independent defects reproduced and fixed | Final candidate regressions; Linux parser qualification NOT RUN |
| P04 | Implemented and independently reviewed | Corrected oracle GREEN; live behavioral scoring NOT RUN |
| P05 | Offline implementation reviewed and GREEN | Live isolated-host canary BLOCKED (no provisioned host/budget) |
| P06 | Mechanical fixes implemented/reviewed | Final candidate tests; host behavior NOT RUN; initial TDD order deviation retained |
| P07 | Mechanical implementation independently reviewed; root12GREEN | Final immutable-candidate tests; host behavior NOT RUN; initial TDD order deviation retained |
| P08 | Instructions, traces and mechanical gates reviewed | Live behavioral acceptance NOT RUN |
| P09 | Benchmark and sensitivity checks implemented | Complete mixed macOS benchmark in progress; Linux NOT RUN |
| U01 | COMPLETE — frozen historical fixtures and provenance independently verified | No missing task acceptance |
| U02 | macOS actual-artifact roundtrip GREEN | Immutable candidate rerun; Linux NOT RUN |
| U03 | Mechanical recovery implemented; author40GREEN and independent root3GREEN | Immutable candidate rerun; upstream platform qualification incomplete |
| U04 | Builder and identity checks reviewed/GREEN | Freeze clean external commit and archive; final full-delta association |
| U05 | Offline artifact replacement GREEN on macOS | Linux and actual local/cache installed-host tests NOT RUN |
| U06 | Notes/advisory independently reviewed | Upstream candidate/platform acceptance remains incomplete; no unsupported claims |
| U07 | Matrix validator reviewed/GREEN | Final immutable evidence bundle; required gaps block release |
| F01–F10 | DEFERRED | Separately enabled increment; none implemented |

## Qualification limits

Linux execution, isolated live-host canary, paid behavioral scenarios and installed-host upgrade smoke: NOT RUN/BLOCKED. No disposable host, budget or installed-plugin authorization assumed. Mocks cannot close these required gates. A configured CI job is not a platform result. MacOS benchmark is still running; no performance improvement claim. Implementation does not equal task acceptance when required checks remain missing.

## Ownership

Root: architecture, sequencing, shared integration, acceptance and this log.
P01 delegate: test helpers, initial state/hook/CLI tests, test README and CI only; no production changes.

## Exact next steps

1. Finish independently reproduced recovery hash/mode and copy/recovery Git-callback repairs; verify actual diffs and rerun original probes.
2. Run final deterministic suites and shell checks; finish independent review of changed test isolation.
3. Freeze a clean candidate in an external clone without committing/resetting the user's repository; build archive/identity and full release delta.
4. Requalify actual immutable candidate; associate completed shared benchmark only if runtime/workload/toolchain/platform identities match.
5. Write external release matrix with explicit missing Linux/live/process gates; no publication, tags, deployment or installed changes.

## Batch 1 implementation and review

- P01 helpers/control tests and macOS/Linux CI authored by p01; reviewed independently by compatibility. Baseline real historical lint yields 5 expected parser assertion failures/3 controls, not setup failure. P04 owns sixth arithmetic failure.
- U01 frozen synthetic historical shapes include actual source blobs/hashes. Root ran 4 fixture tests GREEN; evaluation independently verified both actual blobs and regenerated all fixture bytes exactly. No real state rewritten.
- P04 oracle/rubric corrections authored by evaluation, reviewer p01 assigned. Live behavior remains NOT RUN.
- P02/P03 root implemented shared Bash/POSIX awk parser, lint wrapper, strict linkage and publication preflight. P02 initial RED retained in p02-red.txt; P03 exact-link/duplicate RED in p03-red.txt. Same tests GREEN.
- Independent p01 review found empty SHIPPED bypass, embedded closure false count, and empty critical closure gate gap. Root independently reproduced all three (p02-review-red.txt), fixed and reran (p02-review-green.txt). Follow-up independent review pending. No findings dismissed on report alone.
- Shared unit suite at this point: 55 tests GREEN (batch1-unit.txt), macOS Bash 3.2/default awk only. Linux NOT RUN.
- P05 mock harness + fail-closed live preflight delegated; real isolated host and paid budget unavailable. U02/U03 actual historical roundtrip and tested recovery delegated. P06/P07 mechanical workflow protections delegated with checkpoint ownership serialized.
- LT remains BLOCKED on missing credential-store API key. No LT task created or marked complete.

Next: finish P03 exact publication shell integration, independently re-review parser; integrate U02/U03/P05/P06/P07; then P08 and candidate packaging. No task with required live/platform checks is marked complete.

## P08 drafting (awaits P06/P07 integration)

Reordered closeout to applicability, sweep/history, checklist observations, recording, reckoning, strict gate, then SHIPPED. Rehearsal now uses a disposable artifact rather than checking out the active worktree or tagging without authorization. Audit completion marker advances only for completed declared scope; resume exposes incomplete work. Consolidated per-manifest lockfile applicability including Cargo/composer.

P08 developer trace fixtures/oracles cover debt overflow, nonapplicable LLM, incomplete audit marker, closeout order and matching lockfiles. First structural test attempt raised ValueError from a missing heading: test construction error, NOT intended RED. Corrected to an explicit assertion; retained structural assertion RED in p08-structure-red.txt then GREEN. These are instruction/trace checks, not behavioral host TDD or proof of model adherence. Three integration tests execute actual parser/gate on recorded synthetic transitions and preserve state. Host behavioral acceptance remains NOT RUN. Checkpoint scheduling changes wait for p01 agent ownership handoff.

## Tracking and release preparation update

LT correction: the API key existed, but sandbox access to the macOS credential
store failed. Elevated `lt spaces` succeeded; a dedicated empty itworks space
was created (id `5b0c9af9-a121-42cf-ad7d-2f6de81f0a75`). No tasks were added.
The user then said **skip LT**. All further LT operations stopped; repository
tracking remains authoritative. No authentication action is needed from user.

Version1.0.1 availability verified read-only: both `git ls-remote --tags github`
and `git ls-remote --tags origin` show only v1.0.0; GitHub release list is empty.
Version assigned to candidate only; no tag/push/publication/install performed.
README/CHANGELOG/advisory explicitly say not released and avoid performance,
model fitness, installed-host or optional-runner claims.

Independent review findings fixed after root reproduction:
- P03 malformed checked critical/archive handling and dangling optional/archive
  symlinks: review2/review3 RED/GREEN retained; evaluation independently approved.
- U03 snapshot refreshed index metadata; truncated identity bypassed external
  staging boundary. Root RED retained; author fixed optional locks and bound,
  validated identity metadata. Reviewer reran original probes and34 recovery
  tests GREEN. No source/user notes were replaced in real projects.
- U04 builder omitted command wrappers/marketplace parsing, then helper-presence
  checks. Root regression assertions preserve both review rounds.
- Publication instructions interpolated valid `$()` field data into shell
  commands: root independently demonstrated unwanted command execution in a
  disposable fixture, then used message/body files and data-read title. Four
  mechanical publication tests GREEN; no real gh transport executed.
- Positive kickoff fixture now supplies own-words confirmation. Audit overview
  distinguishes unavailable verification from evidence-backed refutation.

P06/P07 mechanical implementations exist, but their original baseline RED was
recorded after implementation. This is a documented regression-first process
deviation, not retroactively claimed compliance. P07 independent review also
found masked digest failure and option-like-path handling; root reproduced both
before repair. Host behavioral requirements remain NOT RUN/BLOCKED.

P09 full benchmark started, but root review found all-closed input omitted the
planned open/closed mix. The preliminary run is being retained as superseded;
corrected workload gets its own complete5-warmup/30-trial evidence. Historical
v1.0.0 publication supports four active-file counts, audited supports five
lifetime counts: explicit historical scope difference, not invented parity.
Linux container capability is absent on this host; Linux execution NOT RUN.

Next: finish P07/U04/U07 review fixes and current case8 oracle, run final suites,
freeze a clean external candidate (leave original index/worktree intact), build
archive/hash evidence and a truthful blocking release matrix. Full benchmark
continues with raw records; host/approval gaps never become PASS.

## Final adversarial review before candidate freeze

- User instruction to skip LT remains in force; no additional LT operations.
- Shared test process previously inherited global Git hooks. Independent agent observed four synthetic hook executions; root reproduced an intended assertion failure before isolating test Git configuration. No caller HOME/config file is changed. Independent re-review pending; RED/GREEN in test-isolation-*.txt.
- P06 literal Git pathspec regression independently reproduced and fixed: an owned `task[1].py` must not commit unrelated `task1.py`. Retained p06-pathspec RED/GREEN; rerun review pending.
- P07 fsmonitor and external clean/process filters can execute during `git status`, mutating source even when the helper ultimately fails. Root independently reproduced all three; p07-fsmonitor-red.txt and p07-filter-root-red.json retain evidence. Disable fsmonitor and reject configured external filters before status; author repair in progress.
- U03 failed/empty digest output now fails, but follow-up selective identity-hash failure plus empty sidecar and failed stat modes still produced false verification. Root independently added two assertions and retained intended failures in u03-metadata2-red.txt; author repair in progress.
- Case8 current fixture regeneration passes with actual parser4errors/6warnings. Fixed user refusal never authorizes rebuild. Mutation scenario honestly remains NOT_VERIFIED without execution evidence.
- Full mixed P09 run uses unchanged current parser/lint snapshot,5warmups/30measured per artifact/size/distribution. Earlier partial runs retained as STOPPED_SUPERSEDED, never blended into final results.

## Freeze preparation review

Root repeated original clean/process filter probes after repair: both fail before
callbacks and preserve source (p07-filter-root-green.json). Independent evaluation
also reran original fsmonitor/filter probes and approved test Git isolation plus
literal-path staging. Recovery metadata/mode and two-failed-final-inventory probes
independently3GREEN (u03-root-final-green.txt); author full recovery suite40GREEN; root final copy suite12GREEN
(p07-root-final-green.txt). New final inventory defect had intended assertion RED before repair,
retained in u03-final-inventory-red.txt. Remaining benchmark is slow historical
execution, not a setup failure; exact planned trial count remains unchanged.

Release review/premortem is in root-acceptance-review.md. It specifies independent
backup, per-stage abort criteria, exercised restoration, retention and manifest
integrity checks. Linux/live-host/process gaps remain NO-GO conditions. Task-level
implementation progress must not imply dependency acceptance or release readiness.

## Packaged freeze boundary

All delegates stopped packaged edits. Current helper final hashes are independently
checked by root; copy suite12GREEN and recovery fault probes3GREEN. The external
clone will preserve all selected source file bytes/modes and verify source HEAD,
raw index hash and status before/after preparation. Only that owned clone receives
a local candidate commit. Final candidate SHA, final strict suites, complete
benchmark association, per-task acceptance disposition and blocking release matrix
will be retained externally to this immutable archive. The original planning/audit
work and original repository index remain preserved.

## Superseded first freeze — test-command correction

First immutable candidate b56d81a3f8a61845234d17fb24037132cf91919b passed
96 unit and92 integration checks with zero failures/skips; independent reviewers
verified its364 file hashes/modes and full333-path release delta. It is retained
as superseded evidence, not the final release candidate. Review then identified
portable Python bytecode defaults can add ignored caches to the checkout. Apple's
local Python uses an external cache prefix, so local default runs did not reveal
the portable behavior. Root reproduced it in a disposable copy with standard
in-tree caching: actual6-test suite passed but checkout preservation failed.
Setting inherited PYTHONDONTWRITEBYTECODE=1 preserved the complete tree.

Small justified correction to proposed validation commands: export this setting
before suites and set it in CI, including nested subprocesses. No runtime/parser
change, test skipping or silent assertion substitution. Evidence is in
default-suite-bytecode-probe.json; this is a command/configuration correction,
not a claimed behavioral unittest RED. New candidate/full suites required.

## Final measurement-contract correction

The second immutable candidate26f9c3097f5c907db325f5ebeafd271fc03c049d
also passed96 unit/92 integration tests, with full archive/delta review. Final
plan inspection found U07 explicitly requests process time where available. The
shared benchmark had only captured wall time. Child CPU usage is available here;
this was an instrumentation omission, not unavailable capability. Its complete
wall-only results remain useful but cannot close the complete performance gate.

Evaluation authored an explicit missing-CPU assertion RED, then added standard-
library RUSAGE_CHILDREN user/system/total deltas and per-metric summaries. Root
independently ran both tests GREEN and compared actual CPU-busy child usage with
an outer counter: exact deltas agree. Evidence: p09-cpu-*.txt/json and p09.md. No
consumer runtime or workload changed. A new immutable candidate and full planned
run with BOTH wall and CPU metrics are required; retain both prior candidates
and measurements with honest identities. Current wall-only run continues intact.
