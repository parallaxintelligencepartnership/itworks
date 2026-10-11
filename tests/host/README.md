# Explicit host qualification

Default unit/integration suites do not invoke Claude or install/update plugins.
`test_plugin_artifact_upgrade.py` simulates package replacement with trusted local
archives; its selection pointer is a test variable, not a Claude cache pointer.
Neither successful offline tests nor a source hook run qualifies an installed host.

Use [claude-upgrade-smoke.md](claude-upgrade-smoke.md) only with an explicitly
provisioned disposable account/VM and authorized installation/model budget.
Status for 1.0.1: run on 2026-10-11, see
[the release qualification record](../../docs/validation/2026-10-11/release-qualification.md). Local-path and cache-backed installs are separate
cells; unsupported isolation, authentication, or transport is BLOCKED, not PASS.
No Codex/Antigravity installed-plugin compatibility claim follows from this work.
