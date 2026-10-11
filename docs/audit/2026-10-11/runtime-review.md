# Runtime/state audit — 2026-10-11

Target: 7df722830da8fe3a3872459e06308d2d53f4153b. Read-only repository audit. Full current files read: scripts/itworks-lint.sh, hooks/hooks.json, hooks/session-start.sh, both .claude-plugin JSON files, all five commands, references/state-format.md and references/publish.md. Historical AUDIT.md read in full, relevant historical Q-8/Q-9/Q-12 verification sections read, other historical reports searched for runtime seams. No repository edits. No remote mutation. No model behavior claims from these shell probes.

Evidence: scratch fixture /tmp/itworks-runtime-4slpj3u4, initial measured outcomes in results.json. macOS /bin/bash 3.2.57 and system grep; GNU/Linux not exercised. The fixture uses all eight exact PROJECT headings, five MAP headings, DECISIONS title, PROFILE format 3/guided, valid checkpoint and audit dates with SHA, all five lens debt keys zero, and SHIPPED with the accepted risks heading. This baseline returns exit 0, zero errors, zero warnings. Each mutation below was isolated from this baseline.

## R1 — IMPORTANT: alternate Markdown checkbox formatting makes an open CRITICAL invisible

Location: scripts/itworks-lint.sh:85-100, :118-122; publishing repeats the same anchored grammar at references/publish.md:155-167.

Exact REVIEWS inputs tested independently:

```
  - [ ] CRITICAL | security-auth | exposed key | Evidence to close: rotate key
```

```
* [ ] CRITICAL | security-auth | exposed key | Evidence to close: rotate key
```

Actual for both with SHIPPED present: exit 0, `0 error(s), 0 warning(s)`. Expected: invalid canonical syntax must be reported, or normalize the Markdown finding and flag the open CRITICAL. Never silently discard it. State-format.md:200 promises every unchecked finding parses and :202 prohibits open CRITICAL alongside SHIPPED. These are ordinary Markdown list spellings, so a human editing their own state can lose the gate without intending to. Publish greps also omit such findings. A model may still visually catch them; this is a deterministic validation failure, not proof that every model would deploy.

Control: removing the two leading spaces gives exit 1, open CRITICAL ship-gate error and OUTSTANDING warning.

Fix: detect candidate finding/task-list lines broadly, parse one canonical representation, and make malformed candidates explicit errors. Use the same parser for gate state and publication counts. Regression fixtures must include indentation, tabs, `*`, extra spaces, bad severity/lens, and unterminated lines.

## R2 — IMPORTANT: empty Accepted risks section validates an unacknowledged critical waiver

Location: scripts/itworks-lint.sh:94-104, especially :103; state-format.md:200 requires the verbatim accepted-risk entry.

Exact REVIEWS input:

```
- [x] CRITICAL | security-auth | exposed key | Accepted 2026-10-11: see Accepted risks
### Accepted risks
```

Actual with SHIPPED: exit 0, zero warnings. Expected: report that the accepted finding has no corresponding risk entry or user's recorded words. The code only checks existence of a heading anywhere. There is no join between accepted findings and acknowledgments. This matters because explicit individual user acceptance is the exception permitting critical shipment.

Fix: stable finding IDs and explicit matching acceptance records, checked for missing/duplicate/empty user wording. A minimally invasive first fix rejects accepted findings when the section has no entries, but this alone does not handle multiple findings with only one acknowledgment. This validator cannot prove a recorded quote was actually spoken; transcript/orchestrator provenance is a separate limit.

## R3 — IMPORTANT: strict PROFILE and PROJECT rules are prefix matches

Locations: scripts/itworks-lint.sh:28-31 and :140-141; state-format.md:199-201.

Mutation 1: `profile: guided` -> `profile: guided-invalid`. Actual: exit 0, zero warnings; sed truncates to `guided`. Mutation 2: append second `profile: invalid`. Actual: exit 0, zero warnings; `head -1` ignores duplicate conflict. Mutation 3: replace `## Data` with `## Database`. Actual: exit 0, zero warnings; grep lacks end boundary. Expected: invalid enum/conflicting duplicate/missing exact required heading are errors. Normal template inline comments (`profile: guided # ...`) must remain accepted.

Fix: parse complete scalar value allowing comments; reject duplicate singleton keys; anchor headings through optional Markdown closing hashes/trailing whitespace only. Fixture coverage should exercise invalid suffixes, duplicate keys, and heading lookalikes.

## R4 — ADVISORY: missing required drift warnings and closure-field anchoring

Location: scripts/itworks-lint.sh:49-57, :94-97; state-format.md:206.

Remove `llm-security` debt key and change checkpoint to a date without SHA. Actual: zero warnings, despite explicit documented drift warnings. The current loop only detects unknown keys, not absent ones or numeric validity.

Separate input:

```
- [x] CRITICAL | security-auth | regression since Closed 2026-10-11 | Evidence to close: rotate key
```

Actual: exit 0, zero warnings; expected checked-line drift warning because the closure token is in the description, not the terminal closure field. Regex `.*(Closed|Accepted|Verified)` is unanchored to the field delimiter. Publication's closed count does require a delimiter, so lint and publication disagree on this line.

Fix: test the documented drift contract and parse the final status/evidence field rather than scan the whole description.

## R5 — ADVISORY: publishing assumes TMPDIR exists

Location: references/publish.md:205.

Exact expansion: `/bin/bash -c 'unset TMPDIR; printf "%s\n" "$TMPDIR/itworks-site-abcdefgh2345"'` outputs `/itworks-site-abcdefgh2345`. Expected temp directory; actual filesystem root. In shells with nounset it aborts instead. TMPDIR is optional on Linux. Following this on a normal unprivileged Linux user makes clone fail, and the runbook's no-retry rule stops publication. No network clone attempted.

Fix: `mktemp -d "${TMPDIR:-/tmp}/itworks-site.XXXXXX"` and quote source and destination paths. Tests should run with TMPDIR unset and with spaces in both project and temp paths.

## R6 — ADVISORY: publish count pipelines fail on optional absent archive under pipefail

Location: references/publish.md:151-167.

In fixture without optional .itworks/archive, run the documented found pipeline under `/bin/bash -o pipefail`: it prints `1` but exits 2 because grep was passed a nonexistent directory; stderr was suppressed. Under `set -e -o pipefail` automated publishing aborts on a normal project. This is conditional on shell options; default shell pipeline gives exit 0 and the numeric result is correct.

Fix: build the file list from existing files only and distinguish grep no-match from read failure, or derive all counts using the common parser. The ID generator's infinite tr -> head pipeline has a similar pipefail SIGPIPE concern; not separately tested here.

## Measured performance, not a blocking defect

scripts/itworks-lint.sh:75-101 launches two grep pipelines per finding. Measured wall time with canonical closed findings (single runs, warmed local disk): 10 = 0.078s; 100 = 0.383s; 800 = 2.692s. At 800 lines the archive warning does not trigger yet (`> 800`). There is no proved timeout in this path, but per-finding process launches are an avoidable cost on every resume. Move to a single-pass awk or small standard-library parser after compatibility fixtures are in place; benchmark repeated runs and report median/p95 before claiming an improvement. Do not add a service/database for this workload.

## Controls and earlier fixes confirmed

- bash -n passes both runtime scripts. All three JSON manifests parse.
- Hook with state: exit 0, lifecycle block includes resume (1501 bytes). Without state: exit 0, adoption/new-project block (678 bytes). ITWORKS_DISABLE=1 and project .itworks-off each emit zero bytes and exit 0. No integration claim about Claude actually honoring injected prose.
- Previously reported missing-final-newline bug is fixed: unterminated malformed CRITICAL now exits 1 and emits parser plus gate error.
- Previously reported missing-severity warning-only bug is fixed: `- [ ] exposed key` exits 1.
- Current publication counts include archive and critical_accepted; the earlier audit's green accepted-critical badge diagnosis must not be repeated against this commit.
- Current hook includes model warning and differentiates lifecycle opt-outs; hook timeout is 10 seconds.

## Coverage limits

No external receiving-site contract checked (outside assigned scope), no publishing performed, no live Claude/Codex/Agy behavior tests, no GNU/Linux run. Commands' Opus frontmatter and `${CLAUDE_PLUGIN_ROOT}` hook invocation are Claude-specific; shell fixture success alone does not establish support for another agent runtime. Preserve a provider-neutral state/parser core and validate any host adapters independently. Plan/TDD lifecycle design is assigned to other audit lanes.
