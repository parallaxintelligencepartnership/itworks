# Workflow audit — reviewer report

Target: `7df722830da8fe3a3872459e06308d2d53f4153b`. Read-only repository audit. Findings below are reviewer suspicions supported by executions or exact specification traces, pending an independent verifier; they are not evidence of a model actually following every harmful instruction in a live session.

## Coverage

Read in full: all five `skills/*/SKILL.md`; `references/audit-method.md`, `dependency-vetting.md`, `glossary.md`, `injection-patterns.grep`, `secret-patterns.grep`, all five `lens-*.md`; `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `.gitignore`, `LICENSE`. No scoped files skipped. Read `references/state-format.md` in full as a dependency. `references/publish.md` excluded by lane allocation and not needed for these findings. Prior audit: read `docs/audit/2026-09-16/AUDIT.md` fully and relevant keyword-matched passages in the old lane reports. Did not rerun pressure scenarios or inspect tests broadly (assigned elsewhere). No network or production probes. Scratch executions under `/tmp/itworks-workflow-probes-677l3cm5/fixture` only; no repository changes.

Previous fixed findings (relative reference paths, injection plus pattern, missing whole-tree scan, omitted llm lens, absent adoption structure pass, stale PROJECT correction path, missing model caveat) were checked against current files and are not re-reported unchanged. Some new findings are regressions/overbreadth introduced by those fixes.

## W1 — IMPORTANT: recommended secret storage is classified as a critical leak, and clean env templates also block

Locations: `skills/project-kickoff/SKILL.md:62`, `references/glossary.md:146-148`, `references/lens-security-auth.md:23-29,39-45`.

Trigger: follow kickoff exactly: put a server-only credential in ignored `.env`, keep `.env.example` containing names/placeholders tracked for setup. The security lens recursively scans ignored `.env` and says **any** match is CRITICAL; its tracked-file expression also matches `.env.example` unconditionally.

Executed scratch fixture, with synthetic fake key only:

- `.gitignore` is `.env`; `.env` contains `API_KEY=sk-synthetic_audit_fixture_123456789`.
- `git check-ignore .env` -> `.env` (exit 0).
- Exact step 1b grep -> `./.env:1:API_KEY=sk-synthetic_audit_fixture_123456789` (exit 0).
- Track `.env.example` containing only `API_KEY=replace_me`.
- Exact step 3 `git ls-files | grep -E "(^|/)\\.env|\\.pem$|credentials"` -> `.env.example` (exit 0; shell's effective regex is `(^|/)\.env|\.pem$|credentials`).

Wrong outcome: compliant private server configuration becomes a CRITICAL that blocks features/ship, and sanitised onboarding templates produce the same result. This is not an argument to stop scanning ignored files: classify tracked/served/historical exposures separately from intentional private configuration, and inspect template contents before asserting exposure. Redact matched values from retained evidence.

Regression tests: ignored server env should not be an exposure; same token in public bundle/unignored note/history must be detected; empty tracked env example passes, env example with real-shaped secret fails.

## W2 — IMPORTANT: mutation proof can test the previous commit and leave the requested feature stashed

Location: `references/lens-testing.md:25-27`, invoked by `skills/project-checkpoint/SKILL.md:42`.

Exact path: dirty worktree -> `git stash push` is explicitly offered -> break a source comparison -> run suite -> `git checkout -- <file>` -> run suite green -> require status clean. No stash apply/pop or return to the checkpoint's actual feature snapshot is specified.

Executed fixture: commit `compute(1)==2` plus a test asserting 2; dirty change changes both implementation/test to 3. `git stash push` succeeds. Mutation return -1 produces red **against assertion 2**. Checkout restores base implementation. Green output is `base assertion ran`; status is clean; `stash@{0}` still contains the new feature and final source is `return x+1`. All explicit success criteria in lines 25-27 hold while the current feature is absent and unverified.

Fix: capture exact candidate state including tracked/untracked changes into an isolated disposable copy/worktree; mutate only there. Verify expected targeted assertion failure and rerun green against that identical candidate state. Assert user's original worktree/index/untracked content unchanged. At minimum, define stash restoration and do not permit a test of the pre-feature base to count.

## W3 — IMPORTANT: checkpoint explicitly commits a discovered untracked secret, expanding exposure into history

Location: `skills/project-checkpoint/SKILL.md:69`; related `references/lens-security-auth.md:23-37`.

Trigger: add untracked `notes.txt` with a credential during development. Security lens reports it CRITICAL. Step 6 says “Commit everything (code plus .itworks/)” and “Open findings never block this commit.” Therefore the normal prescribed restore-point path includes the key in git even when the scan just identified it. This worsens a private uncommitted exposure into permanent history before resolution, contrary to the security lens's own history warning.

Executed scratch analogue: untracked notes with the synthetic key -> `git add -A`, commit -> `git ls-files notes.txt` returns notes.txt. This validates the consequence of the literal instruction, not an actual live assistant failure.

Fix: stage only intended task files, inspect staged diff, never stage credential material simply because a finding is documented. Keep review state/code restore point separate from sensitive/unrelated files. Make secret exclusion a precondition even with accepted findings; safe candidate snapshot can retain excluded paths locally outside the repository when appropriate. Regression: discovered untracked secret remains untracked after checkpoint; intended feature and review notes commit; unrelated user work remains untouched.

## W4 — IMPORTANT: incomplete audit can be recorded as current without machine-readable completeness

Locations: `skills/project-audit/SKILL.md:16,57,79-84`; `skills/project-resume/SKILL.md:34,40`; `references/state-format.md:158-160`.

Exact trace: lane P read and verified, lane Q skipped (e.g. unavailable service or context/tool budget) -> Step 5 requires recording skipped lanes/coverage gaps -> unconditionally set `last_audit: today @sha` -> resume computes current/due solely from date, SHIPPED presence and ship-history distance -> current even though Q was never read. The audit hard gate says an audit listing unread lanes “is not an audit”; the timestamp write does not carry that distinction. A candid report helps a human who opens it, but the next session's compact current marker and due logic lose the limitation.

Fix: write last attempted audit separately from last completed audit; completeness should distinguish intentional excluded external/live probes from unread in-scope files/lanes. Only a completed declared code scope advances last completed audit. Regression fixture: skipped lane remains due; all declared lanes read with explicitly unavailable hardware probe can have correctly scoped completion, not fabricated hardware coverage.

## W5 — IMPORTANT: closeout's new checks happen after its only mandatory reckoning

Locations: `skills/project-closeout/SKILL.md:30-44,50-60,62-82`.

Trace: Step 1/2 sweep is recorded and Step 3 resolves every current finding. Step 4 then rechecks PROJECT facts before only-if skips, probes routes, and *creates a new IMPORTANT audit-currency finding* (line 60 says it goes through reckoning). A stale sample-only PROJECT causes backup check to have been skipped in Step 1; Step 4 discovers real records, updates state, and orders rerunning lenses. New findings arise after the one defined reckoning traversal. The prose says these must go through reckoning, so a careful agent can infer a loop; the linear workflow does not define one and Step 5 immediately follows.

Assessment: verified ordering/incomplete control-flow defect, not proof a compliant agent may ship with unacknowledged CRITICAL (the top-level hard gate still prohibits that). It invites missed or repetitive handling and makes deterministic orchestration difficult.

Fix: verify applicability facts first; collect all sweep, checklist and audit-currency results before a single reckoning, then revalidate no newly open CRITICAL before writing SHIPPED. Regression: PROJECT says sample, actual real store and no backup; finding appears before reckoning and blocks unless individually accepted.

## W6 — IMPORTANT: mandatory debt inclusion becomes unsatisfiable under ordinary checkpoint history

Locations: `skills/project-checkpoint/SKILL.md:36,63`; `references/state-format.md:161-169`.

Exact values, all lenses applicable: start debts `(security,llm,real,testing,production)=(0,0,0,0,0)`. Three checkpoints touching auth + LLM select security/llm each time, leaving `(0,0,3,3,3)`. Fourth checkpoint must force-include **any** lens >=3, i.e. real/testing/production (3 lenses), but cap is 2. Conflict clause only handles replacing a “lower-priority contextual one”; all three are mandatory, so that rule cannot settle it. Priority list could be inferred as dropping production, but that violates force-inclusion and allows debt >3 without any explicit overdue policy.

Fix: explicit deterministic oldest-debt-first top-two selection (tie break documented), or a bounded overflow exception for multiple overdue lenses. State whether debt is a max promise or prioritisation. Nonapplicable lens debt should stay zero (state-format says this for llm, generic Step 5 increment contradicts it). Table-driven traces should cover >=3 overdue lenses and nonapplicable llm.

## W7 — IMPORTANT: evidence-to-close permits a live probe to close a missing-test finding without adding a test

Location: `references/lens-testing.md:23,35-41`; `skills/project-closeout/SKILL.md:34`.

Exact trace: `IMPORTANT | testing | no failure-path test for login` -> live wrong-password request returns expected 401 -> testing evidence-to-close explicitly accepts “Test run output ... **or the live probe transcript** matching expectations table” -> reckoning Fixed requires runbook evidence-to-close, therefore allows checking the finding while test absence remains. Both options are appropriate evidence for different defect types, but no per-finding mapping prevents this substitution. Similarly a live probe cannot close “no runnable suite at closeout.”

Fix: map evidence requirements to finding type: absent/broken/decorative tests require executable test evidence; live behavior mismatch requires live probe (plus regression test where meaningful). Regression: a correct live rejection with no executable test must leave missing-test finding open.

## W8 — ADVISORY: production dependency command disagrees with dependency-vetting for Rust/PHP

Locations: `references/lens-production-readiness.md:28-32` vs `references/dependency-vetting.md:21-25`.

Trace: Rust project tracks Cargo.lock, no npm/Go/Python/Ruby lock. Dependency-vetting includes Cargo.lock and passes. Production readiness's exact tracked lockfile grep omits Cargo.lock and composer.lock, finds none, and declares absent committed lock IMPORTANT. These runbooks run together in closeout. Fix shared ecosystem-aware lockfile detector; verify Cargo.lock/composer.lock fixtures and no-dependency projects. Avoid treating go.sum as a complete lockfile or exact direct versions as a substitute for locked installs; those are separate ecosystem concepts requiring implementation-specific checks.

## Planning and TDD — enhancements, not falsely labelled regressions

The current implementation is a lifecycle review layer, not a planning/execution/TDD engine. Evidence:

- `skills/project-kickoff/SKILL.md:39-46` defines success proof and failure behavior per feature; useful specification seed.
- Kickoff `:66` proves harness responsiveness with one deliberate failure. This proves runner wiring, not test-first development of product behavior.
- Testing lens `:13-31` runs after the feature is complete; mutation demonstrates one assertion can notice one change. It does not require a feature test before implementation, intended red reason, smallest passing implementation, or safe refactor cycle.
- Audit `:88` / audit-method `:71,81` requires regression tests failing when fix reverted; this is a valuable foundation, not general TDD enforcement.
- No skill owns a per-change plan, task dependencies, plan validation against inspected files, progress/evidence updates, or resumption from a plan. `DECISIONS.md` is a decision journal and PROJECT verification table is product intent, not an execution plan.

Recommended small additive contract: before nontrivial behavior change, inspect relevant code/tests, record task intent/non-goals, changed files, acceptance examples, first failing test, ordered small steps, validation commands and unresolved assumptions. For each meaningful behavior, retain targeted red output with expected failure reason, then green output at candidate commit, then relevant regression suite. Refactor only from green. For existing bug, reproduce first. Permit documented exceptions for prose/static assets/generated code instead of meaningless tests. Prefer extension of existing runner and small shell/Python records over new services.

Model-neutral implementation: keep state schemas, executable check commands, severity/evidence mapping and test protocol vendor-neutral. Adapter files should contain Claude frontmatter/hooks/slash commands and host-specific dispatch only. Codex/Agy should each declare real available capabilities (shell, permissions, browser, isolated workspace, delegation, model identity) and return not-run/unsupported with exact impact when unavailable. Do not infer equivalence from a model brand or “class”; qualify adapters with versioned behavioral scenarios and report observed pass rates with sample sizes. `skills/project-closeout/SKILL.md:15` currently prevents honest completion on non-Opus models by construction; README `:47,116` turns limited empirical model tests into a universal review recommendation. This is a portability limitation/design choice, not evidence any other model works or fails. Verify “Agy” product identity with user before publishing support instructions.

## Efficiency and assurance improvements

- Closeout security Step 1 already runs full history; closeout Step 2 repeats history checks (`skills/project-closeout/SKILL.md:20,28`, security `:31-45`). Reuse same-target evidence once with an explicit shared check ID; don't silently skip required checks.
- Dependency pins/lockfiles are checked twice by production lens and dependency-vetting. Consolidate detector and results, leaving lens-specific classification.
- Mutation step runs suite red/green every selected testing checkpoint; tie to changed critical behaviors and use targeted mutation test plus one full green suite, not arbitrary mutation and repeated full suites.
- For full manifest vetting, use a small evidence record keyed by exact package/version and lockfile digest; expire registry/security information deliberately. Current unconditional full sweep is intentional because no such state exists, so caching before adding freshness/invalidation would reintroduce prior audit defect.
- Grep output capped at first 20/30 hits should be display-limited, not evidence-limited. `lens-real-data.md:16`, `lens-llm-security.md:16` discard remaining hits; save complete result and summarize count. Neither grep absence nor a single mutation gives exhaustive assurance.
- Tighten glossary absolutes: database `:60-61` says file storage cannot be real persistence, localhost `:246` describes reachability as guaranteed, coverage `:215` says untested 30% is always where bug is. These are pedagogical overclaims, not reliable invariants. Reword as conditions without turning this into an encyclopaedia.

No claim of measured application/model performance improvement is made by this audit. Benchmark actual hook/lint latency, scenario success rates, review latency/token cost, and false-positive/false-negative fixture rates before and after a fix wave.

## Orchestration recommendation

Make the main agent the accountable orchestrator, backed by a small deterministic protocol, not another unbounded model supervising models. Its duties are: resolve user intent/scope; inspect and select applicable checks; pin the candidate snapshot; create a small plan with acceptance tests; dispatch bounded read-only lanes when parallel work is justified; collect structured results; route suspicions to an independent verifier; deduplicate findings; apply ordered fixes with red/green evidence; run regression/review; persist exact state; report completion and remaining limitations. The orchestrator must preserve user work, approval boundaries and direct user corrections across every stage.

Each delegated task needs an explicit target revision, file scope, inputs, allowed actions, required evidence, output schema and stop condition. A result has passed / failed / not-run / not-applicable status, plus command, exit code, target hash, assertion or trace, and reason. Text saying “done” alone never advances a gate. Reject incomplete/contradictory results instead of turning absence into green. Independent review need not mean a different vendor, and lack of delegation should produce a declared lower-independence review rather than fabricated independence.

Make loops finite and event-driven: a failed test returns to its owning fix task; changed candidate hash invalidates affected evidence; newly discovered finding returns to verification then reckoning; changed requirements update the plan before more code. After repeated identical failures or no new evidence, stop the loop, preserve the attempted commands/outcomes and explain the specific blocked dependency. Hard-code neither endless retries nor a universal attempt count without considering task cost; configure modest bounds and expose exhaustion honestly.

Start with one small local check runner/evidence manifest plus existing Markdown state, not a server, queue or database. First automate deterministic checks that can demonstrably catch failures; retain agent judgment for planning, relevance and adversarial review. User acceptance of a risk updates that risk only; it must not manufacture passing evidence or approve unrelated findings. This separation gives TDD, audit, closeout and future adapters one auditable handoff protocol instead of more overlapping prose.
