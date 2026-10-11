# Independent U03 review

Separate reviewer read actual recovery helper, marked runbook blocks and test implementation. Ran `python3 -m unittest discover -s tests/integration -p test_state_recovery.py -v`: 13 PASS in 11.241 seconds. Tests execute actual shell blocks and cover byte/mode/CRLF/no-final-newline preservation, symlink/internal destinations, source change, copy capacity, partial replacement, post-write validation failure and failed restoration with retained evidence.

Additional independent fault injection: a cp wrapper copies the source then appends a concurrent DECISIONS note. Snapshot exits1, creates no VERIFIED marker, and preserves the new source note. This is a correct detected concurrent change, not a destructive rollback.

## Blocking findings reproduced

1. **Snapshot refreshes the source index.** In a disposable Git repository, commit valid synthetic state, change only PROJECT.md mtime using `os.utime`, hash `.git/index`, then invoke snapshot. Snapshot exits0 but raw index hash changes. Both project and plugin `git status --porcelain=v1 -z` run without disabling optional locks, allowing read-only identity collection to refresh index metadata. Add `GIT_OPTIONAL_LOCKS=0` (including plugin status), and regress unchanged raw index bytes with stat-dirty tracked files. Staged file content was not changed by the reproduction, but the byte-preservation contract is still violated.

2. **Corrupt identity metadata bypasses external destination protection.** After a valid external snapshot, truncate `BACKUP/identity.txt` to zero bytes without changing payload or manifest. Run `staging-copy BACKUP PROJECT/unsafe-stage`: exits0 and creates the stage inside the source project. `verified_backup` checks only payload/manifest and trusts the identity file loop to supply restrictions; missing entries disable them. Require complete, unique supported canonical location metadata and its integrity before destination operations; reject symlinked/missing/corrupt metadata/payload roots. Retain the valid backup and source on rejection. This is corruption handling, not a claim to defend against an attacker who can rewrite every backup integrity record.

Both findings were sent to root with executable reproduction details. Review outcome REQUEST CHANGES; existing 13 passing tests do not cover either counterexample. Re-run these exact cases and fault suite independently after fixes.

The documented writer-quiescence limitation is honest: multi-file apply is not atomic, SIGKILL/power loss can require manual recovery, and no test here qualifies installed-host semantic repair. Linux: NOT RUN by reviewer.

## Independent correction verification

Re-read corrected helper: all project/plugin Git identity queries disable optional locks; backup metadata now requires regular non-symlink files, integrity digests, unique complete canonical location records, payload-root link rejection and recorded project matching before writes.

Independently reran both original counterexamples: stat-dirty source index bytes remain unchanged after snapshot (PASS); truncating identity.txt blocks staging with no internal destination created (PASS). Expanded `python3 -m unittest discover -s tests/integration -p test_state_recovery.py`: **34 PASS in 59.089 seconds**. Both blocking review findings are resolved in the tested candidate. Existing non-atomic/quiescent-writer and offline-only qualifications remain.

Reviewed helper SHA256: `e9e2555c959c9fdbcf5a1d64531ac3772f709a962132302fd6fe1f653bd418b6`.
