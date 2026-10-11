# Upgrade recovery: preserve state before repair

Lint and version upgrades are read-only with respect to project state. A warning
about v1/v2 omissions does not require a rebuild. Keep original severity, findings,
accepted words, closure evidence, and SHIPPED history. Old reader success never
cancels a corrected parser's blocked result. Missing or ambiguous acceptance stays
unresolved until the ordinary workflow obtains clarification; never invent words
or downgrade severity to obtain a pass.

Before an authorized repair, pause all writers. Set the following absolute paths:
`PROJECT` (project), `PLUGIN` (identified candidate artifact), `INSTALLED_CACHE`
(actual installed-plugin cache root), `BACKUP` (a NEW external recovery directory),
`STAGING` (a NEW separate staging directory), and `RESTORED` (a NEW empty-location
restore target). Their parent directories must exist. Recovery destinations must
be outside project/plugin/cache, including resolved symlinks. Do not use a temporary
CI directory for real user recovery. Keep the recovery point **at least 30 days and
two verified subsequent work sessions, whichever is longer**. Backup roots use
restrictive permissions; state may contain private notes.

A `.itworks` symlink or any nested link/special file is BLOCKED, even if the target
appears local. Resolve its intended target explicitly before repair; never follow
an escaping link into another project. Unsupported control characters in paths
are also blocked. All commands below call the same shell helper exercised by the
integration tests, with SHA-256 utilities selected explicitly and no Python runtime.

<!-- recovery:snapshot -->
```sh
bash "$PLUGIN/scripts/itworks-recovery.sh" snapshot "$PROJECT" "$BACKUP" "$PLUGIN" "$INSTALLED_CACHE"
```

This records source Git HEAD/status where available, plugin manifest identity,
project/plugin/cache locations, complete state paths/modes/hashes including
SHIPPED, and a verified independent copy. Identity and state manifests have integrity
digests; missing, duplicated, changed, or symlinked metadata blocks all recovery.
Verify/apply also require the project root recorded at snapshot time. Restoration
to a new empty directory remains available if the original source is unavailable.
Git identity reads disable optional index locks and filesystem-monitor hooks.
Configured Git clean/process filters are rejected before status inspection because
status can execute those filters. This includes globally configured filters even
when their attributes are not obviously relevant; use a separately reviewed
snapshot method instead of disabling user configuration. Required hash and mode
utilities must return valid results; failure never establishes verified recovery. A failed or existing backup is never
overwritten. Preserve failed copies for diagnosis. A backup is usable only after
its VERIFIED marker exists and its manifest is rechecked.

<!-- recovery:staging-copy -->
```sh
bash "$PLUGIN/scripts/itworks-recovery.sh" staging-copy "$BACKUP" "$STAGING"
```

Edit staging only. For additive drift, add only absent supported fields, obtain
MAP facts from the project, and retain original notes. Do not replace whole notes
with templates. For an interpretive rewrite, show the exact diff and unresolved
records and use the existing one-shot resume confirmation. If meaning cannot be
preserved, retain malformed text verbatim as unresolved evidence and stop for
review. The helper does not infer or perform semantic repairs. Check staging with
`bash "$PLUGIN/scripts/itworks-lint.sh" "$STAGING"` and strict `gate` where the
next release transition requires it. Lint eligibility alone is not release proof.

<!-- recovery:verify-before-write -->
```sh
bash "$PLUGIN/scripts/itworks-recovery.sh" verify-before-write "$PROJECT" "$BACKUP"
```

Changed source means abort and reconcile both versions, never overwrite newer
notes. After reviewing the staged diff and stopping other writers, the optional
`apply PROJECT BACKUP STAGING PLUGIN` operation validates staging, rehearses restore
into a fresh external directory, rehashes source immediately before writing, and
copies staged files deterministically before revalidation. It rejects deletion
of original state files. Multiple files are **not atomic**. No mechanism here
prevents an uncooperative writer after the final comparison; keep writers paused.
If any replacement or final check fails, it preserves the failed state externally
and restores verified original bytes. If restoration also fails, it stops, retains
backup/staging/restore/failed paths, and requires manual recovery. Do not retry in
a loop. The helper never deletes backup or candidate evidence.

<!-- recovery:restore-to-empty-directory -->
```sh
bash "$PLUGIN/scripts/itworks-recovery.sh" restore-to-empty "$BACKUP" "$RESTORED"
```

This restores into a new directory and verifies it; it never overwrites existing
notes. Inspect the restored copy before any manual replacement, retain failed
state separately, and only restore to the project while its writers are paused.
For a failure before the first write, project bytes remain unchanged. For a
mid-write or post-write validation failure, automatic rollback must match the
original complete manifest. A restore failure is BLOCKED manual recovery, not
permission to destroy the remaining evidence. Retain corrected parser diagnoses
externally through package rollback: the old validator can falsely accept them.

The offline suite injects copy failures before and during replacement, concurrency,
and restore failure against synthetic data, executing these exact marked blocks.
This does not prove that a live model will preserve meaning in an interpretive
repair, and does not qualify installed-host updating.
