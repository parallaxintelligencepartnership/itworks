# Text-simulation harness

This developer harness captures fixed-script conversations. It does not activate an
installed plugin, qualify a model, or assign a behavioral PASS. Python standard library
is a developer dependency only; consumers still use the shell runtime.

The previous runner's unrestricted live invocation has been removed. The positional
interface remains `bash run-case.sh <case-dir> <model> [runs]`, but live mode exits 69
before any CLI call: **BLOCKED: no approved live adapter**. A task-specific config
folder or temporary cwd alone is not an OS sandbox.

## Offline mechanics

Ordinary unit/integration tests invoke only `tests/fixtures/harness/mock-cli.py`, through
an absolute Python path; mock mode never resolves a `claude` executable from PATH.
`ITWORKS_HARNESS_MODE=mock` and `ITWORKS_MOCK_CONFIG=/absolute/config.json` select it.
The config object requires a `record` path and optionally `reply`, `stderr`, `exit`,
and `delay`. These values are synthetic test controls, not credentials. No real API
client or model is used. Run from repository root:

```sh
python3 -m unittest discover -s tests/unit -p 'test_harness.py'
python3 -m unittest discover -s tests/integration -p 'test_simulation*.py'
bash -n tests/pressure/harness/run-case.sh tests/pressure/harness/host-preflight.sh
```

`ITWORKS_MAX_REQUESTS` defaults to 20 (maximum 100), runs are 1..10, and each script
has at most 20 turns. `ITWORKS_TIMEOUT_SECONDS` defaults to 30 (maximum 300) per request.
The process group is killed on timeout. These limits are offline mechanics; no paid
budget or token accounting is claimed. An eventual live adapter must enforce the
explicitly authorized total cost and wall-clock bounds as well.

Each run uses a new private temporary cwd and config directory. HOME is never changed.
The child receives a minimal environment without API credentials or copied settings.
Only the exact target skill and explicit `reference-manifest.txt` entries are inlined,
followed by fixture facts and scripted user turns. The rubric/golden answers are never
included. Target paths must be repository-relative skills/*/SKILL.md; references must
remain inside references/. The reviewed manifest lists every current reference,
including pattern files; update it deliberately when transitive references change.

## Evidence and judging

Artifacts default outside the checkout to the system temporary directory; set
`ITWORKS_RESULTS_DIR` to an external private location to retain them. Every invocation
allocates unique `run-*` directories atomically, even with identical clocks/models/cases.
Existing directories are never reused. Each directory retains exact input snapshots
and SHA-256s, each actual prompt and hash, partial stdout/stderr, conversation JSON,
and private manifest (plugin HEAD plus input hashes identify dirty content; requested
model, resolved model `unknown`, mock CLI version, preflight identity, timing and exits).
These files may contain synthetic fixture findings; keep raw artifacts private.

Exit 0 and manifest CAPTURED mean all replies were captured, never behavior PASS.
Whitespace, empty replies, nonzero CLI exits and timeouts leave INCOMPLETE artifacts and
exit 1. Their original exit status remains in the manifest. No automatic retries erase
failures. The run request/turn count is checked before any invocation.

```sh
python3 tests/pressure/harness/export-judge.py /path/to/run-unique /path/to/new-judge-dir
```

The export includes only conversation turns, removes the requested model identifier
case-insensitively, and uses generic filenames without raw run metadata. It never
copies the fixture's internal model metadata or the raw prompt. Give the independent
judge that export and the separately selected fixture/rubric; sanitize any fixture
metadata before sharing. Do not share the private manifest. Model self-identification
through unrecorded aliases or prose may need human redaction before blind judgment.
The exporter refuses an existing destination, protecting prior judgments.

`score.json` starts INCONCLUSIVE, or INVALID_EVAL for incomplete infrastructure, with
an empty independent reviewer/check list. An independent reviewer records PASS/FAIL/
INCONCLUSIVE/INVALID_EVAL and evidence against each rubric check. CLI rejection or
unsupported flags is infrastructure failure, never a passing tool-denial canary.
A captured transcript must not be promoted to PASS by this runner or its author.

## Real-host qualification remains blocked

Read-only local inspection on 2026-10-11 found Claude Code 2.1.296. Its help and the
[official CLI reference](https://code.claude.com/docs/en/cli-reference) document tool
selection, safe mode and settings-source controls. Managed policy remains applicable;
safe mode is not proof that all policy-configured hooks are absent. The
[settings reference](https://code.claude.com/docs/en/settings) describes
CLAUDE_CONFIG_DIR as relocating settings/history/plugins, not OS-level isolation.

No real invocation shape is enabled or certified. Before adding a live adapter:

1. Provision a disposable OS account or VM with no unrelated data/credentials, pin the
   CLI and official documentation identity, inspect effective managed policy, and
   supply approved noninteractive authentication without copying production settings.
2. Agree bounded requests, turns, wall time and paid budget; verify exact supported
   flags and configuration using that pinned host. Preserve all managed restrictions.
3. Run an explicitly authorized canary asking for tool/file actions. Capture tool
   events and external sentinel hashes. Actions must be impossible or denied; an
   invalid invocation/auth failure is INVALID_EVAL. Record output, host/config identity
   and exact final invocation for independent review.
4. Only then enable that adapter and run behavior cases. Without these steps live
   simulation and installed-plugin qualification remain NOT RUN/BLOCKED.

## Corrected fixture oracles

Case1/2 accept honestly held unanswered gates. `case-kickoff-complete` supplies all six
answers plus explicit confirmation; endless refusal fails progress. New kickoff state
uses format3. Case6 without rollback evidence must stay incomplete. Its separately
selectable rollback-evidence.md records one disposable file restoration, not application
or data rollback. Case7 retains the old timestamps as a negative control (actual ISO36
40/8), plus a real Sunday boundary (ISO35 8/0 + ISO36 40/0; company40/8).

```sh
go run tests/fixtures/overtime/main.go < tests/fixtures/overtime/inputs.json
python3 -m unittest discover -s tests/unit -p 'test_eval*.py'
python3 -m unittest discover -s tests/integration -p 'test_overtime*.py'
```

Go and America/Chicago zone data are developer-test capabilities; CI must provision
Go and cannot silently skip regeneration. Dated historical results in pressure-tests.md
remain history, not corrected-oracle passes. Fixture prose cannot substitute for actual
executable evidence, and offline mocks cannot prove a live model follows the skills.
