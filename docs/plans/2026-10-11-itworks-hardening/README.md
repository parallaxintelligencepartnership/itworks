# itworks hardening implementation backlog

Status: **fully planned, implementation not started**. All 26 tasks are pending. This backlog upgrades a released product; it is not a first-launch plan. The compatibility patch is the first deliverable, followed by a separately enabled workflow increment. No task completion or release is implied by this document.

Planning baseline: local tag `v1.0.0` at `0b972ac8232825d82f16023f54d3ccbeda443813`; audited HEAD `7df722830da8fe3a3872459e06308d2d53f4153b`. Both currently advertise 1.0.0. The full tag-to-candidate delta belongs in release review. The [audit](../../audit/2026-10-11/AUDIT.md) is the evidence source; its nine-check reproducer was rerun during planning and still has six failures and three passing controls.

## Read and execute in this order

1. [Shared contracts](contracts.md): released-state compatibility, runtime boundaries, evidence, authorization and preservation rules.
2. [Compatibility patch tasks P01–P09](01-patch.md): executable regressions, parser, acceptance, evaluation correctness and safe lifecycle behavior.
3. [Upgrade and release tasks U01–U07](02-upgrade-release.md): actual old/new artifacts, recovery, unique identity, installed-host qualification and release notes.
4. [Opt-in workflow tasks F01–F10](03-opt-in-workflow.md): schemas, candidate snapshots, evidence, planning/TDD, orchestration, adapters and measurements.

Each task includes exact existing/new paths, implementation decisions, concrete failing cases and expected outcomes, implementation steps, validation commands, dependencies and completion/rollout criteria. Commands in these task documents are proposed interfaces or implementation-time checks; they must not be reported as already implemented or passed.

## Executive decisions

- Preserve the five existing lifecycle entry points, legacy Markdown state and shell runtime in the patch. Test Python is a development dependency only. Add the Python execution runner later, behind explicit enablement.
- Fix the meaning of validation/evidence before adding agent autonomy. Correctness failures and test infrastructure failures remain distinct.
- Never migrate or rewrite existing findings/acceptances merely to make the validator green. Read-only checks may expose old malformed records; interpretation/repair preserves user words and severity.
- Delegate bounded independent work, with one integrator for shared files. Require independent verification of behavioral changes; do not use model branding as a substitute.
- Ship an identified compatibility patch only after its release matrix passes. A provisional 1.0.1 is a planning choice; verify the version is unused before assigning it. Opt-in features receive their own release decision and qualification.

## Ordered tasks and dependencies

All rows are **PENDING**. Dependencies describe prerequisites for acceptance; independent drafting or test scaffolding can proceed earlier if it does not claim completion. IDs below are the cross-plan dependency contract. A range means every task in that range, not a choice of one.

| ID | Deliverable | Depends on |
|---|---|---|
| P01 | Deterministic script regressions, shared test helpers and CI | None |
| P02 | Shared read-only shell/awk parser and strict state syntax | P01 |
| P03 | Individual acceptance linkage and common publication counts | P02, U01 |
| P04 | Executable overtime oracle and coherent positive/negative rubrics | P01 |
| P05 | Isolated simulation, complete transcripts and blinded judge artifacts | P01, P04 |
| P06 | Context-aware secret findings and task-only staging | P01 |
| P07 | Stable disposable candidate copies and finding-specific closure proof | P01, P02 |
| P08 | Deterministic lens scheduling, honest audit currency and closeout order | P02, P03, P06, P07 |
| P09 | Cross-platform patch qualification and one reusable benchmark | P01–P08, U02, U06 |
| U01 | Immutable historical state fixtures from inspected format contracts | P01 |
| U02 | Released artifact → patch → released artifact compatibility | U01, P01–P03 |
| U03 | External backup, non-destructive repair and fault-injected recovery | U01, U02, P02, P03 |
| U04 | Unique patch identity, full release-diff review and artifact builder | U01–U03, P01–P08 |
| U06 | Conservative release notes and existing-user rerun advisory | U02–U04, P04, P05 |
| U05 | Offline package upgrade and separate installed Claude smoke | U02–U04, U06, P01–P03 |
| U07 | Final immutable-candidate release matrix and evidence bundle | P01–P09, U01–U06 |
| F01 | Disabled-by-default optional protocol, config and CLI | U07 |
| F02 | Stable candidate snapshots preserving original index/worktree | F01, P06, P07 |
| F03 | Immutable run evidence, single-writer ownership and crash recovery | F01, F02, U03 |
| F04 | Real check execution, typed outcomes and evidence predicates | F02, F03, P03, P06–P08 |
| F05 | Plan skill, executable task contract and plan validation | F01, F04 |
| F06 | TDD execution with expected RED, GREEN, regression and refactor | F04, F05 |
| F07 | Orchestrator roles, independent verification and bounded repairs | F03–F06 |
| F08 | Safe integration and conditional legacy lifecycle connection | F02–F07, P08, U02, U03 |
| F09 | Separately packaged and qualified host adapters | F01–F08, U05 |
| F10 | Behavioral reliability evaluation and measured performance | F04–F09, P09, U07 |

U06 intentionally precedes U05: packaged notes must exist before the installed artifact is qualified. U07 writes final measurements to the external evidence bundle, not back into a frozen package. Any subsequent packaged-file edit requires a new candidate and affected requalification. P09 implements the benchmark; U07 consumes it rather than creating another benchmark or rerunning unchanged work merely for another report.

## Assignment and integration sequence

**First implementation batch:** establish P01 passing controls/test infrastructure; prepare new bug assertions with their fixes, retaining observed RED evidence. Runtime implementer owns P02/P03; evaluation implementer owns P04/P05; compatibility implementer owns U01. P03 waits for U01's acceptance fixtures. Do not merge a red required CI job into the default branch simply to demonstrate TDD.

**Second batch:** P06/P07 can proceed against the shared contracts, while U02 exercises parser compatibility. Serialize edits to `skills/project-checkpoint/SKILL.md`, state-format and test helpers through one integrator. U03 then validates recovery; P08 composes corrected lifecycle transitions. P09 and release preparation follow the dependency table.

**Patch release batch:** U04 identifies the candidate and reviews every change since the actual release tag. U06 prepares accurate packaged notes, U05 tests the installed artifact, and U07 makes the final release decision. This stage must not depend on completing any F task.

**Optional feature batch:** F01–F04 establish config, snapshot and evidence fundamentals. F05–F08 add the actual plan/TDD/verification/integration workflow. F09 qualifies host packages, and F10 measures behavior before a wider opt-in rollout. Feature design may be refined in parallel with patch work, but release acceptance follows the U07 boundary.

Each implementation PR names its task IDs and includes targeted RED/GREEN output, relevant suite output, source/fixture identity, independent review and any limitations. Test results are invalidated by changed relevant inputs; routine reporting does not require running unchanged tests twice. No PR closes a behavioral task using only a Markdown wording check.

## Audit coverage and additional concerns

| Evidence or requested capability | Implementation tasks |
|---|---|
| A1 hidden malformed findings; A3 scalar/heading prefix bugs | P01, P02, U01, U02 |
| A2 acknowledgment linkage; malformed badge counts | P03, U01–U03 |
| A4 false arithmetic oracle; A6 contradictory kickoff scoring | P04, P05 |
| A5 missing harness isolation; A7 unblinded model identity | P05, U05, F09 |
| A8 false secret exposures; unsafe blanket staging | P06, U02 |
| A9 stashed-away candidate; A11 live probe closing missing-test gap | P07, F02, F04, F06 |
| A10 impossible debt scheduling | P08 |
| A12 incomplete audit recorded current; late closeout findings | P08, F08 |
| Regressions in prior fixes; archives, tempfile and shell portability | P02, P03, P09, U01, U02 |
| Interrupted upgrades, recovery, downgrade, install/cache identity | U02–U05 |
| Existing-user advisory and truthful reliability/performance claims | U06, U07, F10 |
| Feature planning and actual TDD | F05, F06 |
| Orchestrator duties, independent assessment and finite loops | F03, F07, F08 |
| Codex and assumed Antigravity portability | F09, F10 |

The unidentified “checkitself” comparison remains outside this backlog's evidence claims. It is not needed to implement the confirmed defects. If a specific project is supplied later, compare it as a separate research task; do not delay the compatibility patch.

## Gates that cannot be substituted

| Gate | Required proof | Insufficient substitute |
|---|---|---|
| Parser fix | Real script on failing/control fixtures, both OSes | Grepping for added wording |
| Legacy compatibility | Actual tag and candidate executables, input byte preservation | Changing a fixture's version field |
| Safe recovery | Executed documented operations with injected faults and restored hashes | A test-only reimplementation of the intended algorithm |
| Installed upgrade | Disposable real host, loaded artifact identity, fresh-session result | Replacing directories in a fixture |
| Skill behavior | Correctly isolated live-host scenario with external observations | A generated transcript claiming commands ran |
| TDD | Expected assertion RED, same acceptance test GREEN, regression evidence | Any nonzero command exit or a toy failing test |
| Independent review | Distinct assessment and reproduced outcome | A second role label in the implementer's transcript |
| Performance improvement | Same workload/versioned evidence, latency and correctness together | Faster execution that skipped work |

## Planning validation and handoff

Three delegated agents authored the patch, upgrade/release and optional-workflow plans. Cross-review identified and resolved inconsistent benchmark ownership, release dependency ordering, changing-source snapshot risks and runner recovery/evidence lifecycle gaps. The primary agent reconciles task dependencies, cross-plan contracts and audit coverage; the retained [planning review](planning-review.md) records the checks and remaining implementation-time qualifications.

The first implementation task is **P01**, with U01 and P04 able to begin once the shared harness contract exists. All source changes remain unimplemented. Use this backlog to execute the next patch without reopening already-settled architectural choices, while treating live-host versions, credentials, budget and candidate release identity as facts to verify at implementation time.
