# Review: itworks 1.1.0 calibration package

Reviewer: Eagle Eye (read-only, one pass: design verify + itworks lens)
Target: commit 72221e3 ("calibration: review modes, reachability, PLAUSIBLE, gap sweeps, clean fixture (1.1.0 candidate)").
Note: HEAD moved to b8045ff ("plan: review-calibration progress") during the review; `git diff --stat 72221e3 HEAD` shows only docs/plans/review-calibration.md changed, so every file in scope is byte-identical at both commits. Line numbers below are from 72221e3.
Host: `uname -m` = arm64 (no architecture claims made).
Brief: no AGENTS.md, CLAUDE.md or DECISIONS.md at repo root. Requirements read from docs/plans/review-calibration.md (approval line 3: PLAUSIBLE, ADVISORY as a count, 1.1.0, recurrence loop kept).

Counts: CRITICAL 2, IMPORTANT 4, ADVISORY 4.

---

## Findings

### F1. CRITICAL: the checkpoint do-not-flag rule suppresses CRITICALs that the checkpoint's own tree-wide runbook steps find

- Where: references/review-calibration.md:52-56
  > "Checked before a finding is emitted, at every tier: 1. **Outside the scope.** At checkpoint, code the diff did not touch. ... Say "not covered"; do not report it as a finding of this review."
- Conflicts with surviving text:
  - references/lens-security-auth.md step 1: "Scan explicit client/served directories and built bundles, then the remaining working tree" and step 4: "List every route or page that should require login ... hit each WITHOUT a token" (both run at checkpoint when security-auth is selected; neither is limited to the diff).
  - skills/project-audit/SKILL.md:38: "a checkpoint or closeout finds a CRITICAL in code that no recent diff touched" (the surviving text expects checkpoints to record such CRITICALs).
  - skills/project-checkpoint/SKILL.md:54: "Do not improvise checks the runbook does not call for; do not skip ones it does." and :13 "A CRITICAL finding blocks new feature work".
- Trigger: a checkpoint on a diff that touches only `src/login.js` selects security-auth. The secret-candidate scan reports a tracked live key in `src/legacy/config.js:3`, a file the diff did not touch; or step 4's curl returns 200 with data on a pre-existing protected route.
- Wrong outcome: a model following the do-not-flag list, which says it applies "at every tier" and "before a finding is emitted", records "not covered" instead of a CRITICAL. Nothing is written to REVIEWS.md, so the checkpoint HARD-GATE never engages and feature work continues on a known leak until closeout. Before 1.1.0 the same scan output was a CRITICAL blocker. This changes what the checkpoint gate does.
- Reproduce: read the do-not-flag item 1 alongside lens-security-auth steps 1 and 4 as the checkpoint skill's Step 3 runs them; nothing in the new text says that runbook command output over the tree is exempt from "code the diff did not touch".
- Fix direction (not prescriptive): scope item 1 to reasoning about logic outside the diff, and state that runbook command output is in scope wherever the runbook points it.

### F2. CRITICAL: Step 3b drops a suspicion with no "reachable by" before any verifier sees it, contradicting the calibration reference and the release note

- Where: skills/project-audit/SKILL.md:91
  > "Drop any suspicion that has no trigger or no "reachable by" (record the count; it is a fact about the reviewer, not a finding)."
  and references/audit-method.md:119 "drops any with no trigger or no "reachable by" (counted, not reported)".
- Conflicts with: references/review-calibration.md:47-48
  > "A suspicion with no trigger is not passed on. A finding with no "reachable by" is not written to REVIEWS.md."
  (here reachability is checked when a finding is written, after verification, not when a suspicion is passed on) and docs/releases/1.1.0.md:30-31 "A suspicion with no trigger is dropped at dedup; a finding with no "reachable by" is not written." The plan (docs/plans/review-calibration.md, step 2) only says "drop any without [a nameable trigger]".
- Trigger: a lane reviewer reports "shiftpay/pay.py:23 under-pays a shift of N minutes at rate R; input (N, R); wrong outcome: 1 cent short" and forgets the "reachable by" line. Reviewers omit fields, and the Step 3 completion check (line 87) verifies only the last line and the coverage list, not the fields.
- Wrong outcome: the orchestrator follows Step 3b and drops it as a count. A stored-money defect, CRITICAL under the exception at audit-method.md:123, never reaches a verifier and never reaches REVIEWS.md. "every suspicion has a recorded verification disposition" (line 119) is then satisfied vacuously, the audit completes, and last_audit advances. This breaks invariant 3: a CRITICAL skips the verifier because a field is missing. Before 1.1.0 every suspicion went to a verifier.
- Reproduce: follow Step 3b literally on a lane report whose one suspicion lacks the reachable-by field; trace to Step 5. Nothing returns it to the reviewer or lets the verifier supply the actor.

### F3. IMPORTANT: PLAUSIBLE and CONFIRMED-by-trace accept the same evidence but carry different severity ceilings

- Where: skills/project-audit/SKILL.md:99 (a CONFIRMED reproduction may be "a traced code path with the exact values at each step, when the outcome cannot be executed here") versus :101 PLAUSIBLE ("the mechanism is traced with exact values and the trigger is realistic, but it could not be produced here ... capped at IMPORTANT unless the money, time or permission exception ... applies"). The same overlap is at references/review-calibration.md:96-103 ("or the path was traced with exact values, and the control case passed" against "traced with exact values ... could not be produced here").
- Also: skills/project-audit/SKILL.md:53 "Without a sandbox, verification is by traced code path only".
- Trigger: an audit of an untrusted repo with no sandbox, or an own project whose defect needs a production-only environment. The verifier traces with exact values, and a control trace passes, a path where an anonymous request reads a secret (lens-security-auth CRITICAL: "a stranger can read secrets"). The trace evidence fits both dispositions.
- Wrong outcome: the text gives no criterion for choosing. CONFIRMED records a CRITICAL that blocks feature work and the ship. PLAUSIBLE records an IMPORTANT (reading a secret is not a "stored money, time or permission outcome"), which the user can accept at closeout like any IMPORTANT. The same evidence can produce either gate outcome depending on which label the verifier picks. The IMPORTANT cap itself is the owner's approved choice (see Questions); the missing boundary between the two dispositions is the finding.
- Reproduce: apply both definitions to one traced, non-executed path; both are satisfied.

### F4. IMPORTANT: PLAUSIBLE bypasses both guards against a verifier that agrees with everything (control and blind re-check)

- Where: skills/project-audit/SKILL.md:106
  > "When a lane's verifier refuted none of the suspicions it was given (at least three; PARTIALs do not count as refutations), give up to three of its confirmed items ... to a second verifier"
  and references/audit-method.md:101 (same, "Give up to three confirmed items"). references/review-calibration.md:149-150 says "A run where nothing was refuted gets the blind re-check".
- Also: SKILL.md:105 "Every reproduction carries a control ... no control ... stays unresolved", while the PLAUSIBLE definitions (SKILL.md:101, audit-method.md:80, review-calibration.md:99-103) do not mention a control, and SKILL.md:119 says "A PLAUSIBLE item is not unresolved".
- Trigger: a lane with five suspicions; the verifier answers PLAUSIBLE to all five, each with a trace and a named probe and no control.
- Wrong outcome: nothing was refuted, but there are no confirmed items, so the blind re-check is handed nothing. The PLAUSIBLE items have no stated control requirement and are "not unresolved", so all five are written as open findings (up to IMPORTANT, or CRITICAL under the exception), the audit completes and last_audit advances. The agreeable-verifier guard that 1.0.2 relied on is skipped by choosing the new label, and the user then has to fix or accept five unchecked items at closeout. That is the cost this release exists to cut.
- Reproduce: walk Step 4's two bullets with an all-PLAUSIBLE verification file.

### F5. IMPORTANT: a PLAUSIBLE CRITICAL (money/time/permission exception) is both "an unsupported critical verification" and "not unresolved"

- Where: skills/project-audit/SKILL.md:119
  > "An unsupported critical verification stays unresolved, never confirmed evidence. ... while any unresolved item could be CRITICAL or IMPORTANT the attempt is INCOMPLETE. A PLAUSIBLE item is not unresolved ... and it does not keep the audit INCOMPLETE."
  and :13 "An unavailable reproduction remains unresolved, partial or plausible with its coverage gap" (no rule for which).
- Trigger: a verifier traces a race in a pay path where two concurrent clock-outs both write a row (double pay: a stored-money outcome, so CRITICAL under the exception), and the timing cannot be produced here.
- Wrong outcome: two readings with different gate effects. (a) An "unsupported critical verification" goes under `### Unresolved`, which is not a finding line, so `itworks-state.sh gate` does not see it, the audit is INCOMPLETE and last_audit freezes. (b) PLAUSIBLE is written as `- [ ] CRITICAL | real-data | plausible, not reproduced here: ...`, the gate blocks the ship (shown in the lint probe below), and the audit completes. A model has to pick one, and the closeout gate sees the CRITICAL under (b) but not under (a).
- Reproduce: apply line 119's sentences in order to the item above.

### F6. IMPORTANT: closeout's reckoning must walk every finding to Fixed/Accepted/Blocking, but the new text makes ADVISORY a count

- Where: skills/project-closeout/SKILL.md:31
  > "its reckoning lists CRITICAL and IMPORTANT in full and ADVISORY as a count, with every line kept in REVIEWS.md."
- Conflicts with: skills/project-closeout/SKILL.md:54
  > "Walk EVERY unchecked finding in `REVIEWS.md`, oldest first. Each one ends in exactly one of three states"
  and :57 (Accepted requires "the user's verbatim words ... after hearing the concrete consequence once").
- Trigger: closeout with three open ADVISORY findings (for example, missing rate limiting from lens-security-auth).
- Wrong outcome: if the model follows line 31, the user hears "plus 3 advisory" and gives no per-finding words, so each ADVISORY ends neither Fixed nor Accepted and stays open through SHIPPED.md (line 54 is violated). If it follows line 54, it walks and states each one, so ADVISORY is not a count (line 31 is violated). The text does not say whether ADVISORY items are exempt from the reckoning, may be bulk-deferred, or are walked silently, so the model has to decide this itself.
- Reproduce: read Step 1 line 31 against Step 4 lines 54-58.

---

## ADVISORY

### A1. HARD-GATE wording vs the PLAUSIBLE description prefix
skills/project-audit/SKILL.md:18 "A finding enters REVIEWS.md only after a verifier has reproduced it" against :115 "the description starts `plausible, not reproduced here:`". The gate's parenthetical counts "a traced code path with the exact inputs" as a reproduction, so a careful model can reconcile them. A literal reader may keep PLAUSIBLE items out of REVIEWS.md, which defeats the point of the disposition. A logged line only.

### A2. Blind re-check threshold differs between the calibration reference and the skill
references/review-calibration.md:149-150 "A run where nothing was refuted gets the blind re-check" (run-level, no minimum) against SKILL.md:106 and audit-method.md:101 (per lane, "at least three"). A model following the reference re-checks a lane with one suspicion; one following the skill does not.

### A3. Deployment-impossible trigger: refutation or ADVISORY
references/review-calibration.md:77-80: a trigger "the deployment makes impossible (PROJECT.md says ...) is a refutation for this audit". skills/project-checkpoint/SKILL.md:127: "A trigger nobody in PROJECT.md can produce is ADVISORY at most". For the same item, one records nothing and the other records an ADVISORY line.

### A4. "the diff's own tests" in the audit reviewer brief
references/audit-method.md:59 "behavior the diff's own tests assert as intended" (and review-calibration.md:62-63) appears in the audit brief, where there is no diff. A reviewer who reads it as "the code's own tests" would not flag a money defect that a wrong test asserts (lens-testing rates a decorative test guarding money as CRITICAL). This needs a misreading, so it is logged only.

---

## Lint and parser probe (invariant 2)

I built a scratch state at `<scratchpad>/lintprobe/.itworks/` (PROJECT.md with all eight headings, DECISIONS.md, PROFILE.md format_version 3, MAP.md). Its REVIEWS.md has an `## Audit - 2026-10-14 - calibration probe` section with a scope line carrying the tally written with ` | ` separators ("Tally: raised 7 | after dedup 5 | confirmed 1 | plausible 1 | partial 1 | refuted 2 | unresolved 0"), plus:

    - [ ] IMPORTANT | real-data | plausible, not reproduced here: two concurrent clock-outs both pass the open-shift check and write two rows (shiftpay/shifts.py:40) | Evidence to close: run `pytest -k concurrent_clock_out` with two threads under a barrier and assert one row
    - [ ] CRITICAL | real-data | overtime under-counted at the midnight boundary (shiftpay/pay.py:12) | Evidence to close: test_overtime_midnight passes
    - [ ] ADVISORY | testing | partial: only the DST half holds; the leap-day half was refuted (tests/test_shifts.py:5) | Evidence to close: test_dst_shift added and passing
    ### Refuted / ### Coverage gaps lists

Results:

    $ bash scripts/itworks-lint.sh <scratch>
    0 error(s), 0 warning(s)
    exit=0
    $ bash scripts/itworks-state.sh check <scratch>
    FORMAT	1
    SUMMARY	0	0	0
    exit=0
    $ bash scripts/itworks-state.sh gate <scratch>
    FORMAT	1
    BLOCKED	B_CRITICAL_OPEN	.itworks/REVIEWS.md	0	Open critical findings block release
    SUMMARY	0	0	1
    gate exit=2

The PLAUSIBLE line and the tallied scope line pass unchanged, and an open CRITICAL still blocks the gate. Invariant 2 holds. The awk parser (scripts/itworks-state.awk:29, :95) only treats checkbox bullets as findings, so the scope line is never parsed as one.

## Invariant results

1. Internal consistency: broken in F1, F2, F3, F4, F5, F6, A1, A2, A3. Step 3b's "no verifier" for an empty lane is consistent with the completion-line check: SKILL.md:91 has the orchestrator write `no suspicions to verify` plus the completion line, which satisfies :87. The "never dropping findings" phrasing was removed from checkpoint (old Step 4), and no surviving text in skills/, commands/, hooks/ or references/ repeats it (grep).
2. Grammar and lint: holds (probe above).
3. Gates: weakened by F1 (checkpoint CRITICAL suppressed) and F2 (a CRITICAL suspicion skips the verifier), and F3/F5 make the outcome depend on a label choice. Closeout cannot write SHIPPED.md over an open CRITICAL line: the HARD-GATE and Step 4 gate text are unchanged, and the probe shows gate exit 2. The checkpoint failure-path obligation (checkpoint SKILL.md:13, :46-48) is unchanged, and no new text exempts it; lens-testing's rubric keeps "missing failure-path tests" at IMPORTANT.
4. Release identity: holds. plugin.json "1.1.0"; CHANGELOG `## [1.1.0] - 2026-10-14`; docs/releases/1.1.0.md line 1 "# 1.1.0 review calibration"; README line 3 names 1.1.0 and links docs/releases/1.1.0.md and references/review-calibration.md (both exist); tests/unit/test_release_documentation.py asserts '1.1.0'. `python3 -m unittest test_release_documentation -v` passed, 2 tests OK.
5. Clean fixture: no credential-like strings (grep for key/secret/token/password/api and 32+ char base64-like runs found nothing). Nothing executes at import beyond imports, a module constant `NY = ZoneInfo("America/New_York")` and `UTC = timezone.utc` (tests/test_shifts.py:7-8), and `if __name__ == "__main__"` guards. No I/O, subprocess, network or eval. I did not review the fixture code for defects (out of scope per the brief).

## Questions for the owner (not findings)

- PLAUSIBLE's IMPORTANT cap (approved, plan line 3 / open question 1) also caps non-money security CRITICALs such as a race that leads to command execution or a secret read, when the trigger cannot be produced here. Intended?
- Dropping a suspicion with no concrete trigger at dedup is plan-approved (plan step 2). It does mean a real CRITICAL worded without an input never reaches a verifier. Should it go back to the reviewer instead?
- The do-not-flag item "pre-existing code outside the diff at checkpoint" is in the approved plan (step 1). F1 is about its collision with the runbooks' tree-wide commands, not about the item itself.

## Notes (do not count)

- tests/scenarios/audit-02-clean-fixture.md tally assert lists "suspicions, deduplicated, confirmed, partial, refuted, unresolved" and omits "plausible", which SKILL.md:114 and pressure case 9 include.
- test_release_documentation.py checks local links only for 1.0.1.md and the release checklist, not 1.1.0.md (1.1.0.md uses backtick paths, not links, so nothing is currently broken).

## Coverage

Read in full: `git show 72221e3` (all non-fixture hunks; fixture hunks read only for invariant 5), references/review-calibration.md, skills/project-audit/SKILL.md, references/audit-method.md, skills/project-checkpoint/SKILL.md, skills/project-closeout/SKILL.md, references/state-format.md, scripts/itworks-lint.sh, scripts/itworks-state.awk, scripts/itworks-state.sh, docs/releases/1.1.0.md, tests/unit/test_release_documentation.py, docs/plans/review-calibration.md (at 72221e3), tests/fixtures/clean-app/README.md and shiftpay/*.py.
Read in part: references/lens-security-auth.md (inspect steps 1-8 and rubric, for F1); the other four lens files (diff hunks only: one added line each); tests/pressure/pressure-tests.md and tests/scenarios/audit-02-clean-fixture.md (diff hunks only).
Run: the release documentation unit test (passed); the lint, check and gate probe on a scratch state (output above).
Skipped: fixture test bodies (tests/fixtures/clean-app/tests/*.py) were scanned for import-time code and credentials only, not reviewed, per the brief's invariant 5. The research note docs/research/2026-10-14-llm-review-calibration.md was checked for existence only (it is background, not instructions).

END OF REPORT: calibration package
