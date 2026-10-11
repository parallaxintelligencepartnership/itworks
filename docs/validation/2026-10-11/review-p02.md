# Independent P02 review

Reviewer: separate P01 agent, not the parser implementer. Reviewed actual scripts and tests, ran real commands in disposable synthetic projects. No production edits. Local `/bin/bash` is 3.2.57 arm64-apple-darwin26; awk is `/usr/bin/awk`. Linux: NOT RUN.

`python3 -m unittest discover -s tests/unit -p test_state_parser.py`: 10 PASS. Additional counterexamples below were run via shared `build_state` and real `/bin/bash scripts/itworks-state.sh OP TEMP_ROOT`; no mocking of parser.

## Findings requiring correction

1. **Empty SHIPPED marker skips existing-file cross check.** Build default state, set `SHIPPED.md` to zero bytes, set REVIEWS to `- [ ] CRITICAL | testing | missing test | Evidence to close: test`. `check` returns 0 and `SUMMARY 0 0 0`. The wrapper enumerates SHIPPED, but awk sets `seen` only when a record exists. Existing lint checks file existence, so this regresses canonical critical/ship detection. Required: preserve presence independently of line count; regression must assert exit1 and untouched ship bytes.

2. **Embedded closure delimiter manufactures a fixed count.** Without SHIPPED, REVIEWS contains `- [x] IMPORTANT | testing | command `x | Closed 2026-10-11: demo` is not evidence | Evidence to close: real check`. `counts` returns 0 and fixed=1/found=1, with no warning. The parser accepts the first closure-looking delimiter inside description and swallows the actual final evidence field. Required: select genuine field boundaries; this case must warn for missing terminal closure and fixed=0. Preserve pipe-containing description prose.

3. **Malformed critical closure leaves gate eligible.** Without SHIPPED, REVIEWS contains `- [x] CRITICAL | testing | missing test | Closed 2026-10-11:`. `gate` returns 0 with `W_CLOSURE_MISSING`. This may belong to pending P03 strict evidence gating; ordinary `check` warning is appropriate for historical drift, but strict gate must not authorize malformed critical evidence. Exact acceptance linkage is explicitly pending P03 and was not counted as a new P02 regression.

## Other observations

Protocol emits only fixed diagnostic text, and privacy test passes. Shell arrays are Bash 3.2 compatible; inspected awk does not use GNU-only capture arrays/gensub. Archive names with tab/CR/LF and symlinks are rejected, and quoted filenames begin `./`, avoiding awk assignment operands. Existing tests cover root spaces/backslash/equals and CRLF. This inspection does not establish Linux runtime behavior or finish P03 acceptance semantics.

Review outcome: REQUEST CHANGES for findings 1 and 2; carry finding 3 into strict-gate acceptance. Root implementer was notified with the exact counterexamples. Fixes require independent rerun before acceptance.

## Independent fix verification

After root implementation corrections, the same reviewer reran all three exact counterexamples with actual current scripts:

- Empty SHIPPED + open CRITICAL: check exit1, E_SHIPPED_CRITICAL, untouched fixture.
- Embedded closure plus terminal Evidence-to-close: counts exit0, W_CLOSURE_MISSING, found1/fixed0.
- Empty critical closure: gate exit2, B_CLOSURE_MISSING plus warning.

All three reported findings are now resolved in these independently reproduced cases. This does not supersede pending P03 broader linkage review or remote Linux qualification.
