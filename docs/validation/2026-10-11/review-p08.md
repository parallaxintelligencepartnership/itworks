# Independent P08 review

Separate reviewer inspected checkpoint debt selection/update, audit completion marker, resume incomplete replay, closeout applicability/checklist/reckoning/gate ordering, shared lockfile table and tests/fixtures. Executed actual commands:

- `python3 -m unittest discover -s tests/unit -p test_workflow_traces.py`: 4 PASS.
- `python3 -m unittest discover -s tests/integration -p test_closeout_trace.py`: 3 PASS.

Manual independent trace: debts 0,0,3,3,3 select real-data/testing, production becomes4; next selects production before new contextual security. Nonapplicable LLM remains0. Step5 matches Step2. Partial audit preserves marker and resume reports incomplete/due. Closeout now observes applicability, then sweeps/history/checklist before recording/reckoning; late findings explicitly return before gate/ship. Dependency table includes Cargo and composer and disallows cross-ecosystem lock substitution.

No instruction contradiction reproduced in those cases. Two acceptance coverage gaps remain before full offline acceptance:

1. Lockfile unit check is a developer hardcoded dictionary/set intersection; it never creates a tracked Cargo.lock or executes the prescribed git query. Add a disposable tracked/untracked fixture using the real command to validate the claimed mechanical applicability evidence.
2. Audit oracle advances solely on scope subset of read files. Revised audit instructions additionally require verification dispositions and hold incomplete for required unavailable verification. Add a case with all files read but required verification unavailable, distinct from a declared-before-review external exclusion.

These gaps were reported to root, not silently counted as PASS. Full live behavior remains NOT RUN; trace models do not prove a host follows instructions. P06/P07 post-implementation historical sensitivity checks remain an explicit regression-first process deviation; review cannot retroactively turn those into pre-fix TDD.

## Independent acceptance-gap verification

Root added the required-unavailable-verification audit fixture and updated oracle to retain old marker, distinct from predeclared external exclusions. Added actual disposable Git check extracted from shared lockfile document: Cargo.lock tracked+committed passes; unrelated npm lock does not satisfy composer; staged-only composer lock fails until committed. Reviewer independently reran workflow unit suite (4 PASS) and closeout integration suite (now 4 PASS), and inspected the new fixture/actual commands. Both reported offline coverage gaps are resolved. This does not turn developer traces into live behavior qualification.
