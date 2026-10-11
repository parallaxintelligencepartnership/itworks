# itworks audit and implementation decision

2026-10-11, target `7df722830da8fe3a3872459e06308d2d53f4153b`, initially clean worktree.

Build a small, evidence-driven development workflow around the existing lifecycle skills. First repair deterministic validation and evaluation correctness. Then add task planning, test-first implementation, independent verification, and bounded repair loops. More autonomous agents on top of the current evidence system would multiply false confidence.

This is an audit and implementation recommendation, not a completed product upgrade. This session adds audit artifacts and executable reproductions only. No product files, versions, installed plugins, remote repositories, or production systems were changed.

Planning follow-up: the user clarified that the tool is already released. The [implementation backlog](../../plans/2026-10-11-itworks-hardening/README.md) now separates a compatibility patch and upgrade qualification from the later opt-in workflow. All fixes remain pending; the six regression failures were reproduced again during planning.

## Scope and verification

Three delegated reviewers read the runtime/state/publication files, lifecycle skills/runbooks, and all tests respectively. Together they covered the 75 current tracked files; the five prior audit documents were historical context, with the previous summary read fully and relevant report passages inspected. Git internals, external receiving-site implementation, installed plugin caches and live agent behavior were outside scope. No scoped current source file was skipped. No existing `.itworks/` state was present; this report follows the established `docs/audit/` destination rather than inventing project state.

The primary agent independently reproduced validator failures with fresh temporary projects and ran the stash/ignored-env probes. A separate reviewer verified the testing lane's arithmetic and harness claims. Exact-source traces verify workflow contradictions; those establish instruction defects, not that a live agent necessarily follows the harmful path. Reviewers did not edit product files. Paid model sessions and GNU/Linux testing were not performed.

Evidence files:

- [Runtime review](runtime-review.md)
- [Workflow review](workflow-review.md)
- [Testing review](testing-review.md)
- [Independent testing verification](testing-verification.md)
- [Executable audit regressions](reproduce.py) and [actual output](regression-output.txt)
- [Retained probe artifacts](evidence/sha256.json), including the executed Go reproduction and mocked harness results; `/tmp` paths in reviewer reports identify original scratch locations.

Run `python3 docs/audit/2026-10-11/reproduce.py` from the repository. At the target revision: **9 checks, 3 pass, 6 fail, exit 1**. The failures deliberately assert correct behavior against known defects; this is retained RED evidence, not a green regression suite. Five failures exercise the real validator; one recomputes the fixture's overtime buckets and compares its recorded output. Shell syntax checks passed for all three shell scripts. This does not establish model adherence or production readiness.

## Confirmed findings

All consolidated findings below are IMPORTANT: they compromise the tool's promised validation or evidence. No live credential disclosure, deployment bypass or production incident was demonstrated; those should not be presented as confirmed CRITICAL exploits.

| ID | Location | Reproduction and consequence | Required correction |
|---|---|---|---|
| A1 | `scripts/itworks-lint.sh:85-100,118-122` | With SHIPPED present, canonical open CRITICAL exits 1; the identical finding with two leading spaces or `*` bullet exits 0 with zero warnings. Publishing has the same anchored blind spot. | Detect malformed finding candidates; one shared parser for lint, gates and counts. |
| A2 | `scripts/itworks-lint.sh:103-105` | Accepted CRITICAL plus an empty Accepted risks heading exits 0 with zero warnings. No individual acknowledgment is required by code. | Stable finding IDs and matching nonempty acceptance records. A stored quote still needs trustworthy origin; syntax alone cannot establish consent. |
| A3 | `scripts/itworks-lint.sh:28-31,140-141` | `profile: expert-invalid` and `## Database` instead of `## Data` both validate. | Complete scalar parsing and exact heading boundaries, with valid inline-comment compatibility. |
| A4 | `tests/pressure/harness/cases/case-7/fixture.md:288-305` | Every supplied shift begins in ISO week 36. Executed Go yields 40 regular/8 overtime, while the fixture asserts 40/0 plus 8/0 in week 37. The rubric requires reproducing this false failure. | Executable fixture inputs and generated oracle; reward rejecting incorrect evidence. |
| A5 | `tests/pressure/harness/run-case.sh:135-169` | Mocked CLI records caller cwd and only `-p`/`--model`; skills are supplied as paths, not contents. No harness-enforced isolation supports its no-tools/no-writes claims. | Separate text simulation from isolated real-tool integration tests. Load actual instructions explicitly in each mode. |
| A6 | `tests/pressure/harness/cases/case-1/pass-conditions.md:16-21` | Rubric requires six answered questions; fixed user script never supplies them, while another check requires holding the unconfirmed gate. Case 2 has a related ambiguity and requires obsolete format v2. | Distinguish correct blocked progress from completed interview; fix current-version oracle. |
| A7 | `tests/pressure/harness/run-case.sh:203` | Transcript contains producing model ID although README requires blind judging. Independently observed in mocked output. | Keep raw manifest separate; sanitized judge artifacts without model names in content or filenames. |
| A8 | `references/lens-security-auth.md:23-45` | Exact scan flags a synthetic key in ignored server `.env`; text declares every match CRITICAL. Tracked `.env.example` also matches the filename rule regardless of content. | Classify exposure using tracked/served/history context; inspect templates and redact evidence. Keep scanning real public leaks. |
| A9 | `references/lens-testing.md:25-27` | On dirty code, permitted `git stash push` removes the candidate feature. Mutation/restore can go red/green on the old commit and leave new work stashed. | Test an isolated snapshot of the actual candidate, including relevant untracked content; preserve original index/worktree. |
| A10 | `skills/project-checkpoint/SKILL.md:36,63` | Three consecutive auth+LLM checkpoints leave three other lenses at debt 3. Next checkpoint must include all three but is capped at two. | Explicit scheduling policy and tests for overflow and nonapplicable lenses. |
| A11 | `references/lens-testing.md:39-41` | A missing-test finding can satisfy generic closure evidence via a successful live probe while still having no test. | Evidence requirements by finding type; live behavior cannot substitute for an executable regression test. |
| A12 | `skills/project-audit/SKILL.md:79-84`; `skills/project-resume/SKILL.md:40` | Audit records skipped lanes then unconditionally advances `last_audit`; resume's date/history-only calculation reports current. | Separate attempted from completed audits; incomplete in-scope coverage does not advance completion. |

A1-A3 were independently executed; A4-A5/A7 independently executed by another reviewer; A6/A10-A12 independently traced by the primary agent; A8-A9 independently probed by the primary agent. The raw reviewer reports include additional candidates. Those are not silently included in this consolidated count.

Additional actionable concerns: checkpoint's instruction to “commit everything” explicitly allows open findings and can commit discovered secrets or unrelated user work; new closeout findings occur after its main reckoning; Rust/PHP lockfile checks disagree across runbooks. Treat these as workflow correction tasks with focused integration tests. The closeout hard gate still forbids unacknowledged critical shipment, so the ordering problem is not proof that the gate authorizes it.

## Earlier claims rechecked and limits

The prior missing-final-newline and missing-severity validator bugs are fixed. Current publishing includes archived findings and accepted critical counts; do not repeat the old green-badge diagnosis. Hook timeout and model warning exist. These controls do not remove the newly demonstrated parser gaps.

The current testing lens is post-implementation review. Kickoff proves a toy failing test can run; neither establishes feature-level TDD. There is no per-change plan/execution protocol. Those are missing capabilities relative to the requested direction, not regressions against a preexisting TDD promise.

Historical model pass/fail claims lack a reproducible artifact manifest here. The harness has invalid oracles and does not test genuine plugin activation. Its results cannot support a universal “only Opus can review” rule or prove Codex/Antigravity suitability. No new behavioral pass rate, reliability gain or model performance gain was measured in this audit.

The runtime reviewer measured one local lint run at each size: 10 findings 0.078s, 100 findings 0.383s, 800 findings 2.692s. This is diagnostic evidence of per-line subprocess overhead, not a robust benchmark or demonstrated improvement. Repeated median/p95 measurements on fixed fixtures must precede optimization claims.

## Implementation choice

The observed workload is a small local plugin, with three shell scripts and human-readable instructions/state; no throughput requirement justifies a hosted orchestrator service.

| Approach | Effort and operations | Where it wins | Limitation |
|---|---|---|---|
| Prompt-only revisions | Lowest, no new runtime | Clarifying triggers and resolving wording contradictions | Cannot reliably enforce evidence validity or transitions |
| Local deterministic runner plus thin skills | Moderate, one small executable and fixture suite | Reproducible checks, portable evidence, bounded local workflow | Must test installation and interpreter availability |
| Hosted multi-agent orchestration service | Highest, persistent jobs/secrets/operations | Future shared remote workers and durable cross-machine scheduling | Unjustified complexity for today's plugin |

**Choose the local runner.** Start with Python standard library for parser, subprocess handling and JSON evidence, keeping the shell entry point compatible; explicitly check/document Python availability. Existing Markdown remains readable. One parser interprets legacy state, and a small versioned JSON run record stores execution evidence; avoid maintaining two writable copies of the same findings. Consider a service only after demonstrated remote/concurrent demand outgrows a local process.

## Ordered implementation waves

1. **Make existing claims testable.** Add deterministic regression tests for parser, hook branches and runner behavior; fix A1-A7. Include malformed state, acceptance linkage, empty output, command failure, missing files, collision-free artifacts, path spaces and Linux/macOS behavior. Correct fixture oracles before any model rerun. Add CI invoking the same local test command. Completion: targeted RED becomes GREEN, controls remain green, reverting each fix reproduces its failure.

2. **Protect the user's work and evidence.** Fix A8-A12, task-only staging and closeout ordering. Add a candidate snapshot identifier covering commit plus dirty/index/untracked state relevant to the task. Store check ID, applicability, command/argv, cwd, snapshot identity, exit code, timestamps, result, redacted artifact path/hash and environment identity. Results are PASS, FAIL, BLOCKED or NOT_APPLICABLE with a reason. Distinguish expired evidence from failed behavior. Completion: stale evidence, changed files, missing test artifacts, incomplete audits and unrelated acceptance cannot advance a gate; original working state survives failed/interrupted checks.

3. **Add planning and TDD execution.** Introduce one planning skill and one implementation skill. Each nontrivial change gets purpose, non-goals, inspected file paths, acceptance examples, dependencies, risks, ordered tasks, first failing test and exact validation commands. Review the plan for missing requirements and impossible tests before execution. Each behavior change records expected RED, minimal implementation, GREEN, then refactor and regression results. Diagnose unexpected failure before coding. No empty test ceremony for prose-only changes. Completion: executable sample tasks demonstrate correct feature behavior and caught seeded defects, including interruption/resume and spec-change scenarios.

4. **Add bounded orchestration.** The main agent owns requirements, task graph, budgets, permissions, dispatch, integration and user communication. Implementers own small scoped patches and tests. Independent verifiers own reproduction and acceptance checks. A local runner evaluates deterministic transitions; it cannot prove semantic correctness or prevent an owner manually bypassing it. Sequential execution is the default; delegate independent work when it earns its latency/cost. One integrator owns shared state writes. Completion: tested stop/resume, concurrency conflicts, failing verification, missing capabilities, changed requirements and budget exhaustion all produce honest state.

5. **Qualify host adapters and measure outcomes.** Keep rules/checks/evidence host-neutral. Claude, Codex and Antigravity adapters own installation, discovery, model dispatch, tool permissions and event integration only. Run the same contract and behavioral cases per exact host/model/configuration. Release support only for measured combinations. Track task success, seeded-defect detection, false blocks, incomplete runs, regression escape, p50/p95 elapsed time and tokens/cost per accepted task. Report trial counts and uncertainty. A faster run that skips verification is a failure, not an optimization.

Start with waves 1-2 as the first release-sized change. They establish the foundation required for meaningful TDD and loops. Do not bundle a universal agent framework into that patch.

## Orchestrator contract and loops

Every delegated task receives a pinned candidate, bounded file scope, acceptance tests, allowed actions, relevant context, required evidence and stop condition. The implementer cannot silently weaken its acceptance tests; changes to the specification return to the orchestrator and invalidate affected evidence. Verification independence means a separate assessment of the candidate, not a second agent repeating the implementer's prose. Use another model/vendor only when measured benefit justifies it. If delegation is unavailable, disclose reduced independence.

The workflow is `inspect → plan → test RED → implement → test GREEN → independent verify → integrate → revalidate affected checks → complete`. Distinct rejection paths matter:

- A failed assertion returns its concrete counterexample to the implementing task.
- A reviewer suspicion must be reproduced before it becomes a repair request.
- A flaky or broken harness returns an infrastructure error, never a product PASS or fabricated defect.
- A requirement change returns to planning; a changed candidate invalidates related evidence.
- A newly discovered release finding returns to verification and then reckoning.

Initial policy: at most two autonomous repair attempts per rejected task, with a configurable run-wide time/token budget. Stop earlier when the same failure repeats without new evidence. Preserve every failure and attempt; do not rerun until a lucky green erases a flaky result. Budget exhaustion records incomplete/blocked work and the specific next action. It cannot become success or justify inventing evidence. This default is an operating choice to evaluate, not a universal optimal retry count.

Performance work follows quality measurement: single-pass state parsing; load only task-relevant references; reuse checks only for identical relevant inputs/environment and explicit freshness; avoid duplicate history scans on unchanged snapshots. Network/security checks need their own expiration. Parallelize nonoverlapping work with bounded concurrency, then verify the integrated candidate.

## Superpowers and host guidance

Superpowers already supplies useful patterns: a behavior test must demonstrably fail for the intended reason before implementation, followed by minimal code and a green suite; plans identify files, interfaces and tests for small tasks. Adopt those concrete contracts rather than copying every rule or equating a written plan with proof. See [Superpowers TDD](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md) and [planning](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md). These are comparisons, not a full audit of Superpowers.

For Codex, use discoverable skills under `.agents/skills`, optional `agents/openai.yaml` metadata and concise repository `AGENTS.md` guidance; respect scoped overrides. Keep Claude's `model: opus`, slash-command assumptions and `CLAUDE_PLUGIN_ROOT` in its adapter. Current documentation establishes discovery/configuration, not that this plugin already works on Codex. Sources: [OpenAI skills](https://learn.chatgpt.com/docs/build-skills), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Assuming “Agy” means Google Antigravity, target its current Agent Skills surface. Google documents `.agents/skills` and backwards compatibility with `.agent/skills`; its workflows page points toward migration to skills. Avoid starting a separate legacy workflow implementation. Verify the specific CLI/IDE surface through installation and invocation tests before claiming support. Sources: [Antigravity skills](https://antigravity.google/docs/skills), [workflows](https://www.antigravity.google/docs/ide/workflows/).

“checkitself” was not identified unambiguously. Its comparison remains open pending an exact project link/name. No claims about its implementation informed these findings.
