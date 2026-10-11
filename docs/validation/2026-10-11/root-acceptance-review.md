# Integration acceptance and release premortem

Release remains **NO-GO** pending the external immutable-candidate matrix. A
reviewable local candidate is an authorized implementation deliverable, not
permission to publish, tag, deploy or change installed plugins.

## Independently checked implementation

Root reviewed the actual helper/parser, workflow and test changes against the
approved contracts, retaining the initial audit6RED/3controls. Distinct delegated
reviewers examined meaningful batches; their reports were checked against diffs
and independently run commands. Runtime parser defects, unsafe publication field
interpolation, literal-path staging, copy digest/options/Git callbacks and recovery
metadata/final-verification defects were reproduced before their repairs. Exact
RED/GREEN logs remain alongside the per-task reports. A failing tool invocation,
missing Go, timeout, fixture setup mismatch or import error is not an intended RED.

The historical fixtures use actual released/audited source blobs. U02/U05 exercise
actual Git archives and executable scripts; development working-tree runs remain
separate from final immutable candidate qualification. Historical bug acceptance
is recorded, not treated as fresh release permission. User-authored finding,
acceptance and SHIPPED bytes are preserved by read-only validation and roundtrips.

Root separately inspected evaluation-owned corrected overtime source/oracles,
case8 fixture regeneration, positive kickoff confirmation and mutation rubric,
offline harness, benchmark and sensitivity code. Regeneration/Go/fixture checks
execute actual code. Pressure rubrics permit honest held gates and cannot invent
execution evidence. Mock transcripts qualify transport mechanics only. Benchmark
counts execute the actual historical documentation; released four-active-count
semantics differ from audited/candidate five-lifetime-count semantics and are
explicitly recorded rather than faked as full parity.

Final full-suite output, exact source/archive hashes, coverage association and
benchmark results belong to the external candidate evidence bundle. Source-level
review does not establish real installed-host behavior. The original P06/P07
regression-first order deviation is retained; later successful regressions do
not rewrite that history.

## Failure stories and protections

1. **Source and destination both damaged.** Before an authorized repair, create
   and verify an independent backup outside project, plugin and cache. Backup
   state includes hashes/modes and protected identity metadata. Tests inject
   copy/hash/stat faults and reject unusable backup claims. No actual user-state
   repair has been performed during this implementation.
2. **Repair only partly applies.** Abort before writing on changed source, invalid
   staging, missing/deleted original state, bad backup, or failed restoration
   rehearsal. During write failure, preserve failed state separately and restore
   the rehearsed original. Tests exercise partial-write and interruption paths.
3. **Apparently successful repair loses notes.** Compare complete manifests,
   checking each inventory command's exit status before equality. Empty failed
   inventories cannot prove success. Preserve original quote/severity/closure
   history; semantic interpretation requires ordinary human review.
4. **Rollback also fails.** Stop with explicit manual-recovery requirement,
   retaining independent backup, staged candidate, restore copy and failed state.
   Never delete the remaining copies or retry automatically. Restore-to-empty is
   exercised and does not overwrite the original project.
5. **Git identity reads execute project programs.** Disable fsmonitor and refuse
   configured clean/process filters before status collection. Unsupported projects
   need a separately reviewed snapshot method. A disposable copy is not an OS
   sandbox; arbitrary project tests are not automatically run by the helper.
6. **Wrong installed package appears healthy.** Archive/version/hook identities
   and offline replacement tests identify candidate bytes. Actual fresh-session
   loaded-byte checks for both local and cache installs remain NOT RUN; therefore
   no installed-host compatibility claim or update command is qualified.

The recovery window is **at least30 days AND two verified subsequent work
sessions**, whichever is longer. Post-change acceptance requires manifest equality,
corrected lint/gate checks and relevant executed application evidence, not merely a
version banner. Writers must be paused: these shell operations are not atomic
filesystem snapshots and do not claim protection from an adversarial ABA edit.

## Remaining external gates

Linux suites/benchmark; provisioned disposable host and authorized model budget;
live canary and independently judged workflow behavior; real local/cache installed
upgrade smoke; explicit disposition of the documented TDD process deviation.
No missing gate is silently skipped or replaced by an offline PASS.
