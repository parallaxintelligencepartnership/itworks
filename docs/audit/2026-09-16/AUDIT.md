# Audit 2026-09-16

## Scope

Audit tier review, target `0b972ac`. Two lanes: lane P (plugin lifecycle) and lane Q (runbooks and contract). Each lane got one Opus reviewer and one independent Opus verifier. Every finding was reproduced either by a quoted passage plus a trace through the skill/hook text, or by a command run on a planted fixture.

Not covered: the pressure harness was not run for this audit. Harness cases 7 and 8 are written, not run. GNU grep and bash 5 were not available on the review machine.

## Findings

- [x] CRITICAL | production-readiness | Gates are known to fail on Sonnet and nothing at runtime says so (README.md) | Closed 2026-09-16: e5f7619
- [x] CRITICAL | production-readiness | An accepted CRITICAL publishes as `critical_open: 0`, a green badge (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] CRITICAL | security-auth | The SQL-injection grep's `+` branch is dead; string concatenation never matches (references/lens-security-auth.md) | Closed 2026-09-16: bd2ebaa
- [x] IMPORTANT | production-readiness | `references/...` pointers do not resolve from a skill's base directory, in all five skills (skills/*/SKILL.md) | Closed 2026-09-16: 265fb86
- [x] IMPORTANT | production-readiness | The hook says two "not now"s turn off any skill, but closeout has no such opt-out (hooks/session-start.sh) | Closed 2026-09-16: 8031811
- [x] IMPORTANT | production-readiness | Hook and README tell the agent to leave un-instrumented projects alone, contradicting kickoff's own trigger and adoption mode (hooks/session-start.sh) | Closed 2026-09-16: 5182e27
- [x] IMPORTANT | production-readiness | Checkpoint Step 3's readable lens list omits `lens-llm-security.md`, which Step 2 can select (skills/project-checkpoint/SKILL.md) | Closed 2026-09-16: 5f31125
- [x] IMPORTANT | production-readiness | Adoption mode never runs Step 4, so an adopted project gets no env/pin/spend-cap/test-harness setup (skills/project-kickoff/SKILL.md) | Closed 2026-09-16: af26387
- [x] IMPORTANT | production-readiness | Closeout never restates checkpoint's "not verified live" rule, so the auth probe can be satisfied without running (skills/project-closeout/SKILL.md) | Closed 2026-09-16: 6e89016
- [x] IMPORTANT | production-readiness | "if any dependency was never vetted" is unanswerable; no state file records what was vetted (skills/project-closeout/SKILL.md) | Closed 2026-09-16: 27f344a
- [x] IMPORTANT | production-readiness | The publish curl cannot detect a non-2xx and can hang the session (skills/project-closeout/SKILL.md) | Closed 2026-09-16: 4360ef8
- [x] IMPORTANT | production-readiness | publish.md's "Not sent" list contradicts what the `summary` field actually is (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] IMPORTANT | production-readiness | Resume rebuild can silently downgrade an open CRITICAL to ADVISORY (skills/project-resume/SKILL.md) | Closed 2026-09-16: c1c28c7
- [x] IMPORTANT | production-readiness | The closeout HARD-GATE gates deploy steps on the sweep completing, not on the reckoning resolving (skills/project-closeout/SKILL.md) | Closed 2026-09-16: 934edba
- [x] IMPORTANT | production-readiness | Backup, spend-cap and role checks are gated on PROJECT.md fields nothing re-asks (references/lens-production-readiness.md) | Closed 2026-09-16: 660d38c
- [x] ADVISORY | production-readiness | Confirmation standard stated two ways ("own words" vs "explicit confirmation") (skills/project-kickoff/SKILL.md) | Closed 2026-09-16: 4567101
- [x] ADVISORY | production-readiness | hooks.json declares no `timeout` (hooks/hooks.json) | Closed 2026-09-16: f1d0195
- [x] ADVISORY | production-readiness | The publish payload file has no specified location (skills/project-closeout/SKILL.md) | Closed 2026-09-16: c16e2d3
- [x] ADVISORY | production-readiness | publish.md cites a `docs/SPEC.md` that does not exist in this repo (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] ADVISORY | production-readiness | Two glossary cards named by runbooks do not exist (references/glossary.md) | Closed 2026-09-16: d5855b7
- [x] ADVISORY | production-readiness | The one-card-per-message cap is scoped to the interview only, not Step 4 (skills/project-kickoff/SKILL.md) | Closed 2026-09-16: 4567101
- [x] IMPORTANT | security-auth | Four inspect commands abort under the stock macOS shell (unquoted `--include` globs) (references/lens-security-auth.md) | Closed 2026-09-16: 4ee84be
- [x] IMPORTANT | security-auth | `src/ app/` is hardcoded; llm-security self-gates off on a project that does call an LLM (references/lens-llm-security.md) | Closed 2026-09-16: f7cc9bc
- [x] IMPORTANT | security-auth | No inspect step greps the working tree for secrets outside client dirs (references/lens-security-auth.md) | Closed 2026-09-16: a9caa74
- [x] IMPORTANT | security-auth | publish.md's summary rule has no length cap and produces a 400 against the site (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] IMPORTANT | security-auth | publish.md's repo_url rule sends an SSH origin, which the validator rejects (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] IMPORTANT | security-auth | publish.md's audit_date rule sends `<date> @<sha>`, which the validator rejects (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] IMPORTANT | security-auth | itworks-lint.sh silently skips the last line of REVIEWS.md with no trailing newline (scripts/itworks-lint.sh) | Closed 2026-09-16: 5028537
- [x] IMPORTANT | security-auth | The lint downgrades to a warning what state-format.md calls corruption (an open checkbox with no severity) (scripts/itworks-lint.sh) | Closed 2026-09-16: 17c75c9
- [x] ADVISORY | security-auth | secret-patterns.grep misses modern shapes: DB URL with password, AWS secret key, Discord and Telegram tokens (references/secret-patterns.grep) | Closed 2026-09-16: f377fde
- [x] ADVISORY | security-auth | publish.md's "Not sent" promise is a promise about PROJECT.md, not about the transport (references/publish.md) | Closed 2026-09-16: 4360ef8
- [x] ADVISORY | security-auth | The found/fixed counts shrink after archiving (references/publish.md) | Closed 2026-09-16: d0e6143
- [x] ADVISORY | security-auth | Severity is not decidable from the text in four places (references/lens-*.md) | Closed 2026-09-16: 399ca7f
- [x] ADVISORY | security-auth | Scenarios are stale on the lens count (four instead of five) (tests/scenarios/*.md) | Closed 2026-09-16: 26b9540
- [x] ADVISORY | security-auth | Pressure-tests case 7 (audit) has no harness case; resume and audit are untested by the harness (tests/pressure/pressure-tests.md) | Closed 2026-09-16: d02d650
- [x] ADVISORY | security-auth | `dev vs production data` is a guided card with no glossary entry (references/lens-real-data.md) | Closed 2026-09-16: d5855b7
- [x] ADVISORY | security-auth | SHIPPED.md's shape is enforced by the lint but defined nowhere in state-format.md (scripts/itworks-lint.sh) | Closed 2026-09-16: b27bc84

Not included above: lane P's A7 (the hook injects `plugin.json`'s version string verbatim into the prompt) was verified CONFIRMED as accurate but also CONFIRMED as not a defect (informational only; `plugin_root` derives from `BASH_SOURCE`, never from project content). It is left out of this list because it names no fix to close.

### Refuted

- Lane Q, within Q-10 (secret pattern recall): a *bare* 40-hex token pattern cannot be added safely, the verifier's benign control (`build sha 5a87acd...deadbeef1234`) shows a 40-hex string is also a full git SHA-1, so an unprefixed pattern would false-positive on commit ids in prose. The fix instead added four other shapes and left the bare-hex case out.

### Coverage gaps

- The pressure harness was not run for this audit.
- Harness cases 7 and 8 are written, not run.
- GNU grep and bash 5 were not available on the review machine.
