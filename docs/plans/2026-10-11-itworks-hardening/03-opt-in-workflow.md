# Future opt-in workflow — implementation tasks F01–F10

Planning artifact only. None of these features is implemented by writing this document. This lane follows the compatibility patch P01–P09 and its U-series qualification gates. It does not change the installed plugin, the current `1.0.0` version, project state, or release identity. Future release numbering follows the owner's recorded decision; completing the patch does not silently authorize a minor/major release.

## Scope and choice

The inspected application is five Markdown skills, five command wrappers, shell hooks/linter and a Claude-specific pressure harness. `commands/checkpoint.md` delegates to a skill; there is no scheduler, execution-plan engine or evidence runner. `tests/pressure/harness/run-case.sh` currently models conversation and emits transcripts; it is not a real-tool execution backend. Existing `.itworks/PROJECT.md`, `DECISIONS.md`, `REVIEWS.md`, `PROFILE.md` and `MAP.md` remain authoritative for intent, decisions, findings and project facts. Do not replace them with a second findings database.

Assumed operating scale: one local project owner, one active modifying workflow per project, small on-disk evidence, optional bounded read-only reviewers. No multiuser daemon, hosted service, queue, database or arbitrary parallel writers is justified. A failure must leave user files intact and an honest resumable/incomplete record.

| Candidate | Effort and operations | Failure scope | Fit |
|---|---|---|---|
| Extend Markdown and existing shell only | Lowest effort; no new runtime | Model may skip instructions or invent completion | Appropriate for P-series compatibility patch, insufficient alone for enforced evidence transitions |
| Opt-in local Python standard-library runner plus skills | Moderate implementation; Python 3.10+ only for users who enable it | One local run; recoverable immutable evidence and isolated candidate | Selected for executable check receipts, bounded loops and safe integration |
| External workflow/CI service | Highest setup, credentials and ongoing operations | Remote permissions and availability affect workflow | Consider only if independently requested multiuser/remote scheduling needs exceed local runner |

The selected runner coordinates local evidence; the host agent remains responsible for judgment and user interaction. It never claims a prose rule is a hard platform interceptor. Native host permissions still govern every operation.

## Shared future contract

### Files and command line

New implementation files planned:

- `scripts/itworks-run.py`: thin CLI; Python 3.10+ with standard library only.
- `scripts/itworks_core/{__init__,cli,config,snapshot,events,runner,protocol,orchestrator}.py`: ordinary importable modules, split by the responsibilities below, not plugin services.
- `references/workflow-protocol.md`: versioned human-readable schemas, state transitions, evidence predicates and host boundary.
- `skills/project-plan/SKILL.md`, `skills/project-execute/SKILL.md`, `commands/plan.md`, `commands/execute.md`: optional user-facing plan/TDD entry points.
- `adapters/{claude,codex,antigravity}/`: documented host packages/configuration; no automatic installation into the user's global skill directories.
- `tests/unit/test_*.py`, `tests/fixtures/workflow/`, `tests/integration/test_workflow_*.py`: deterministic tests and harmless local execution fixtures.

CLI namespace (do not add a shell wrapper that makes Python mandatory for existing commands):

```text
python3 scripts/itworks-run.py enable --project PATH
python3 scripts/itworks-run.py disable --project PATH
python3 scripts/itworks-run.py status --project PATH [--run RUN_ID] [--json]
python3 scripts/itworks-run.py start --project PATH --plan .itworks/PLAN.md [--budget-seconds 1800] [--supersedes RUN_ID]
python3 scripts/itworks-run.py check --project PATH --run RUN_ID --spec CHECK_SPEC.json
python3 scripts/itworks-run.py request --project PATH --run RUN_ID --role implementer|reviewer|verifier --task TASK_ID --out REQUEST.json
python3 scripts/itworks-run.py ingest --project PATH --run RUN_ID --result RESULT.json
python3 scripts/itworks-run.py resume --project PATH --run RUN_ID
python3 scripts/itworks-run.py abandon --project PATH --run RUN_ID --reason TEXT
python3 scripts/itworks-run.py integrate --project PATH --run RUN_ID --expected-base BASE_SHA --expected-worktree DIGEST
python3 scripts/itworks-run.py finish --project PATH --run RUN_ID
```

`enable` is explicit user activation, not inferred from detecting Python. It writes `.itworks/workflow.json` only after validating the existing project; it does not bootstrap/adopt a missing `.itworks` tree. Missing Python gives an actionable error before mutation. Without a valid enabled config, every new skill and mutating command other than `enable` or idempotent `disable` exits disabled before creating files. `disable` sets enabled false only when an enabled configuration exists; missing or already-disabled configuration is a successful no-op that creates no file and changes no bytes. It permits read-only status, does not delete evidence or modify legacy state. A disabled unfinished run cannot execute or integrate until explicitly enabled again.

Exit codes: `0` successful requested command (status always includes run outcome); `1` expected behavioral check failure; `2` invalid input/unsupported protocol; `3` disabled/unavailable capability; `4` incomplete/budget/interrupted/recovery required; `5` conflict/ownership/candidate mismatch. Failed checks are evidence, not CLI success disguised as a passing check. `finish` returns 0 only for a completed run; `status` may return 0 with `outcome: incomplete` because reporting status succeeded.

### Configuration and authority

`.itworks/workflow.json` schema 1:

```json
{
  "schema_version": 1,
  "enabled": true,
  "adapter": "manual",
  "defaults": {"budget_seconds": 1800, "max_repairs": 2, "max_transport_retries": 1},
  "snapshot": {"include_untracked": [], "exclude": []}
}
```

Use finite positive integer budgets; initial release accepts `max_repairs` only 0–2 and transport retries 0–1. Increasing those limits requires an explicit design/version change, not an adapter override. CLI may lower or explicitly change wall-clock allowance for a new run; it cannot replenish an existing exhausted run. Paths are project-relative, validated against traversal and forbidden metadata paths. `enable` adds exact `.itworks/runs/` ignore entry after preserving existing ignore content and reports the change. Do not add global ignore settings or a new field to legacy PROFILE. Enable/disable must roundtrip legacy version 1–3 states without migrating or rewriting them.

The optional `.itworks/PLAN.md` is a human-editable plan, not a replacement for PROJECT/DECISIONS. JSON evidence references task/check IDs local to that plan/run. No stable IDs or new grammar are forced onto old REVIEWS entries. If a finding is referenced, use file plus section/text digest as a best-effort pointer; state that changed text requires re-association. Do not copy mutable findings into evidence as a second authoritative registry.

### Run storage and identities

`.itworks/runs/<run-id>/` contains `header.json`, immutable `events/000001.json` records, redacted `artifacts/` and `candidate/`. The single project writer lock is `.itworks/runs/.writer-lock/`, shared by all runs and excluded from snapshots. Run ID is a generated UUID; timestamps are UTC. `header.json` is immutable and records schema version, run ID, project canonical path identifier, plugin revision, original branch/HEAD, plan hash, baseline worktree digest, candidate manifest digest, policy-input digest, capability snapshot, start time, original deadline and limits. Evidence claims are tied to these identities, not a date alone.

Candidate digest: SHA-256 over sorted canonical relative path, file kind, executable bit, length and byte digest for the explicit source/test/config scope manifest. Include relevant tracked and explicitly approved untracked files; exclude `.git/**`, `.itworks/runs/**` and generated evidence/output. Record exclusions explicitly. `.itworks/{PROJECT,MAP,DECISIONS,REVIEWS,PROFILE}.md`, `.itworks/PLAN.md`, workflow config and selected skill/runbook versions are control inputs with their own policy/plan digest, not application-source bytes. Candidate manifest and policy digest together identify what was evaluated. Do not silently exclude arbitrary application files called `results` or `build`; scope/exclusion rules determine their treatment. Recomputing a digest must not change it because the runner wrote a new event.

Every event includes `schema_version`, `run_id`, monotonically increasing `sequence`, `event_id`, `event_type`, timestamp, candidate digest, task/check ID where applicable, and payload. Record task and check state in events; derive summaries rather than maintaining an independently mutable status database. For modest local runs, replaying small events is sufficient. Store raw tool outputs only in restricted scratch until redacted; retained artifacts record command metadata/exit/result, not credential values.

### States, results and limits

Run transitions: `created -> ready -> executing -> reviewing -> verified -> integrated -> complete`. At any active phase, `incomplete` records interruption, missing capability, exhausted budget or unresolved issue; `conflict` records changed user workspace. A resolved recoverable incomplete state can resume at its last safe phase only before the original deadline; an exhausted run requires `start --supersedes OLD_RUN_ID` with explicit fresh budget. After proving all old child processes stopped, one locked transaction appends a terminal `superseded` event to the old incomplete/conflicted run, records its preserved candidate/evidence pointer, releases its integration ownership and creates the linked new run from a newly verified snapshot. If creation fails, the old run remains terminal and evidence intact, and no run owns integration. `abandon --reason` similarly records terminal `abandoned` after child cleanup without creating a new run. Neither terminal state counts as complete nor deletes any evidence; complete runs cannot be rewritten as superseded. No state skips required review/evidence predicates. The initial optional runner supports implementation runs only; it has no verification-only mode. Read-only audits continue through the existing audit lifecycle, with its declared coverage and independence limits. Every optional runner completion requires its planned task evidence, review and integration receipt; it never skips implementation/TDD stages by relabeling a run.

Check status: `passed | failed | not_run | not_applicable`. `not_applicable` needs the concrete applicability rule and observed inputs. `not_run` needs a reason and unresolved completion requirement. “Accepted risk” is a Markdown decision, not `passed`; it may satisfy a separate policy gate only when existing risk acceptance rules permit it.

Each task permits initial implementation plus at most two repairs. A check transport timeout/adapter transport error may be retried once inside the same original wall-clock budget; assertion failure is never transport failure. Identical candidate + check-spec + normalized outcome signature on the next attempt is no progress and terminates that loop early. Normalize the outcome to stable check/assertion IDs, exit/signal and failure category; exclude timestamps, random scratch paths and incidental log wording. A genuinely changed candidate is a distinct attempt even if the resulting assertion failure is unchanged, but still consumes a repair. Any real candidate change invalidates affected current-success receipts; first release conservatively invalidates all candidate-dependent current-success receipts. Historical intended-RED observations remain immutable provenance for their original task/candidate, not current correctness receipts. Previously done tasks become `needs_revalidation` in derived status when a later task changes the candidate. Before final review/integration, rerun every required GREEN and regression contract at the final candidate, then review that candidate; do not repeat initial RED or reset repair counters. Revalidation failure reopens the affected task within its remaining repairs/deadline, otherwise leaves the run incomplete. Two tasks can therefore accumulate historical TDD proof while sharing a newly checked final candidate. Maximum one modifying implementer at a time. Reviewers/verifiers are read-only, never spawn agents recursively, and may be parallel only with disjoint bounded review briefs and remaining budget.

Default global deadline is 1,800 seconds from `start`, explicitly configurable for each new run. Each child command's timeout defaults to 120 seconds and is min(explicit check timeout or default, remaining global budget). A longer check timeout must be explicit in its reviewed spec, never an adapter's hidden override. Persist the original deadline; resume does not reset it. Monotonic elapsed time controls a live process; after restart use original UTC deadline, and fail incomplete if clock rollback makes remaining time unreliable. Do not pretend to know host-native tokens: usage fields are nullable with `source: native | estimated | unavailable`; estimates are labelled and cannot enforce a claimed exact token budget.

## F01 — Specify and implement the opt-in protocol boundary

**Status: PENDING.**

**Depends on:** U07 patch qualification, including P-series baseline; design drafting may proceed earlier, but optional feature implementation/qualification starts after that gate.

**Files:** CLI/config/protocol modules above, `references/workflow-protocol.md`, `.gitignore` for this repository's own generated-run exclusion if enabled during development, core config/protocol tests.

**Build:** Implement argument parsing, schema validators using explicit type checks (booleans must not pass as integers), project resolution, disabled preflight, enable/disable/status, exit contract, canonical JSON serialization and unknown-version rejection. Preserve unknown legacy Markdown fields. Refuse unknown configuration fields rather than accepting misspelled controls silently. Allow additive result metadata only under a designated `extensions` object. No network, model invocation or execution in this task.

**Red tests:** Missing config then `start` returns 3 and creates nothing; `enabled:false` with existing evidence is read-only; schema 99 returns 2 without rewriting; budget `true`, zero, negative and a string fail; `enable` twice changes no content on second invocation; disable leaves all five legacy file hashes unchanged; absent Python never affects existing Bash commands. Check actual filesystem before/after, not wording in prompts.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_config.py' -v`; `python3 -m unittest discover -s tests/unit -p 'test_protocol.py' -v`.

**Done/rollout:** Validators and real CLI subprocess tests pass on Python 3.10 and newest supported Python in CI. Optional commands only; no automatic hook activation. Document supported runtime and failure codes before F02 consumers land.

## F02 — Snapshot the candidate without touching user work

**Status: PENDING.**

**Depends on:** F01; P-series secret handling and safe mutation contracts.

**Files:** `scripts/itworks_core/snapshot.py`, `tests/unit/test_snapshot.py`, `tests/fixtures/workflow/snapshot/`, protocol snapshot section.

**Build:** First release supports ordinary local Git worktrees on macOS/Linux. Detect repository root, linked-worktree gitdir, branch/HEAD, index tree and staged/unstaged tracked content. Reject unmerged index, unsupported sparse/submodule/filter/LFS configurations with `not_run` and a precise capability reason until tested. Require quiescent snapshot inputs: collect full selected path/kind/mode/content inventory plus HEAD/index fingerprint before copying, repeat after copying, and compare both to the copied manifest. Any changed selected byte/path/mode or HEAD/index yields conflict; discard the candidate as unusable and preserve originals. This detects observed concurrent changes, not an impossible guarantee against an undetectable change-and-restore (ABA) between reads; document that limitation and require the user/editor to stop writes during snapshot. Build a disposable candidate from exact working content; separately retain baseline index tree/content fingerprints for preservation checks. Do not stash, commit, checkout or reset the user's worktree. Include untracked files only from config/explicit reviewed plan scope. Never dereference symlinks out of the project; record symlink target or refuse execution when required inputs escape isolation. Recreate only safe ignored local config by declared name, without copying secret values into retained artifacts. External test services/credentials are opt-in inputs and remain a declared coverage limitation when absent.

Use an isolated temporary Git repository/snapshot under the run directory, populated from selected bytes and explicit file metadata. Git metadata never points back to the original worktree. The candidate's initial baseline is immutable; task modifications occur in its working copy. Repeated snapshot for the same inputs yields the same manifest digest. Hash executable bits and deletion/rename paths correctly; reject non-regular special files. Set conservative file-count/byte bounds (10,000 files and 100 MiB initially, configurable upward explicitly at start), fail before a partial snapshot is treated as usable.

**Red tests:** Mixed staged and unstaged changes to one source, untracked selected test, ignored fake-secret env, deleted tracked file, executable script, symlink outside root, filename with spaces/newline, linked worktree, interrupted copy. After snapshot/mutation/testing, original HEAD/index/diff/untracked bytes match exactly. Out-of-tree symlink content never appears in snapshot or evidence. Writing 50 events changes no candidate digest. Changing one application byte changes it; changing a recorded applicability input changes policy digest. Unmerged index returns unsupported without writes to user files.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_snapshot.py' -v`.

**Done/rollout:** Actual fixture Git state preservation proven on both supported OSes. No Windows support claim until isolated execution/integration tests pass there. Only synthetic credentials in fixtures.

## F03 — Retain immutable evidence and recover interruptions safely

**Status: PENDING.**

**Depends on:** F01–F02; U-series backup/recovery design must agree on artifact retention.

**Files:** `scripts/itworks_core/events.py`, `tests/unit/test_events.py`, protocol persistence/recovery section.

**Build:** Single writer per project via atomic lock-directory acquisition outside any candidate copied tree, containing run ID, owner PID/start identity and random ownership nonce. Each CLI process acquires/releases the project writer lock for its mutating transaction; a run cannot be concurrently advanced by two writers. A competing run may be created only when no active run owns unfinished candidate integration; return conflict with a status pointer. Avoid a permanent daemon. Never delete an apparently stale lock just because PID is missing; prove same-host owner terminated and record recovery, otherwise require explicit local recovery after status inspection. Read-only status never needs the writer lock.

Write each event to a same-directory temporary file, flush/fsync, then publish atomically under its unique final sequence filename; never overwrite an existing event. Fsync directory where supported, documenting platform limit. Ignore incomplete temporary files during replay but mark recovery needed. Validate monotonic sequence, run identity, schema and referential consistency; a malformed/gapped finalized event stops mutation and preserves all originals. Header/artifacts are hashed; mismatched referenced artifacts cannot satisfy evidence. `resume` replays, checks original deadline/candidate/policy identities, reconciles interrupted checks as not_run, and never reexecutes a potentially mutating command silently. Before dispatch, persist launch-intent with a nonce; a small child supervisor starts a new tracked process group and completes a parent/child identity handshake (PID, start identity, group/session ID, nonce) before executing any target command. Recovery first proves that recorded group/descendants are stopped, using host-qualified process control; stop group and verify termination when owned, or block recovery when ownership/quiescence is unknown. Parent death alone is not evidence children stopped. Commands that daemonize/escape the tracked group are unsupported unless native host isolation can enumerate/terminate descendants; do not claim a generic process group is a security sandbox. Never permit a second writer against a candidate still being modified by an orphan child. Do not duplicate successful evidence when ingest repeats identical result/event ID; divergent reuse is conflict.

**Red tests:** Kill writer before/after temp creation and final rename; two processes append simultaneously; duplicate result identical vs changed; event sequence gap; corrupted artifact; stale PID reused by another process; disabled config with unfinished run; restart after budget expiry; timezone/clock rollback; SIGKILL parent while child/grandchild keeps writing a sentinel; exhausted run followed by explicit superseding start; abandon with child still alive. Only one writer advances sequence. Every original evidence byte survives recovery. Interrupted child is not marked passed. Repeat status/replay leaves no changes.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_events.py' -v` plus `python3 -m unittest discover -s tests/integration -p 'test_workflow_recovery.py' -v`.

**Done/rollout:** Crash/concurrency integration fixtures pass, retained evidence is immutable to runner operations, and recovery procedures are documented without claiming tamper-proof storage against a user who owns the directory.

## F04 — Execute checks and enforce evidence-specific completion

**Status: PENDING.**

**Depends on:** F02–F03; patched scanner/runbook semantics from P-series.

**Files:** `scripts/itworks_core/runner.py`, `tests/unit/test_runner.py`, `tests/integration/test_workflow_checks.py`, protocol check-spec section.

**Build:** A check spec contains schema version, check ID, task ID, `argv` array, candidate-relative `cwd`, environment-variable **names** to pass explicitly, timeout seconds, applicability reference and `predicate` with required observable outcome. Execute with `shell=False`, explicit cwd, minimal environment and process-group timeout/cleanup. Never evaluate text received from a finding as shell syntax. Commands remain user/plan-authorized code and a copied directory is not a security sandbox: honor native permissions, do not claim isolation prevents arbitrary network/filesystem access. Default checks are offline local fixtures; network/live destructive probes require explicit reviewed execution context.

Check evidence records exact executable argv (redacted as necessary), start/end, exit code/signal, duration, stdout/stderr artifact hashes, candidate/policy digests, check-spec hash and predicate result. Tests distinguish expected assertion failure from import/collection/runtime setup failure. Built-in predicates initially support exit status, explicit structured unittest/custom-runner report assertion IDs and no-test detection; unsupported frameworks require an adapter rather than guessing pass counts from prose. Red and green run the same targeted test contract. Tests absent/broken/decorative cannot close with a live probe; live behavior and test existence are distinct check IDs/predicates. Live/external probe receipts include a nonsecret environment fingerprint (target identifier, configured test instance/build identifier, synthetic fixture dataset revision) and observed timestamp. Their default validity is 300 seconds, bounded by run deadline; consume them only with matching candidate and environment fingerprints. Pure deterministic local receipts have no arbitrary TTL but expire on relevant input changes. A missing/mismatched environment identity or expired receipt is not_run until re-probed; no silent reuse from a prior server instance. A scan no-match is meaningful only if scan command completed successfully and expected files were traversed. Truncated output has a count and retained redacted full artifact; missing artifact never equals clean.

Canonical check-spec file schema 1 holds a `checks` array. Each check has the fields below; source placeholders resolve only to runner-controlled paths (not through a shell). Implement `scripts/itworks_core/unittest_adapter.py` as a trusted standard-library `unittest.TestResult` bridge, loaded from the recorded plugin revision, to emit structured reports for the initial supported test framework:

```json
{
  "schema_version": 1,
  "checks": [{
    "id": "rounding-red",
    "task_id": "T01",
    "argv": ["python3", "<plugin-root>/scripts/itworks_core/unittest_adapter.py", "--test", "tests.test_pay_rounding.TestPay.test_half_cent", "--report", "<check-scratch>/test-result.json"],
    "cwd": ".",
    "env_names": [],
    "timeout_seconds": 120,
    "applicability": {"rule": "task-required", "task_id": "T01"},
    "predicate": {
      "kind": "unittest-expected-assertion-failure",
      "expected_test_id": "tests.test_pay_rounding.TestPay.test_half_cent",
      "expected_assertion_label": "half-cent rounds up",
      "min_tests_run": 1,
      "expected_exit": 1,
      "required_errors": 0
    }
  }]
}
```

The semantic spec has no mutable candidate value; invocation binds its canonical hash to the current candidate digest and records both in the event. The matching green spec uses the same argv/test ID, `kind: unittest-success`, exit 0, zero errors and zero failures. The required regression spec selects its declared suite and requires nonzero count, exit 0, zero errors/failures. Label is an explicit assertion message carried by the retained test; the independent review checks it is the intended behavioral assertion, not a deliberately unconditional failure. `TestResult.errors` includes import/setup/teardown errors and prevents intended-red acceptance; fixture cases prove the adapter's classification. A failure in a different test, an unrelated assertion, process crash, timeout or a missing report is not the requested RED. A model-provided report is insufficient: runner must observe the trusted bridge process/exit and bind its emitted report/hash to that invocation. Bridge conformance cannot prove tests are semantically good; F06 review/mutation supplies that evidence. All reports include discovered/run test IDs, run count, assertion failures, errors and skipped tests; required skipped tests block success. Permit additional predicate kinds only through versioned built-in validators with executable negative tests.

**Red tests:** `exit 0` with zero tests; failing intended assertion; import error; fake result stdout claiming pass while process exits 1; timeout leaving grandchild; paths containing shell substitutions; stderr with synthetic key; missing executable; valid N/A inputs; false N/A despite required auth; live receipt at age 301 seconds; restarted server with different fingerprint; local deterministic receipt with unchanged inputs. Assert outcome, process cleanup, untouched user files and redacted artifacts. Harmless loopback service validates live failure behavior separately from automated regression-test presence.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_runner.py' -v`; `python3 -m unittest discover -s tests/integration -p 'test_workflow_checks.py' -v`.

**Done/rollout:** Deterministic negative controls pass; no unverified output can satisfy completion. Keep existing lens commands available to legacy users without Python.

## F05 — Add a plan skill with a small reviewable task contract

**Status: PENDING.**

**Depends on:** F01, F04; P-series workflow-scope rules.

**Files:** `skills/project-plan/SKILL.md`, `commands/plan.md`, `scripts/itworks_core/plan.py` (new optional PLAN-block parser only), `references/workflow-protocol.md`, `tests/fixtures/workflow/plans/`, `tests/unit/test_plan.py`. The existing Markdown state still uses the P-series shared parser.

**Concrete skill content:** Description explicitly requires an existing enabled `.itworks/workflow.json`; explicit invocation when disabled offers the `enable` route and stops before any plan/state write. Trigger for requested nontrivial feature/fix planning; no auto-plan for a spelling change. Read current PROJECT/MAP/DECISIONS and relevant code/tests first. State observed facts vs assumptions, compare credible implementation alternatives when design space exists, then write `.itworks/PLAN.md` using the schema below. Existing user authorization may cover implementation; plan creation must not invent a mandatory extra approval gate. Ask only genuinely unresolved scope/risk questions. Never silently turn audit suspicions into approved implementation scope.

Plan shape: title, target base SHA, intent/non-goals, observed inputs, open questions, acceptance examples and ordered tasks. Each task has a stable local ID `T01`, owner role, dependency IDs, exact files, first failing test/expected reason, implementation boundary, verification command references, done criteria and risk/rollback. Runtime task status lives only in immutable run events and derived status output, never as repeated writes to PLAN during execution. Keep prose authoritative; `start` validates and extracts only required machine fields using a documented narrowly constrained Markdown block format. Do not introduce YAML/parser dependencies. Tests with no behavioral significance may use `test_exception: documentation-only` with reason; no meaningless failing test ceremony. Do not write progress/status back into PLAN during a run. Its full bytes are immutable run inputs; any user change to requirements or prose requires explicit revalidation/new plan hash and invalidates dependent success receipts conservatively. Runtime events are the single source of execution status; they do not mutate the plan hash.

The one machine-readable block is fenced with the exact info string `itworks-plan-v1`; require exactly one such block and parse its interior as JSON with the standard library. Human prose outside it supplies rationale but may not contradict its acceptance/scope. Example:

```itworks-plan-v1
{
  "schema_version": 1,
  "base_sha": "<40-or-64-hex Git object id>",
  "intent": "Round invoice halves away from zero",
  "non_goals": ["Changing tax calculation"],
  "blocking_questions": [],
  "tasks": [{
    "id": "T01",
    "owner": "implementer",
    "depends_on": [],
    "files": [
      {"path": "src/pay.py", "operation": "edit"},
      {"path": "tests/test_pay_rounding.py", "operation": "create"}
    ],
    "acceptance": [{"input": "round_money(1.005)", "expected": "1.01"}],
    "failure_behavior": "Reject invalid decimal text without storing a record",
    "checks": ["rounding-red", "rounding-green", "pay-regression"],
    "check_specs": ".itworks/checks/pay-rounding.json",
    "first_red": {"check": "rounding-red", "reason": "Boundary assertion fails because current result is 1.00"},
    "implementation_boundary": "Only monetary rounding and its focused tests",
    "done": ["Boundary assertion green", "Required pay regression suite green", "Independent review resolved"],
    "rollback": "Discard candidate before integration; after integration restore only transaction-owned unchanged bytes"
  }]
}
```

Required fields/types are exactly those above: strings nonempty, arrays of the stated records/strings, task ID matching `T[0-9]{2,}`, owner enum `implementer`, file operation enum `create|edit|delete`, at least one acceptance/check/done entry and no duplicate task/file/check IDs. `edit`/`delete` paths must exist at baseline; `create` paths must not already exist (except the test created during this run). All paths remain inside project and obey F02 restrictions. Dependencies reference existing tasks and form a DAG. Check IDs resolve uniquely in the indicated new optional check-spec file, whose bytes join policy identity. For documentation-only exceptions, replace `first_red` with `test_exception: {"kind":"documentation-only","reason":"..."}`; both fields together are invalid and the task still declares meaningful static/preview checks. No mutable task status belongs in the block. `blocking_questions` nonempty prevents `start`; an explicit scope decision removes resolved questions before execution. Unknown fields/version fail validation; no magical YAML or free-form command extraction.

**Red tests:** Plan referencing nonexistent source as observed fact is rejected by preflight; missing success/failure acceptance; cycle in task dependencies; duplicate T01; command referring to undefined check spec; exception without reason; disabled invocation; plan with unresolved blocking question. Tiny documentation-only task yields no fabricated red-green evidence. Fixture plan roundtrip preserves owner prose and task IDs.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_plan.py' -v`; live skill cases deferred to F09/F10.

**Done/rollout:** Valid plan drives a real small fixture change; malformed plans stop before execution. Skill descriptions/config gate verified in installed-host tests, not just phrase matching.

## F06 — Add execution/TDD with demonstrable red, green and regression

**Status: PENDING.**

**Depends on:** F04–F05.

**Files:** `skills/project-execute/SKILL.md`, `commands/execute.md`, orchestrator task-transition code, `tests/integration/test_workflow_tdd.py`.

**Concrete skill content:** Requires enabled config and valid plan. Existing bug: reproduce exact trigger first. New behavior: write the smallest meaningful behavior test against observed interface, execute on candidate and confirm intended assertion fails for missing/wrong behavior, implement smallest change, run same targeted test green, then related regression suite. Refactor from green and rerun. Do not weaken expectations or remove failing tests to manufacture success. A test change needs semantic review against acceptance examples; immutable red artifact preserves the original expectation. Test discovery/import/config errors never count as red proof. Fixes require reverting the specific implementation in a disposable copy to reproduce failure when feasible. Cosmetic/documentation exceptions are explicit and cannot be reused for behavior changes.

Task states: `planned -> red_verified -> implementing -> green_verified -> reviewed -> done`; bug reproduction may supply red_verified only if it is an executable regression assertion retained in the candidate. Authorized nonbehavioral exceptions use `planned -> implementing -> verified_exception -> reviewed -> done`. Failure transitions to bounded repair under F07; missing capability becomes incomplete. A green targeted test does not waive relevant regression checks. Preserve exact candidate IDs between red/green and review; source mutation never touches the original worktree.

**Red tests:** Fixture function rounds a payment incorrectly at a specified decimal boundary; assertion red, minimal fix green, unrelated arithmetic regression remains green. Companion mutant wrong return is caught. Import error/empty suite cannot advance red_verified. Deleting/assertion-weakening the failing test cannot advance green without review. Existing unrelated failing test is recorded baseline-known, never hidden, and by default blocks task/run completion if it is in the plan's relevant regression suite. Re-scoping an unrelated suite requires an explicit plan revision with a concrete reason and fresh validation; an agent cannot silently waive it or call a failed required suite green. UI/text-only exception and behavior mislabeled UI-only are distinct fixtures.

**Commands:** `python3 -m unittest discover -s tests/integration -p 'test_workflow_tdd.py' -v`.

**Done/rollout:** The fixture behavior actually changes, tests prove it, and a reverted fix fails. No percentage-coverage target substitutes for acceptance assertions.

## F07 — Implement a bounded orchestrator and explicit independent verification

**Status: PENDING.**

**Depends on:** F03–F06.

**Files:** `scripts/itworks_core/orchestrator.py`, `protocol.py`, `tests/unit/test_orchestrator.py`, `tests/integration/test_workflow_loops.py`, protocol adapter boundary.

**Build:** Main agent owns plan interpretation, applicability, delegation, deduplication, user questions and the final report. Runner enforces state/evidence transitions, limits and candidate identity. Implementer changes only isolated candidate task scope; reviewer reads a pinned candidate and tests, reports suspicions with exact input/file/trace plus coverage; verifier is a distinct invocation/session from reviewer, reproduces without accepting the reviewer's words as proof. If host cannot delegate independently, declare independence unavailable and leave independent-verification requirement incomplete, or fall back to the existing read-only audit outside the runner, without claiming independent audit completion. Do not invent a second identity within one transcript.

Adapter request JSON v1: request/run/task IDs, role, parent event sequence, candidate/policy/plan digests, read scope, write scope (empty for review/verify), acceptance/check-spec references, remaining seconds, repair index, allowed capabilities, nonrecursive delegation flag and output path. Adapter result JSON v1: matching identities, invocation/session identity and host/version/model identity (unknown allowed), status `completed|incomplete|failed`, evidence artifact references, candidate digest after execution, proposed next transition, coverage read/skipped, structured suspicions or verification verdicts `confirmed|refuted|partial`, usage source and nullable counts. Results are proposals; `ingest` validates identity, artifact paths confined to the run, artifact hashes, permitted writes and allowed transitions before appending evidence. An adapter cannot self-attest that arbitrary model prose is an executed PASS. Never treat free-form explanation as an executed test receipt. A verifier may be same model family but must have independently recorded execution context; this is process independence, not proof of statistical independence.

One initial implementation + two repairs per task, one transport retry per request, original global deadline from F01. On same candidate/spec/failure signature, stop early as no progress; new error on unchanged candidate still consumes the same attempt budget. Permission denial is not transport failure and cannot be retried as bypass. New scope/requirements return to planning; new confirmed findings return to plan/acceptance policy. No unattended cost-bearing model calls unless their invocation/budget is within user's existing authorization.

**Red tests:** Scripted adapters emit success without artifacts; wrong run/candidate ID; forged reviewer equals verifier session; reviewer modifies candidate; stale result after new candidate; endless failing implementer; timeout then one retry; assertion failure wrongly marked transport; global deadline expires during retry; no-progress identical outcome; token usage unavailable. Assert exact invocation counts, denied transition, preserved receipts and incomplete output. Happy path uses distinct local adapter processes and real F06 fixture checks. A two-task fixture makes T01 green, changes candidate for T02, observes T01 needs_revalidation, reruns both green contracts at the final candidate without replaying initial RED, and preserves each task's consumed repairs. A regression caused by T02 must reopen T01 or stop incomplete, never keep stale green.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_orchestrator.py' -v`; `python3 -m unittest discover -s tests/integration -p 'test_workflow_loops.py' -v`.

**Done/rollout:** All loop termination/identity negative controls pass. No model-brand condition substitutes for successful evidence or independent context.

## F08 — Integrate safely with legacy lifecycle and candidate compare-and-swap

**Status: PENDING.**

**Depends on:** F02–F07, P-series lifecycle patch, U-series legacy roundtrip and recovery tests.

**Files:** conditional sections in all five existing `skills/*/SKILL.md`, optional command documentation, `scripts/itworks_core/snapshot.py`, `orchestrator.py`, `tests/integration/test_workflow_lifecycle.py`.

**Build:** Legacy flows remain default. Enabled lifecycle skills may attach runner evidence but preserve existing Markdown authority and opt-out behavior. Consume the P-series shared shell/awk parser's documented structured output for legacy Markdown validation/findings/acceptances; do not implement a second Python parser. The new narrowly specified PLAN block parser is only for that new optional file. Before any enabled state-write/repair, create and verify an external backup of affected state with paths/modes/hashes as required by `contracts.md`; never overwrite a newer state file from an old backup. Resume distinguishes legacy narrative evidence (historical/unverified by runner) from current machine receipts; never fabricate receipt history from old “Closed” lines. Audit timestamp advances only after declared scope completion; incomplete run gets attempted date/coverage in report without inventing successful currency. Closeout gathers applicability/sweep/checklist results before reckoning and validates new findings before ship document. Accepted risk remains accepted, not a green check.

`integrate` requires verified candidate, expected original HEAD and full baseline worktree/index fingerprint, and current candidate/policy hashes. Recheck under writer lock immediately before applying only planned file changes. This is a guarded compare-before-write transaction, not filesystem-atomic compare-and-swap against arbitrary editors: the lock excludes runner writers only. Require quiescent external editing, compare each target's expected original bytes/mode immediately before its write, and detect post-write differences. If external edits are observed, stop conflict and preserve both versions; do not restore a backup over newer external changes. Document the residual check/write race and do not advertise stronger atomicity than the filesystem provides. A changed source, branch/index or relevant policy causes conflict and no writes. Stage integration patch in scratch, run `git apply --check` or equivalent safe validation without altering index, then apply scoped bytes with per-file original backups and transaction journal. Never commit automatically. Failure partway restores exact backed-up working bytes/modes and leaves the index as it was; unresolved restore failure retains journal and instructs recovery, never “complete.” Existing staged/unstaged mixed state is preserved: only working content changes by the approved candidate delta, index is unchanged. Integration must not overwrite arbitrary untracked files; unexpected path collision is conflict. Final validation runs on actual integrated content; original staged work is not falsely described as committed.

`finish` verifies required tasks/checks/reviews completed, integration receipt, no expired budget or changed candidate, and writes a short Markdown evidence reference in the appropriate lifecycle report. Immediately before finish, re-hash integrated application bytes and the exact pre-finish plan/policy inputs used for verification. Any unrelated Markdown edit since verification invalidates completion; revalidate instead of appending a stale receipt. The only allowed control change in this transaction is one exact append-only final receipt block prepared and hashed before writing. Append to the existing appropriate lifecycle section, never rewrite findings/acceptances as part of finish. Record a finish-prepared event with pre-policy digest and receipt bytes/hash; append only if target original bytes still match; then record finish-completed event with post-append digest. The receipt references run ID, prepared-event ID, candidate digest and evidence path, not its own hash. Interrupted recovery either observes the exact already-appended block and finalizes once, or sees unchanged preimage and resumes append, or returns conflict; it never duplicates the receipt. Further state-note edits are separate new control changes and invalidate evidence reuse where applicable, not silently represented as part of an earlier application receipt. Archive/disable leaves evidence available; no legacy linter requires it to exist.

**Red tests:** Old v1/v2/v3 states with Closed/Accepted entries; no config; disabled config; conflict after another editor changes one byte; branch switch; user stages a file mid-run; untracked collision; failure on second file of three; integration followed by failing actual-worktree check; accepted critical with outstanding remainder; skipped audit lane; interrupted closeout. Assert no unintended changes, exact restored hashes and truthful currency/receipts. Repeated integrate of same completed transaction is idempotent; changed candidate requires new verification.

**Commands:** `python3 -m unittest discover -s tests/integration -p 'test_workflow_lifecycle.py' -v` plus U's full upgrade/rollback gate.

**Done/rollout:** Enable -> run -> disable and old/new plugin roundtrips pass on fixture copies. No production installation/update or publish is part of implementation tests.

## F09 — Package and qualify Claude, Codex and Antigravity adapters independently

**Status: PENDING.**

**Depends on:** F01–F08 and U05 clean-host/installed-plugin qualification; this task owns its conformance case definitions (F10 expands measurement after conformance).

**Files:** adapter directories above, adapter contract fixtures, `tests/integration/test_workflow_adapters.py`, README support table. New host packaging must not duplicate divergent core runbooks; reference/copy with generated-content checks from canonical sources.

**Build:** Treat “Agy” as assumed Google Antigravity, to be corrected before publishing an installation claim. Before implementing a host invocation, define local conformance cases for identity, permissions, actual tool output and disabled behavior; these are F09 deliverables and avoid a dependency cycle with F10. Record dated official documentation and installed CLI/help output; choose flags only from that evidence. Current verified skill-discovery pointers are [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Codex scoped instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Antigravity skills](https://antigravity.google/docs/skills), and [Antigravity workflow migration](https://www.antigravity.google/docs/ide/workflows/). These establish packaging surfaces, not working execution flags, hook equivalence or live qualification. Recheck them at implementation because host behavior changes.

For Claude, preserve current `.claude-plugin`, hooks and slash wrappers and qualify installed skill discovery/model pin behavior using current official docs and actual host. For Codex, use repository-scoped skill packaging and applicable AGENTS instructions, declaring optional implicit-invocation policy only if current documented schema supports it. For Antigravity, use current documented skills surface; do not assume legacy workflow files, Claude hook JSON or command names work unchanged. No adapter silently copies into global configuration or overwrites user instructions. Installation must have previewed target paths and reversible removal of only owned artifacts.

Capability probe records host name/version, instruction/skill loading path, shell support, actual permission model, browser availability, safe subprocess termination, independent delegation, model identity visibility and usage visibility. Unknown capability is unavailable, never guessed. Manual adapter supports JSON request/result handoff without pretending automated model invocation. Live qualification uses disposable project fixtures and explicit user-authorized credentials/cost; simulated adapter conformance is a separate result. If a host lacks independent sessions/delegation, mark independent audit unsupported rather than silently running same-session verification.

**Red tests:** Installation under nested repo scope loads intended instructions; disabled optional skill does not write state or run checks; permissions denied; absent shell/browser/delegation; unknown model; malformed tool result; unsupported CLI version; non-ASCII/spaced project path; uninstall leaves unrelated skills untouched. Real fixture command must write expected artifact in candidate, never just say it did. Cross-host same fixture yields same normalized state/evidence contracts. Host runtime snapshot in every retained result.

**Commands:** `python3 -m unittest discover -s tests/integration -p 'test_workflow_adapters.py' -v`; live commands recorded only after CLI verification, separately per host with exact version and budget.

**Done/rollout:** Publish support table as `not tested`, `simulated conformance`, or `live qualified` per host/version/capability. A Claude pass qualifies no other host. No universal “Opus class” or newer-is-better assurance. Available adapter is not equivalent to proven reliability.

## F10 — Measure reliability and performance before expanding rollout

**Status: PENDING.**

**Depends on:** F04–F09, P09 regression baseline and U07 release-evidence verification.

**Files:** `tests/evals/workflow-cases.json`, executable fixture cases, `scripts/evaluate-workflow.py`, `tests/evals/README.md`, dated ignored/raw and redacted retained evaluation artifacts following U's evidence rules. Reuse existing eight pressure case intents where relevant; do not represent their simulated outputs as live tools.

**Build:** Define case manifest with fixture revision/hash, intent, permitted writes, exact initial state, seeded defect, required observed commands/artifacts, forbidden changes, expected final behavior, and whether human judgment is needed. Deterministic scorer reads actual final filesystem/process/evidence outputs; separate blinded reviewer scores semantics/tone only. Model under test cannot author the user script, expected outputs or its own passing score. Version model, host, plugin, case, grader and protocol; preserve failed/incomplete attempts in denominator. Keep native/estimated/unavailable usage distinct.

Minimum behavioral matrix: ignored env vs public secret; dirty-worktree preservation; zero-tests/import-error TDD failures; true arithmetic red/green/revert; safe unrelated changes; missing independent verifier; stale evidence; interrupted resume; exhausted/no-progress loop; legacy enable/disable; incomplete audit currency; closeout discovers new finding. Add clean controls so false-positive rate is measurable. Fixed repeat counts and budgets are selected before model runs; start with three runs per host/model/case as a smoke qualification, explicitly inadequate to assert broad reliability. Larger samples are justified by confidence interval/variance and cost, not post-hoc cherry-picking. Any forbidden user-file write, fabricated passing evidence or exceeded retry bound is a hard failure independent of mean score.

Performance: measure deterministic runner startup, manifest hashing at 100/1,000/10,000 fixture files, event replay at 100/1,000 events, total check execution and adapter/model wall time separately. Record p50/p95 across >=20 local repetitions for deterministic timing after one excluded warmup; record OS/CPU/Python/cache condition. Compare legacy opt-out startup with patched baseline; default users should incur no Python startup. Set initial acceptance budget: disabled legacy startup within baseline noise (report absolute ms); core status on 1,000 events <250 ms p95 on recorded reference machine; 1,000-file/10 MiB candidate digest <1 s p95 there. These are proposed thresholds, not current measured results; if unmet, profile and justify a threshold revision before release. Do not reduce checks to meet a latency claim.

Reliability metrics: case completion with required evidence, false pass, false blocker, mutation killed/not killed, preservation failures, loop bound violations, incomplete rates, median total time, model calls and measured cost where available. Report current sample counts and intervals, not unsupported “reliable” labels. Improvement claim requires same case/version/environment baseline and new candidate; a changed case suite is explicitly noncomparable.

**Red tests:** Scorer rejects forged green transcript without test receipt; missing/incomplete attempts affect denominator; model identity leaks excluded from blinded pack; fake usage not accepted as native; corrupt artifact hash fails; evaluation interrupted midway resumes without replacing failed attempts; hard failure cannot be averaged away; subprocess timeouts included in cost/time accounting.

**Commands:** `python3 -m unittest discover -s tests/unit -p 'test_evaluation.py' -v`; `python3 scripts/evaluate-workflow.py --cases tests/evals/workflow-cases.json --mode deterministic --output PATH`; host/model evaluation invocation schema follows F09's verified adapters and explicit run budget.

**Done/rollout:** Deterministic suite passes; raw evidence integrity and independent result review complete; U-series rollback/compatibility gates pass. Enable only in disposable/personal opt-in pilots first. Broader support/release requires owner-approved identity and published honest host matrix; no public deployment or automatic enablement follows from task completion.

## Lane completion

F01–F04 establish the optional foundation; F05–F08 add demonstrable task execution and safe lifecycle integration; F09–F10 qualify hosts and claims. Run the full local suite once at integration:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py' -v
python3 -m unittest discover -s tests/integration -p 'test_workflow_*.py' -v
```

These commands describe planned tests, not tests already present or passed. Release requires the U-series gates as well as these checks. No feature in this lane can weaken the P-series fixes or make Python a dependency for users who never enable the new workflow.
