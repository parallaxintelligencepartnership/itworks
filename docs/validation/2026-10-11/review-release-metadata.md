# Independent release metadata and historical-delta review

Reviewer: compatibility delegate, independent of root's runtime parser and U06
notes. Scope includes the full released→audited HEAD name list and historical diff
outside the separately assigned skill/reference/hook/command/test lanes. Byte
identities and exact reviewed paths are in `review-release-metadata-hashes.json`.
This working-tree review must be associated with final immutable candidate hashes.
No self-certification of my U01–U05 helper implementation is implied; root/other
reviewers assess those files independently.

Read current README, CHANGELOG, plugin and marketplace JSON, ignore policy,
candidate advisory/release checklist, and current shell parser/renderer. Reviewed
historical lint diff, historical audit summary and report/verification scope,
verdicts and selected evidence passages. September reports remain unchanged
historical artifacts, not reexecuted September audits. Their claimed model limits
are corrected/contextualized by U06, not silently rewritten. The immutable release
already documented v3; audited HEAD still identified itself as 1.0.0, so a new
version is necessary. Candidate manifest1.0.1 agrees with notes; marketplace uses
one relative-root itworks entry and no duplicate version authority.

Historical lint fixes for unterminated lines and unchecked severity violations
are preserved by the shared parser. Parser implementation is read-only shell/awk,
canonical active findings affect gates, archive aggregation is counts-only, and
error/blocked modes cannot emit publishable count payloads. Current maintained
parser tests: 32 PASS; Bash syntax on state/lint wrappers: PASS. No new independent
behavioral defect found in this scope. Existing independent parser review records
and U01/U02 fixture evidence remain separate acceptance sources.

U06 documentation correctly separates offline tests, text simulation and installed
host qualification; no speedup or universal model reliability claim is made. It
preserves accepted wording/SHIPPED history and links external recovery before any
repair. Source-type qualification and actual loaded content are explicit. Current
release-doc link/version tests: 2 PASS. The host checklist is a procedure, not
completed qualification; Linux, real hosts, workflow behavior and other required
matrix gaps still block release.

Two prose corrections requested from root before freeze:

1. README opening “makes sure what gets built is real” implies a guarantee despite
   the later model-guidance caveat; describe its intended guidance instead.
2. Prior Unreleased CHANGELOG claim that receiver derivations “are validated”
   should identify the historical September check, avoiding a claim of current
   receiver compatibility without testing that external product today.

Packaging notes: archive includes historical audit documentation and test fixtures,
including old local paths/host references and explicitly synthetic samples; do not
mistake those historical reports for new supported behavior or fresh host evidence.
No new credentials or external service interactions were discovered/performed in
this review. Generic plugin marketing text is not an authorization to publish.
No additional missing-runtime packaging requirement found beyond U04's previously
reproduced and fixed command-wrapper/marketplace/helper omissions.

Prose follow-up: root revised the README opening to describe added checks and
reworded the receiver-derivation entry as a historical September review. Re-read
both changes; the two requested clarifications are resolved. Updated the two file
hashes in the review association record. No installed-host qualification implied.
