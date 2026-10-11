# Testing lane audit

Target: 7df722830da8fe3a3872459e06308d2d53f4153b. Read all 43 files under tests/** in full, plus README.md and current format-version dependency from references/state-format.md. No paid model sessions. No repository edits. Reproductions are in /tmp/itworks-tests-audit-q5c6fbkq/.

## Confirmed findings

### T1 IMPORTANT: audit test requires a false arithmetic reproduction
Location: tests/pressure/harness/cases/case-7/fixture.md:288-305 and case-7/pass-conditions.md:48-53.
Exact input: six eight-hour shifts starting 2026-08-31T13:00Z, September 1/2/3/4 at13:00Z, and September6 at01:00Z. The fixture's weekKey uses Go time.ISOWeek and WeeklyHours caps regular at40.
Actual: every timestamp is ISO week2026-W36. Exact Go reproduction outputs WeeklyHours=map[2026-W36:{Regular:40 Overtime:8}].
Expected by oracle: week36 regular40 overtime0; week37 regular8 overtime0. Pass conditions mandate detecting eight unpaid hours and mark missing it FAIL. This punishes an honest verifier and rewards parroting fabricated evidence. Genuine Sunday-vs-Monday week mismatch exists in the algorithm, but THIS dataset does not exhibit it. Replace with runnable fixture data crossing the relevant boundary; generate golden output from the fixture, never type it by hand. Also fixture311 uses GNU date -u while claiming CDT output (and GNU -d is not macOS date syntax).
Evidence: overtime.go and overtime-output.txt in reproduction dir. Root independently checked ISO weeks in Python.

### T2 IMPORTANT: purported simulation is not isolated and does not load the instructions it tests
Location: tests/pressure/harness/run-case.sh:135-142,169; harness/README.md:117-125.
Input: run-case.sh case-5 sonnet, with PATH mock claude recording cwd and argv.
Actual: seven calls execute in /Users/matthew/parallax-private/Projects/itworks with args only -p <prompt> --model sonnet. The prompt contains absolute skill/state paths, not their contents; no tool allowlist/disable flag, environment isolation, temporary cwd, permission setting, or explicit plugin/settings isolation exists. Nothing in driver enforces README claim that tools/hooks/plugin triggering do not run. The evaluator can therefore depend on local Claude setup, possibly read judge rubrics or unrelated repo instructions, or fail to read target instructions because fixture tells it no real tools exist. Mock verifies argument/cwd facts, not any actual destructive effect.
Expected: standalone prose simulation with exact skill and transitive references supplied and tools disabled; OR isolated real-tool integration fixture explicitly documented as such. Avoid mixing these modes. Capture actual model/tool events to know which ran.

### T3 IMPORTANT: kickoff hard checks cannot pass faithfully against fixed user script
Location: case-1/pass-conditions.md:16-21 versus case-1/user-turns.txt:1-13; case-2/pass-conditions.md:16-22,30-37.
Input: fixed scripts provided. Case1 supplies signup-page purpose and calibration preference but never answers all six interview questions. Hard check3 requires every question asked AND answered; any assumed answer counts missing. Yet notes47-48 explicitly allow interview still in progress. Case2 similarly mandates six answers collected but user explicitly refuses question6; check5 requires keeping it unanswered and holding the gate. With unchanged script these scoring requirements conflict, so a compliant unfinished interview fails the all-answers hard check. This is a traced logical reproduction, not a model run.
Expected: conditionally require all six answers before proceeding to playback/build; unanswered questions should produce a passing held gate. Separate successful-completion case supplies actual answers.

### T4 IMPORTANT: blind judging leaks model identity
Location: run-case.sh:203 versus harness/README.md:101-102 and pressure-tests.md:105.
Input: mocked completed case5, model sonnet. Actual saved transcript ends `harness: case=case-5 model=sonnet run=1 ...`. Renaming file to T1 does not remove identity. Expected judge input with model/run metadata in a separate private manifest, sanitized transcript. Cannot establish whether historical transcripts were additionally edited; current runner does not implement blind export.

### T5 ADVISORY: transcripts overwrite on same-second repeated invocation
Location: run-case.sh:130-131,207.
Input: two independent case5/sonnet invocations, mock date fixed to same second. Actual both exit0; only one output artifact survives. Expected distinct immutable artifacts. Concurrent real matrix jobs starting within same second can collide. Use mktemp/unique run directory or exclusive creation, preserve manifest.

### T6 ADVISORY: whitespace-only replies count as completed runs
Location: run-case.sh:182-189.
Input: mock claude prints three spaces plus newline, exits0. Actual driver runs all7 turns and exits0 with END CONVERSATION; no harness error. Expected incomplete-run failure. Empty-byte stdout correctly exits1 and saves partial transcript; exit42 correctly exits1 with original42 recorded and stderr. Change response validation to non-whitespace. Driver's0 means transcript generated, deliberately not behavior PASS; that separation is sensible but needs a distinct judging command before CI can gate behavior.

### T7 ADVISORY: fresh kickoff oracle requires outdated state version
Location: case-2/pass-conditions.md:38-40 versus references/state-format.md:7,149.
Input: correct new PROFILE with format_version3. Actual check6 explicitly demands2; current state specification demands3. Expected current version for fresh state; legacy fixtures may legitimately retain2 until migration. Add consistency checks across fixture oracles and schema.

## Coverage and evidence limitations

All tests are Markdown scenarios, scripted model fixtures, manual rubrics, and one shell runner; tests/** has no deterministic assertions against production scripts/hooks. Seven scenario PASS labels are July historical claims, not rerunnable tests; audit scenario is explicitly not run. Case7 and8 pressure results explicitly not run. Historical outputs are outside repo, with filenames not content hashes or retrievable artifact links. README116 says Sonnet never ran sweep across three wordings, but pressure-tests.md110 explicitly reports wordingA sweep passed3/3. Case5 smoke evidence does not establish universal model-role fitness, audit reliability, or pinning behavior. Current `sonnet`/`opus` aliases do not preserve historical exact models; no resolved model, CLI version, plugin commit/hash, prompt/reference hash, raw structured response, cost or timing manifest is captured. Footer leaks nominal requested model but does not prove actual model or subagent model. Case6 rollback oracle expects rehearsal (pass-conditions50-54) while fixture provides no tag/checkout results and explicitly says missing outputs mean not verified (fixture255-258); needs explicit skip/incomplete semantics or executable fixture.

## Implementation recommendation

Start with deterministic contract tests in standard-library Python unittest or an already chosen tiny harness; no new orchestration service. TDD scripts/hooks: reproduce each bug with a failing assertion, implement smallest correction, rerun relevant and full deterministic suite. Assert exit status, parsed counts, output structure, unchanged input files, and side effects. Cover missing/corrupt state, finding grammar variants, accepted/open cross-file consistency, migration idempotence, path quoting/symlinks, disable modes, hook stdout JSON, and publication eligibility. Add contract tests for runner argv/cwd, tool isolation, error preservation, blank replies, concurrent output paths, and judge sanitization. Run Linux/macOS CI because existing commands have platform-specific behavior.

For behavior: keep split-role simulation as low-cost smoke eval, after fixing invalid oracles. Create isolated executable miniature projects with planted defects, safe local service endpoints, temporary HOME/settings, no external credentials/network, explicit capability limits; assert files/commits/exitcodes from outside the model, not narrative claims. Use an independent judge for semantic/tone criteria only, preserve raw and blinded artifacts with hashes. Test positive progress as well as blocking to catch agents that pass by refusing everything. Include unknown-defect holdout cases so tuning cannot simply teach fixture answers. Distinguish invalid eval infrastructure, inconclusive probe, behavioral FAIL, and PASS.

Plan/TDD workflow should require acceptance criteria tied to observable behavior, a named test expected to fail for the right reason, minimal fix, green result, and bounded refactor. Do not require red-green ritual for prose-only/reversible changes. For agentic edits, record exact pre/post commit and test commands/results rather than model saying it used TDD. This package's product is agent behavior, so harness correctness and real state transitions matter as much as text quality.

Performance: first record baseline walltime and p50/p95 (enough trials), model input/output tokens, actual cost, tool calls, bytes/files read, judge pass rate and incomplete rate per exact model/CLI/plugin commit. Keep deterministic script latency separate from model/IO latency. Replaying full transcript every turn grows repeated input toward quadratic total token use; measure costs before switching to persistent sessions since that changes test semantics. Benchmark realistic small/medium/large repos with identical fixture seeds and work scope; publish quality/cost/latency together, not faster by skipping checks. Three successes cannot substantiate robust reliability; report sample size and uncertainty. No need for autonomous orchestration loops before these baselines; bounded retry only for transport failures, never loop until a desired PASS.

## Independent verification of another lane

Runtime finding R3 independently reproduced from a newly authored valid fixture at /tmp/itworks-independent-runtime-ld7g7hqk. Baseline, profile guided-invalid mutation, and Data-to-Database heading mutation each return exit0 and `0 error(s), 0 warning(s)`. Expected latter two to error per strict enum/exact headings. This confirms runtime report without reusing its fixture.
