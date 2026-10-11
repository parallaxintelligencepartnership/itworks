# Implementation boundaries and shared contracts

Status: planned, no implementation started. These decisions apply to the task plans in this directory. Where a task needs a changed contract, update this file and the affected tests before implementation continues; do not silently let two agents implement different interfaces.

## Released baseline and scope

- The local published tag `v1.0.0` resolves to `0b972ac8232825d82f16023f54d3ccbeda443813`.
- Audited branch HEAD is `7df722830da8fe3a3872459e06308d2d53f4153b`. Its plugin manifest still says `1.0.0`; the changelog calls subsequent changes Unreleased. Neither equal version text nor a successful source checkout proves which content a user installed.
- Upgrade qualification covers the tag and the audited branch separately. Release review covers the entire tag-to-candidate diff, including earlier unreleased fixes, not only edits made for these plans.
- All tasks below are future work. This planning session must not change runtime code, install plugins, change tags or versions, publish releases, open external issues or run paid model evaluations.

## Patch versus opt-in feature increment

| Property | Compatibility patch | Later opt-in workflow |
|---|---|---|
| User entry points | Preserve current five skills/commands and `bash scripts/itworks-lint.sh [root]` | Add explicit planning/execution commands; existing lifecycle continues when disabled |
| Runtime prerequisites | Existing Bash and standard Unix tools; no new mandatory Python | Python standard library, declared minimum/version preflight; absence blocks optional feature only |
| State authority | Existing `.itworks/` Markdown and SHIPPED remain authoritative | Same intent/findings/acceptance authority; separate config and generated execution evidence |
| Format versions | Read v1/v2/v3, preserve legitimate legacy drift | No forced legacy migration or new mandatory finding IDs |
| Autonomy | Correct existing behavior | Explicit enablement and bounded execution under host permissions |
| Completion claim | Tested patch scope and known limits | Per-host/model qualification, exact scope and retained evidence |

The prior audit recommended a Python core. Applying that as a mandatory patch prerequisite would break installations that currently need only shell tools. Therefore the patch uses a small shared shell/awk parser; the optional runner may consume its output later. Do not implement a second, divergent Markdown parser in Python.

## State preservation and acceptance

1. Validation and counting are read-only. A missing optional legacy field does not authorize rewriting all state or rerunning kickoff.
2. Malformed open findings must be detected, not omitted. Preserve their severity and original words in diagnostics/recovery; diagnostics redact values that look like credentials.
3. A structurally empty acceptance record is invalid. A historical record with genuine quoted words but ambiguous linkage requires review before it can authorize shipment; it must not be silently matched to whichever finding happens to be next.
4. Missing legacy `Revisit when:` is drift, not fabricated consent or proof that no acceptance exists. Preserve the quote; ask for the missing condition only when the applicable existing workflow reaches that risk.
5. Strict gate outcomes and ordinary lint drift need separate representations. In particular, historical ambiguity should not force a destructive whole-state rebuild. The patch parser task defines the exact exit codes and records.
6. A validator cannot prove a quote was spoken by the user. New execution evidence records origin where the host exposes it, and explicitly labels manual imports; no local file format is a cryptographic proof of user approval.
7. A previously written SHIPPED file is historical evidence, not permanent eligibility for another release. Never erase ship history to satisfy a validator. New findings block the next eligible transition according to severity and recorded acceptance.

## Test and evidence rules

The shared planned deterministic commands are:

```sh
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
```

These directories and suites are task deliverables; the commands do not exist as working suites yet. Python here is a development/CI dependency, not a patch runtime requirement. Each task names its targeted test module and its expected RED reason before implementation. A missing executable, syntax error or import error is not the intended RED.

- Unit/contract tests exercise real parsers and shell entry points on synthetic data. Mock host CLIs only at the subprocess boundary; assert observable cwd, argv, filesystem effects, return codes and evidence.
- Integration tests materialize temporary repositories, preserve tracked/staged/untracked distinctions and test interruption. They never point at real project data or production services.
- Behavioral evals require separate positive-progress and held-gate cases, a corrected executable oracle, isolated settings/workspace, and an independent judge where semantic judgment is necessary.
- Synthetic fixtures, mocks and static instruction tests cannot prove a live model obeyed a skill. Release evidence distinguishes them explicitly.
- Keep the October audit reproducer and recorded failing output as historical evidence. Promote its behaviors into maintained tests; fix the oracle fixture and its executable generator together. Do not rewrite the historical report to suggest its original failures passed.
- In each task's implementation PR, retain the targeted RED result, GREEN result, relevant suite result and tested revision. Reverting the fix in a disposable copy must make its regression fail for the intended reason.
- One command finishing is not a behavioral PASS. Test infrastructure errors, timeouts, unsupported hosts, missing outputs and budget exhaustion must remain distinguishable from product assertion failures.

## Candidate isolation and recovery

No task may stash, checkout, reset, blindly stage or clean the user's working tree merely to obtain a convenient test baseline. Candidate tests must include the work being assessed, including relevant untracked files, and must retain the distinction between HEAD, index and worktree. Mutation tests and rollback rehearsals run in disposable copies.

A copy/worktree is not an OS security sandbox. Tests that can execute untrusted project commands use an explicitly limited environment and host-supported isolation; lack of a required capability is a blocked test, not permission to run against live credentials. Ordinary project checks remain governed by the user's authorized scope and host permissions.

Before any state-writing upgrade or explicit repair, take an independent snapshot outside both source and destination, with paths, modes and byte hashes. Restoration must be tested into a separate location before it overwrites anything. Retain recovery evidence through the release's documented rollback window. If source state changed after backup, do not overwrite newer notes with that older backup; preserve both and stop for reconciliation.

## Delegation and completion

The orchestrator owns acceptance criteria, task dependencies, budgets, permissions and integration. Delegates receive a bounded scope, target identity, allowed actions, required evidence and stop conditions. One integrator writes shared state. Concurrent edits to the same file are serialized unless an explicit merge task owns their reconciliation.

An independent verifier assesses the resulting candidate and can reject the implementer's interpretation. It does not count as independent merely because it repeats a success summary. Sequential fallback is allowed where delegation is unavailable, but the result states reduced independence.

The later workflow starts disabled. Initial repair policy is two repair attempts after the original implementation, one bounded retry for a classified transport failure, a wall-clock deadline, and explicit capability reporting for token/cost limits. No-progress stops sooner. Do not invent unavailable usage metrics or claim a hard token cap when the host cannot enforce one. No repeated rerun may erase a prior flaky failure.

Permission to plan these changes does not itself publish or deploy them. Implementation can prepare a concrete release candidate and evidence; external publication follows the user's then-current authorization and platform permissions. Do not add repeated approvals for already-authorized reversible implementation work.

## How success will be measured

Patch release: regression failures fixed, legacy roundtrips preserved, no unwanted worktree changes, safe rollback demonstrated, corrected host smoke/evaluation records, explicit installed-content identity.

Feature increment: accepted tasks satisfy behavior tests, seeded defects are detected, correct work is not falsely blocked, interrupted runs resume honestly, and supported adapters pass the same contract. Report counts and denominators alongside p50/p95 latency and cost per accepted task. Faster results achieved by omitting checks fail qualification.

Do not promise support for an untested host, infer reviewer fitness from a model brand, or substitute an expected score for observed evidence. “Agy” is treated as Antigravity for planning only; exact product/surface identity must be resolved before shipping that adapter. The unidentified “checkitself” comparison does not block the concrete audit fixes.
