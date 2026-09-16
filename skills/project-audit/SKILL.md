---
name: project-audit
description: Use when the user asks for a review of the whole application ("review the app", "full review", "is it solid", "check everything", "audit"), before the first ship that carries other people's real data, or when a shipped project has never been audited or its last audit is stale, in any project with a .itworks directory. Also on /itworks:audit. This is the review tier that reads application logic; checkpoint and closeout never do.
model: opus
---

# Project Audit

## Overview

The whole-application adversarial review. Checkpoints look at a diff through at most two lenses. Closeout re-runs five fixed runbooks (secret scan, restart test, dependency pins, forced-failure UX, and so on) over the whole tree. Neither reads the application's logic, so neither can find a pay calculation that under-counts, a login that trusts a stale row, or a restore that reverts itself. Those live in the code's reasoning, and only a reviewer who reads the code in full, with a brief to break it, finds them.

An audit splits the application into lanes, gives each lane to a read-only reviewer who reads everything in scope, then gives every finding to an independent verifier who must reproduce it before it is written down. What the verifier cannot reproduce is recorded as refuted, with the evidence, so the same suspicion is not re-raised next time.

<HARD-GATE>
A finding enters REVIEWS.md only after a verifier has reproduced it (a failing test, a probe transcript, or a traced code path with the exact inputs). A reviewer's word is a suspicion, never a finding. An audit report that lists lanes it did not read, or findings nobody reproduced, is not an audit; say what was skipped instead. A CRITICAL confirmed by the audit blocks new feature work and the next ship exactly as a checkpoint CRITICAL does.
</HARD-GATE>

## When this skill is the right one

The user's words decide the tier, and the tier decides what gets read:

| The user says | Tier | What gets read |
|---|---|---|
| "it works", "done", "next feature" | `project-checkpoint` | the diff since the last checkpoint, at most two lenses |
| "ship it", "deploy", "put it live" | `project-closeout` | the five lens runbooks over the tree, then the reckoning |
| "review the app", "full review", "is it solid", "check everything", "find what's wrong", "audit" | **`project-audit`** | every lane's code in full, adversarially, then verification |

A request for "a review" with no object named, in a project that has shipped or holds real data, means an audit. If the request could mean either tier, ask one line: "Whole application (audit, reads all the code, takes a while) or what was just built (checkpoint)?" Never silently run the smaller tier and call it a review.

The audit is also due, and the skill says so at the next checkpoint or closeout without being asked, when:

- the project holds other people's real data (PROJECT.md `Data` / `Who uses it`) and `last_audit` in PROFILE.md is `none`;
- `SHIPPED.md` exists and the last audit is older than 60 days or more than 5 ship-history entries back;
- a checkpoint or closeout finds a CRITICAL in code that no recent diff touched (a defect that was already shipped is exactly the kind an audit finds more of).

Due is a statement, not a gate: "An audit is due (last: never). Run it now, or after this ship?" One line, asked once per session.

## Step 1: Read state and choose the target

Read `PROFILE.md` (`last_audit`), `PROJECT.md` (Verification expectations, Data, Who uses it), `REVIEWS.md` (open findings and every accepted risk), `DECISIONS.md` (settled decisions a reviewer must not re-flag), and `MAP.md` (the layout the lanes are cut from, and the gotchas every reviewer is told about). Pin the target: a commit sha on the branch the user wants reviewed, recorded as `<date> @<sha>` in the report. Reviewers read that sha, not a moving branch.

## Step 2: Lanes

Read `references/audit-method.md` for the lane contract. Lanes live in `.itworks/LANES.md`. If the file exists, use it, and update it when the code layout has moved (a lane whose listed files no longer exist is stale). If it does not exist, derive lanes now:

1. Start from PROJECT.md's Verification expectations table: each feature row that carries money, time, identity, permissions, stored records, or exports is a lane candidate.
2. Start from MAP.md's Layout table, then walk the tree for anything it misses (and add those rows to MAP.md), and assign every package or directory to exactly one lane, or to an explicit "not in scope" list with a reason. Nothing is unassigned silently.
3. Size each lane so one reviewer can read it in full in one pass. Split a lane that is bigger than that; merge lanes that are trivial.
4. For each lane record: the lens id its findings file under, the files in scope, the invariants to attack (properties a reviewer tries to break, phrased as properties, not past bugs), the probe recipes a verifier uses, and the settled decisions never to re-flag.
5. Play the lane list back in one message and get a yes. Lanes are the user's document like the other state files; write `.itworks/LANES.md` after the yes.

## Step 3: Review, one reviewer per lane

Each lane gets one reviewer with the brief in `references/audit-method.md`. The reviewer:

- reads every file in scope in full, and lists any file it skipped and why (a skip is a coverage gap in the report, never silence);
- reads the tests for what they prove and what they do not;
- runs read-only probes (test runs, scripted inputs, timezone and boundary sweeps) but never edits the repository;
- reports suspicions with file:line, the concrete input that triggers each, the wrong outcome, and a proposed severity per the lens rubric;
- never re-flags a settled decision from DECISIONS.md or the house rules; a reviewer who thinks a settled decision is wrong says so in a separate "questions for the owner" list, not as a finding.

Run lanes in parallel when a delegation tool is available, one agent per lane, each told plainly that it must not spawn agents of its own and must not write to the repository. Without delegation, run lanes one at a time in the main session and stop after each lane to write its report; never claim a lane was read that was not. A reviewer should be at least a Sonnet-class model, and should not be the same session that wrote the code under review when that can be arranged.

## Step 4: Verify, one verifier per lane

Every suspicion goes to a verifier who did not write the lane report. The verifier reproduces each one:

- a test that fails on the current code and names the input (`go test -run`, `pytest -k`, a scripted request), or
- a probe transcript against a running instance, or
- a traced code path with the exact values at each step, when the outcome cannot be executed here.

Each suspicion ends as CONFIRMED (with the reproduction and the final severity), REFUTED (with the evidence that shows the code is right), or PARTIAL (what holds, what does not). A refutation needs the same rigor as a confirmation: "looks fine" refutes nothing. For the highest-consequence confirmed items, a third opinion from a different model or tool is worth the cost; record who gave it.

## Step 5: Record

Append to `REVIEWS.md` under `## Audit - <YYYY-MM-DD> - <context>`:

- a scope line: target sha, lanes read, lanes or files skipped and why, the verifier method, and what was NOT covered (live hardware, external systems, anything only a person can test);
- one five-field finding line per CONFIRMED item, grammar per `references/state-format.md`, filed under the lane's lens id;
- a `### Refuted` list, one line each with the evidence, so the suspicion is not re-raised;
- a `### Coverage gaps` list: every skipped file, every lane not run, every probe that could not run here.

Set `last_audit: <YYYY-MM-DD> @<sha>` in PROFILE.md. Retain the lane reports and verifications under `docs/` (or the project's evidence directory) so the next audit can start from what was read last time.

## Step 6: Fix path

A confirmed CRITICAL is a blocker in one plain sentence, as at checkpoint. The fix wave that follows is ordinary work: a branch, one fix per confirmed finding, each with a test that fails when the fix is reverted, then the fixes themselves reviewed (a fix wave introduces its own regressions; the first audit of a mature app found nearly as many in the fixes as in the code). Then the project's release gate, then closeout for the ship.

## Report shape

At any profile the report opens with the scope line, then findings grouped by severity, criticals first, one line each, then refuted and coverage gaps as counts with a pointer to the retained reports. Guided adds one paragraph per CRITICAL on what it means for the user. Nothing else; an audit is long enough already.

## Rationalization table

| Thought | Reality |
|---------|---------|
| "Closeout already swept everything" | Closeout runs five runbooks. It never read the pay calculation. |
| "The tests pass" | Tests prove what someone thought to test. The audit looks for what nobody did. |
| "Reading every file is too expensive" | Two criticals shipped to production for two months because nobody read them. Reading is cheaper. |
| "The reviewer found it, that's enough" | Reviewers are wrong often. Half of one audit's suspicions were refuted. Verify, then write it down. |
| "It's a mature app, it's fine" | Mature apps carry the oldest bugs. |

## "Not now"

An audit invoked by mistake stands down in one line. A due audit that the user defers is recorded in DECISIONS.md with their words and re-stated at the next closeout as an OUTSTANDING line in SHIPPED.md. Repeated opt-out: record `project-audit` in `opted_out`; `/itworks:audit` re-enables it any time.
