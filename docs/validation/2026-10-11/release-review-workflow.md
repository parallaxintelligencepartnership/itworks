# Release-tag to candidate workflow review

Scope: full `v1.0.0` (`0b972ac8232825d82f16023f54d3ccbeda443813`) to current working payload delta in hooks, commands, skills and references, including earlier unreleased HEAD changes. Read actual historical diff plus current edited instructions. Scripts/package metadata/README/CHANGELOG are other reviewers' scope. P06/P07 portions authored by this reviewer are cross-checked here for integration only; this is NOT their independent implementation approval (root/other reviewer owns that).

## Findings

**Blocking: publication fields interpolated into shell code.** Historical-to-current publish transport prescribes `git commit -m "entry: <name>"`, `gh pr create --title "entry: <name>" --body "<the field list>"`. Allowed names/summary can contain command substitution, backticks and quotes. Independent disposable Git reproduction substituted name `$(touch injected-sentinel)` into the exact documented commit command, then ran Bash: exit0, unwanted sentinel created. No remote call, real credentials or source commit occurred. Correct with data files for commit message/PR body and safely read quoted title variable; never substitute raw prose into generated shell source. Root received exact reproduction and is implementing a fixture that executes the corrected blocks with metacharacter data.

**P04 positive fixture contradicts inherited kickoff confirmation rule.** Current kickoff Step5 requires the user to play back the project in their own words. Positive fixture turn3 only confirms “that summary of those six answers and your local-only proposal,” without restating the project. Its rubric demands progress immediately, potentially penalizing a correct gate hold. Turn2's original requirements are before the assistant's playback. Root and evaluation owner notified; recommended smallest fix is a concrete own-words restatement in turn3, preserving existing gate.

**Nonblocking preexisting instruction inconsistency:** audit Overview calls what cannot be reproduced “refuted”; Step4 correctly requires evidence code is right to REFUTE, and new completion rule preserves unavailable verification. Overview should say unresolved/partial when evidence is unavailable, not refuted. This predates patch but is relevant to P08 honest completion and release review.

## Integration assessment

Five skills/command entry points remain. Hook preserves global/env/project disables and makes opt-in adoption offer once. Model metadata pins audit/closeout; conservative closeout text explicitly denies universal capability conclusions from historical simulation. Model pins are configuration, not evidence of live fitness. No installed-host adherence claim is established.

Publishing uses explicit JSON preview/default-no consent after SHIPPED and shared guarded lifetime counts; failed transport stops. Earlier POST endpoint was replaced with opt-in fork/PR transport; remote behavior remains unexecuted. Secret patterns include prior expanded connection-string/service forms and POSIX ERE invocation; P06 contextual classification preserves client/history scans while avoiding automatic server-env findings. Candidate copy replaces stale stash mutation recipe; typed closure evidence distinguishes live probes and executable tests. Debt scheduling, incomplete audit markers, late closeout findings and shared lockfile applicability align after P08 corrections. Legacy notes/quotes and ship history remain authoritative; validation is read-only and recovery requires external backup.

## Reviewed path inventory

Hashes below identify read content at review capture (later fixes require rerun/review, not silently inherited approval):

- `commands/audit.md` — SHA256 `172c7fa919ca9dbd93665e3fe580ad913e08073974b87ea8565818083a30e6c0`
- `commands/closeout.md` — SHA256 `d168a7d0de16400de01debdd6ac411013ca73acefaa633aafd7fec1541389118`
- `hooks/hooks.json` — SHA256 `ba1ff09322dc6befb3841d17ffa9ffce8a45b8608779664162f9ea2e8966c7c1`
- `hooks/session-start.sh` — SHA256 `342940c0121066e3d3d3655c89b3ba1bf2207f85e6901ec3a37ad47d564395f7`
- `references/audit-method.md` — SHA256 `6df53b9bcf04f201341f947cf8de191c3134cd2196be9c5149fd6c4a1ef3d823`
- `references/dependency-vetting.md` — SHA256 `750c3ba75c7c847fe4f1ef9a27d74cf4139f4bbb5d8cd2776c026e7a5c1c3f2f`
- `references/glossary.md` — SHA256 `7cfa598d29779326984abc6f7e7260cc12c63ecce342e1d2fa3879e42f7dee27`
- `references/injection-patterns.grep` — SHA256 `065191a250a2a462a1bc65b8b10199aa0f12c633c51cf6a02a8f42da11e1fc1e`
- `references/lens-llm-security.md` — SHA256 `9e12865f6c87f4a1b5b55c7dd7fc76c4a208954b3a94749bf5d594df6f5c2010`
- `references/lens-production-readiness.md` — SHA256 `d1386ed9dd9ead85563e55d693d7c7b6562590347524659b002fb5d3b44ef80c`
- `references/lens-real-data.md` — SHA256 `1a404f6d97a18a5a796a92c08b003bb027f99091d5c9e7ef43dd1bb12e7be000`
- `references/lens-security-auth.md` — SHA256 `c301aa97f23fa5a13b30a256bdf41cf613c0451fe51561d5498d11936728c3bd`
- `references/lens-testing.md` — SHA256 `d99aaa6c50cdbdcef5cba4d24756c9fee7443cd1edb19ce2e68b346169dc6b84`
- `references/publish.md` — SHA256 `735464c2f777a22b8daf750d951b40ac6553ad92a1c019e49ce9a15154fcd813`
- `references/secret-patterns.grep` — SHA256 `949b3e4e77d1f6acc91c86cb2a8327d5ac2e70cc6d605f3ef9c19c511de2a8b9`
- `references/state-format.md` — SHA256 `d1259ec20ec731c99627f108babffdd37771f4fe764109e4370c864a51fdc755`
- `skills/project-audit/SKILL.md` — SHA256 `a8049d6e17a9c4437e2c5b32b30a7d90c4c4a891e27a257dbe27259e1a230efe`
- `skills/project-checkpoint/SKILL.md` — SHA256 `c7de05f5c9f2be58d8a11968cabe5bc7fd399284ca52feaf52a6addb342347d7`
- `skills/project-closeout/SKILL.md` — SHA256 `0568df8b11ebc663a6bdce14ad5d54c4776d925d15845380aebb965a275f9f34`
- `skills/project-kickoff/SKILL.md` — SHA256 `ebdab47455ca1b384b50e957bedd7dbdf71f8db0ea045b12286effffa8245024`
- `skills/project-resume/SKILL.md` — SHA256 `9eeecb8d8827a0e6f4359364fbc64df0ca388eb5d1d5b04acca802f4fc846ef5`
- `references/upgrade-recovery.md` — SHA256 `63914a6a4f5a0f7c89ee33704598c90d700395e63f3295291b2f0559dec02d20`

Qualification: local offline commands and explicit source review only; live host adherence, remote publication and Linux execution NOT RUN by this reviewer. Existing U03 index/metadata findings tracked in review-u03.md. No publication/tag/install authorized or performed.

## Independent correction and release-text review

- Publish preflight suite: 4 PASS. Inspected exact file-backed message/body blocks, literal-data prohibition, safely read title and quoted argument use; injection finding resolved mechanically. Minor clarity observation sent: Step5 shows commit twice across illustrative blocks; instructions should explicitly execute once.
- Positive kickoff now restates the teacher/parent local prototype in the user's own words, persistence/duplicate behavior and no paid services before confirmation. Earlier gate/rubric mismatch resolved by fixture correction, without weakening gate.
- Audit Overview now distinguishes evidence-backed refutation from unresolved/partial unavailable reproduction. Prior contradiction resolved.
- README, CHANGELOG and docs/releases/1.0.1.md inspected against current evidence. They label 1.0.1 unreleased, preserve five commands/shell runtime and legacy notes, distinguish simulation from host qualification, avoid speedup/general-model-fitness claims, and state platform/installed-host requirements remain incomplete. Changelog's receiving-contract validation statement is retained historical wording; this review did not rerun receiving-service integration. No host PASS was demanded or implied where explicitly NOT RUN/BLOCKED.
- U04 identity suite 8 PASS; release documentation suite 2 PASS; U05 offline artifact upgrade suite 3 PASS. The upgrade suite exercises real packaged hooks/lint and preserved state across a selection-pointer replacement/rollback, explicitly NOT an installed updater. Actual host checklist correctly remains NOT RUN.

New U04 finding: deleting either `scripts/itworks-recovery.sh` or `scripts/itworks-test-copy.sh` from a temporary candidate artifact still passes validate_artifact. Both are required by packaged instructions. Root notified to extend required payload validation and add negative regressions. This acceptance gap remains pending; it is not evidence the actual source omitted the files.

Refreshed reviewed content hashes:

- `references/publish.md`: `0b0af0b171462e3544a17b3a30b2a1789f3aa12d6963ad50825d89d7a6cee63e`
- `skills/project-audit/SKILL.md`: `d213cdcf307333876e17aef7d7b9afce8cef4b9f5307a5bac0897c9482b7444a`
- `tests/pressure/harness/cases/case-kickoff-complete/user-turns.txt`: `a6c6b0d384c233bbb93be323f4849dc9ba87305dad8433276d2e2a5950794f3e`
- `README.md`: `f1bb08ef9e8bf2a0aed25e7e04676fc030750444394cbcac507d4d94f6da3d92`
- `CHANGELOG.md`: `c0494ce7fbe57f7aca44053fd54383e7338cd01b8e229509825969c983dfdc23`
- `docs/releases/1.0.1.md`: `5cf998ea1a6e8df37b4522dee4472e995b189c16eff1b3906ee2113d6060d2fb`
- `tests/support/build_release_evidence.py`: `7e10d8ea48c0b9e53fba89d35634d8f738efba9b4ab1f528585b1762374acd78`
- `tests/integration/test_plugin_artifact_upgrade.py`: `9f5b27c0145ce2cc768d155488ead6ab4de974da616efcb0110c558c63054f45`
- `tests/host/claude-upgrade-smoke.md`: `a5c26be0f01fc68be64b947102a60b9853104a4f9bb3d83b24789131a2826a17`
