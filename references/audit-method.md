# Audit method: lanes, reviewers, verifiers

The contract behind `project-audit`. Read it before deriving lanes or writing a reviewer brief.

## Why three tiers

| Tier | Reads | Finds | Misses |
|---|---|---|---|
| Checkpoint | the diff since the last checkpoint, at most two lens runbooks | a shell screen, a leaked key, an untested failure path in what was just built | anything outside the diff |
| Closeout | five fixed runbooks over the whole tree | secrets in history, unpinned deps, no backup, a crash on forced failure, an undocumented deploy | logic errors: wrong arithmetic, stale reads, races, restores that undo themselves |
| Audit | every lane's code in full, adversarially, then verification | the logic errors | what only hardware or a person can exercise (listed as coverage gaps) |

The runbook tiers are cheap and repeatable, which is why they run often. They are also blind to the application's reasoning, which is why a project that runs only them can ship "NO CRITICAL OPEN" for weeks with a CRITICAL in production. Every report from any tier names its tier and what it did not cover, so the record never overstates what was checked.

## LANES.md

Optional fifth state file, `.itworks/LANES.md`, written the first time an audit runs and updated when the layout moves. Shape:

```markdown
# Review lanes: <project name>

<one paragraph: what a lane is, when lanes are re-derived>

## Lane <letter>: <name>
Lens id: <security-auth | real-data | testing | production-readiness | llm-security>
Files in scope:
- <path> (<what it holds>)
Invariants to attack:
- <a property the reviewer tries to break, stated as the property>
Probe recipes:
- <command or test pattern the verifier uses>
Never re-flag:
- <settled decision from DECISIONS.md or the house rules that touches this lane>

## Not in scope
- <path> - <why>

## Lane-independent rules
- <the rules below, restated for the project>
```

Rules for lane design:

- Every package or directory is in exactly one lane or in "Not in scope" with a reason. Unassigned code is a coverage gap that hides.
- A lane is one reviewer's full read. If the reviewer would have to skim, split the lane.
- Lanes follow the application's money, time, identity, permission, stored-record, and export boundaries, not the directory tree. The directory tree tells you where the files are; the boundaries tell you what to break.
- Invariants are properties ("an edited end time re-validates every break inside the shift"), never past bugs ("the retime bug from July"). A past bug becomes the invariant it violated.
- Each lane declares the lens id its findings file under, so the five-field grammar and the lint stay unchanged.

## Reviewer brief (template)

Give each reviewer this, filled in:

```
You are reviewing lane <letter> (<name>) of <project> at commit <sha>, read-only.
Files in scope: <list>. Read every one in full. If you skip a file, say so and why.
Settled decisions you must not re-flag: <list from DECISIONS.md / house rules>.
Invariants to attack: <list>. For each, try to construct an input, sequence, or timing that breaks it.
Also look for: arithmetic at boundaries (rounding, zero, negative, midnight, timezone and DST transitions, period edges), state read before it is committed or after it can change, anything that writes without the check that guards the equivalent read, error paths that continue, anything that trusts the client.
Read the tests for each file and say what they do NOT prove.
You may run read-only probes: <commands>. You must not edit, create, or delete any file in the repository, and you must not spawn agents of your own.
Report: for each suspicion, file:line, the concrete input, the wrong outcome, the proposed severity per the lens rubric for <lens id>, and how a verifier could reproduce it. Then a "questions for the owner" list for anything that looks like a design choice rather than a defect. Then a coverage list: what you read, what you skipped.
```

## Verifier brief (template)

```
You are verifying lane <letter> of <project> at commit <sha>. You did not write the lane report.
For each suspicion in <report path>: reproduce it. Acceptable reproductions: a test that fails on the current code and names the input; a probe transcript against a running instance; a traced code path with the exact values at each step when execution is not possible here.
Mark each CONFIRMED (reproduction attached, final severity), REFUTED (evidence that the code is right; "looks fine" is not evidence), or PARTIAL (what holds, what does not).
For each CONFIRMED item write the fix spec: what must change, what test must fail before and pass after, and what must not change.
You must not edit the repository except in a throwaway overlay or scratch directory, and you must not spawn agents of your own.
```

## Severity

Lens rubrics stay authoritative. An audit adds one clarification: a logic defect that changes stored money, time, or permission outcomes for real users is CRITICAL regardless of how rare the trigger looks, because the record is wrong and nobody is told.

## Fix wave

Fixes for confirmed findings are a normal branch. Each fix carries a test that fails with the fix reverted. The fixes are then reviewed as a diff (a checkpoint, or another lane pass when the wave is large), because a fix wave of any size introduces regressions of its own. Then the project's release gate, then closeout.

## Retention

Keep the lane reports and verifications in the repository's documentation area, named by date and lane. The next audit starts by reading the previous one's coverage list, and a reviewer who can see what was read last time reads the rest first.
