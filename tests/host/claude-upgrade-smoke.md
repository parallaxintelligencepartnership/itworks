# Claude upgrade smoke — NOT RUN

This is an operator checklist, not a record of completed qualification. Existing
user plugins must not be modified. Run only after explicit authorization in a
disposable OS account or VM, with a dedicated authorized account for model calls.
Use a task-specific CLAUDE_CONFIG_DIR; never redefine HOME or copy production
credentials. Record managed settings that remain in force. Configuration isolation
alone is not an OS security boundary. No budget or account has been provisioned.

Record before work:

- OS/account isolation, CLI version and exact candidate commit/archive SHA-256.
- Baseline release `0b972ac8232825d82f16023f54d3ccbeda443813`, version 1.0.0.
- Candidate identity from `build_release_evidence.py`, manifest and file hashes.
- Source type: local in-place OR cache-backed Git marketplace; separate records.
- Finite command deadlines: help/metadata 60s; install/update 120s. Retain stdout,
  stderr, status, elapsed time, timeout classification. Never poll indefinitely.

First record `claude --version`, `claude plugin --help`, `claude plugin marketplace
--help`, and install/update/uninstall help. Verify flags against that pinned CLI
and current official [discovery documentation](https://code.claude.com/docs/en/discover-plugins),
[settings documentation](https://code.claude.com/docs/en/settings), and
[plugin reference](https://code.claude.com/docs/en/plugins-reference). These links
are starting points, not evidence the pinned commands were tested. Unsupported
flags/isolation/network/authentication make the cell BLOCKED before mutation.

Only after help confirms syntax and authorization applies, add the disposable local
release marketplace with `claude plugin marketplace add <absolute-path>` and install
`claude plugin install itworks@itworks --scope user`. Record reported location,
version, and loaded file hashes; compare with the exact baseline artifact. Start a
fresh host session and verify version-bearing hook output and all five commands.
A model invocation, if needed, needs its own explicit budget and captured effective
model; do not quietly charge it to the deterministic suite.

Replace the disposable marketplace source with the verified candidate artifact.
If supported by recorded help, use `claude plugin marketplace update itworks` then
`claude plugin update itworks@itworks --scope user`. Record outputs and actual
installed/cache hashes. Begin a fresh session, verify candidate hook identity and
five commands, then run installed candidate lint against copied U01 fixtures.
Compare complete project-state hashes before/after. Any mixed or stale payload is
FAIL. A successful command without matching loaded bytes is not PASS.

Qualify cache-backed update separately using a help/documentation-supported local
Git marketplace/file remote in the disposable account. Local-path loading can run
in place; it does not prove cached update. Unsupported cache-backed transport stays
NOT RUN, with no corresponding support claim.

Rollback uses another disposable config and exact released artifact, with help-
supported uninstall/reinstall only if necessary; do not invent arbitrary downgrade
support for `plugin update`. Retain candidate blocked-state reports externally and
verify state bytes and old artifact hashes. Old false passes do not clear risks.

| Cell | Current status | Required evidence |
|---|---|---|
| Pinned CLI/help and isolated settings | NOT RUN | Version/help/settings capture |
| Local source old install | NOT RUN | Installed bytes and new-session identity |
| Local source candidate update | NOT RUN | Exact qualified candidate hashes |
| Cache-backed old→candidate update | NOT RUN | Loaded cache hashes and fresh session |
| Rollback | NOT RUN | Old loaded hashes, preserved state/patch diagnoses |
| Live model repair (if separately requested) | NOT RUN | Budget, effective model, independent behavioral result |

Store evidence outside the candidate payload. Each record names artifact SHA,
source type, CLI, command, status, output hashes, reviewer, limitations, and any
requested/effective model when observed. Any packaged change invalidates affected
artifact-specific smoke and requires a new candidate association and rerun.
