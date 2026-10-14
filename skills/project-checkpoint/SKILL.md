---
name: project-checkpoint
description: Use when the user says a feature works, is finished, or asks to build the next thing, in any project containing a .itworks directory and after meaningful new code. Also on /itworks:checkpoint. Fires BEFORE starting the next feature.
---

# Project Checkpoint

## Overview

A short, targeted review of what was just built, using at most two lenses, producing evidence-backed findings. Criticals block building on top. The tier runs in precision mode (`<plugin-root>/references/review-calibration.md`): it executes the runbook steps, records what each command showed, and reports only what a rubric names. A step that finds nothing records "clean" with the command and its output and moves on; a checkpoint with no findings is a result, not a failure to look hard enough, and nothing is added to make it look like work. This is the skill that turns "I asked for X and got X, it works!" into an actual fact before the next layer gets stacked on it.

<HARD-GATE>
An "it works" claim is accepted only with evidence. Run the failure path before agreeing. A CRITICAL finding blocks new feature work until fixed or accepted in writing.
</HARD-GATE>

## Step 0: Confirm this is the right tier

A checkpoint reads the diff since `last_checkpoint` through at most two lenses. It never reads application logic outside that diff. If the user asked for "a review", "a full review", "is it solid", "check everything", or an audit, and named nothing they just built, that is `project-audit`, not a checkpoint: hand off, or ask one line ("whole application, or what was just built?"). Running a checkpoint and calling it a review is the failure this rule exists to stop.

## Step 1: Read state

Read `.itworks/PROFILE.md` (profile, lens_debt, opted_out), `.itworks/PROJECT.md` (the Verification expectations table), `.itworks/REVIEWS.md` (open findings), and `.itworks/MAP.md` (how to run and test it, and the gotchas). If `.itworks/` does not exist, this is not a checkpoint moment: hand off to `project-kickoff` adoption mode instead.

Bookkeeping drift (a `last_checkpoint` date with no matching REVIEWS.md section, counters that look off) is not corruption: proceed, and let this checkpoint's Step 5 write becomes the new truth. Structural violations of the state contracts are `project-resume`'s job, not yours.

## Step 2: Select lenses

Decide from what was just built:

- Touched login, users, roles, keys, or payments → `security-auth`
- Wired an AI or LLM feature (chat, generation, agents, embeddings) → `llm-security`
- Built UI over data, or wired a form to storage → `real-data`
- Any works/done/tested claim → `testing`
- Asked about hosting, users, or going live → `production-readiness`

**Cap at 2 lenses.** Determine applicability first. Among applicable lenses,
choose overdue debt >=3 first, ordered by highest debt, then the existing tie
order: `security-auth`, `llm-security`, `real-data`, `testing`,
`production-readiness`. Fill remaining slots with contextual lenses in that same
tie order. Overdue means prioritized, not that every overdue lens fits this
checkpoint. Unselected applicable debt increments; selected debt resets to zero;
nonapplicable debt stays zero. Three tied overdue lenses therefore select the
first two; the third reaches debt4 and wins the next checkpoint ahead of fresh
contextual work. Adoption baseline and closeout remain the two all-lens exceptions.

The cap never excuses skipping the current feature's required failure-path test
or calling untested work successful. Those evidence obligations apply regardless
of whether the testing lens fits the two selected review lenses.

**Outside the cap:** if the diff since `last_checkpoint` adds or changes dependencies (package.json, go.mod, requirements.txt, Cargo.toml, Gemfile, composer.json), also run `<plugin-root>/references/dependency-vetting.md`. The plugin root is the directory above `skills/`; the loader reports the skill's base directory as `<plugin-root>/skills/<name>`. It is a small fixed runbook, not a lens; it never counts against the cap and never gets skipped for cap reasons.

## Step 3: Run the runbooks

Read ONLY the selected lens files from `<plugin-root>/references/` (`lens-security-auth.md`, `lens-llm-security.md`, `lens-real-data.md`, `lens-testing.md`, `lens-production-readiness.md`). Execute their inspect steps with the real commands. Capture command output as evidence. Do not improvise checks the runbook does not call for; do not skip ones it does.

Two edge rules:
- A live probe that cannot run right now (no server up, no route built yet) is not skipped and not guessed green: assign severity from what the code shows, and put "not verified live:" plus the exact command into the evidence-to-close field. The live-behavior finding closes only when that command has actually run clean. A missing-test or decorative-test finding instead requires the executed regression or candidate-copy mutation evidence specified by lens-testing; a live response cannot close a test-coverage finding.
- Runbook steps gated by their own "only if" are skipped when the condition is absent. But if PROJECT.md REQUIRES the missing thing (auth needed: yes and no auth code exists), the absence itself is a finding, not a skip. And when the code shows the thing PROJECT.md says is absent (real user records in a store PROJECT.md calls sample-only, a paid API client where PROJECT.md says no paid services), the PROJECT.md line is what is wrong: fix it in the same turn and run the gated step.

## Step 4: Report at profile depth

The report's first line is the scope statement, at every profile: `Scope: checkpoint, diff <sha>..<sha>, lenses <a, b>. Not covered: code outside the diff, application logic, <anything the runbooks could not run here>. Last audit: <date or never>.` A reader who sees only that line knows what was and was not checked.

Findings use the five-field grammar from `<plugin-root>/references/state-format.md`. Always include: severity, location (file:line where applicable), and evidence to close.

- If `last_audit` is `none` and the project holds other people's real data, or `SHIPPED.md` exists and the last audit is older than 60 days, add one line after the scope statement: "An audit is due (last: <date or never>)." Say it once per session; it is a statement, not a gate.
- `guided`: each new term gets its glossary card, and each finding gets one short paragraph on what it means for the user. When one checkpoint surfaces more than 3 findings, paragraphs and cards go to the CRITICALs only; the rest get one line each. Guided depth never justifies a wall.
- `brief`: one context line per finding.
- `expert`: a terse table, plus the one-sentence blocker line for each CRITICAL. That sentence is universal across profiles; everything else stays out.

The spoken report lists CRITICAL and IMPORTANT findings in full, one line each, criticals first, and ADVISORY as a count ("plus 2 advisory, logged in REVIEWS.md"); REVIEWS.md keeps every line. Brevity comes from ranking, never from leaving the record short. A CRITICAL finding is stated as a blocker in one plain sentence, for example: "This must be fixed before we build more on top of it, because every new feature would inherit the hole." Never deliver a wall: two lenses maximum, findings only, no lecture.

## Step 5: Update state

Append the checkpoint section to `REVIEWS.md`. Still-open findings from earlier checkpoints are not restated; leave them where they are (the report may say "plus N still open from Checkpoint n"). New findings only in the new section. In `PROFILE.md`: reset `lens_debt` to 0 for selected lenses, increment unselected applicable lenses by 1, and keep nonapplicable lenses at 0.

Recurrences become rules: when a finding type (the same lens step, the same kind of gap) has appeared at three checkpoints of this project, add one line to the report proposing a deterministic check in its place (a lint rule, a test, a grep line under MAP.md Gotchas), instead of a fourth review comment. If the user takes it, record it in DECISIONS.md (`- <date> | <check> replaces review comment for <finding type> | why: recurred three times | instead of: a fourth comment`) and the runbook step points at the check from then on. Asked once per finding type.

Patch `MAP.md`: any entry point, route registration, storage location, env var name, or run/test command the diff added or moved gets its row updated, and a row the diff made false is removed. Any correction the user made this stretch about the project or its environment that is not yet under Gotchas goes there, dated, in their sense if not their words. If MAP.md does not exist (a project from before it did), write it now from the tree and the README, at most about 60 lines, and set `format_version: 3`; this is the one time a checkpoint reads outside the diff, and it reads for layout only, never for findings.

## Step 6: Restore point

Create a restore point only from explicit task-owned paths after reviewing their staged diff and scanning for credential material. Preserve unrelated staged and unstaged work. Never use blanket `git add`, plain `git commit` with unrelated staged changes, index reset, stash, or checkout over user files. Acceptance of a risk does not authorize committing known credentials. Commit authorization comes from the surrounding session/host policy.

When each owned path belongs wholly to this task and has no unrelated staged hunks, the following path-limited operation commits those paths while retaining unrelated index entries. Before running it, record `git diff --cached --binary`, status, and each unrelated file's bytes; inspect both the owned working diff and prospective staged diff. Use explicit paths (including intended review notes), never `.` or a directory that could contain unrelated files:

```bash
# checkpoint-owned-commit (owned_paths is a reviewed Bash array)
git --literal-pathspecs add -- "${owned_paths[@]}"
git --literal-pathspecs diff --cached -- "${owned_paths[@]}"
git --literal-pathspecs commit --only -m "$checkpoint_message" -- "${owned_paths[@]}"
```

Verify the resulting commit's changed paths and confirm unrelated index entries and worktree bytes are unchanged. If an owned file contains unrelated staged hunks, ownership is unclear, credentials would be included, commit authorization is absent, or safe partial staging cannot be achieved: record restore point **pending**, preserve the index, and continue only as existing finding gates permit. Do not fabricate a clean checkpoint SHA. Open findings do not themselves prevent an authorized safe restore point.

Only after a verified task commit, update `last_checkpoint` to today's date plus that commit's short SHA. Commit the owned bookkeeping change with the same isolation checks; if PROFILE contains unrelated edits, leave bookkeeping pending rather than mixing them.

## Version and release identity

Before changing any version string, tag, or release identity (package.json version, plugin manifest, git tag, build metadata beyond an auto-incrementing build number), read the recorded versioning rule in `DECISIONS.md` and follow it. If no rule is recorded (a project started before this convention), ask once, record the answer as a `- <date> | versioning: <rule> | why: ... | instead of: ad-hoc bumps` line, then follow it. Never bump minor or major on your own initiative; that holds even when nothing is recorded yet.

## Cadence guard

If fewer than roughly 15 lines changed since `last_checkpoint` (measure with `git diff --shortstat <sha>` against the sha recorded there; if no sha is recorded, the guard cannot measure and the checkpoint runs), skip silently. Do not announce a skipped checkpoint twice in a row: quiet is the point.

The guard exists to prevent checkpoint spam on trivial edits, and it NEVER outranks the gate: a works/done/tested claim, or any open CRITICAL, runs the checkpoint regardless of diff size. A gate-forced checkpoint runs its selected runbooks in full, not just a re-confirmation of the already-logged finding: stale state is exactly when fresh findings hide.

## Override handling

The user may proceed over IMPORTANT or ADVISORY findings; log each as an accepted risk in `REVIEWS.md`, quoting their words verbatim. Proceeding over a CRITICAL requires the user to say so AFTER being told the concrete consequence in one sentence; log it verbatim. Closeout will re-surface every accepted risk.

Each acceptance gets ONE short follow-up: "what would make you revisit this?" The answer is recorded as that entry's `Revisit when:` field (required, per `<plugin-root>/references/state-format.md`). A shrug or a non-answer records `next closeout`; the question is asked once and never pressed.

Acceptance is per finding: the user's words must answer the specific finding they cover ("it's a burner key" accepts the key exposure, nothing else). With several CRITICALs open, each needs its own answer before work proceeds past it; a broad "keep building" covers none of them.

Repeating the request is not acceptance, and silence on the consequence is not acceptance. On a repeat: do not restate the consequence (it was said once), do offer the fastest fix path as the way out, and name the exact words that would unblock ("say accept the risk and I'll proceed"). Hold that line however many times the request repeats; the work does not start on repetition alone.

## Rationalization table

| Thought | Reality |
|---------|---------|
| "They tested it themselves" | They ran the happy path in a browser. Run the failure path. |
| "Reviewing now kills their momentum" | Building feature 2 on a broken feature 1 kills the project. |
| "It's a tiny feature" | Tiny features touch auth and data too. Select lenses, then decide. |
| "Expert profile means lighter review" | Expert changes the words, never the checks. |
| "A review that finds nothing looks like it did nothing" | The scope line says what ran. Clean output from a real command is the evidence. |
| "That edge case could bite someday" | A trigger nobody in PROJECT.md can produce is ADVISORY at most; a trigger the code makes impossible is not a finding. Name who can reach it. |

## "Not now"

Suppress for the session on request, in one line. Repeated opt-out: record `project-checkpoint` in `opted_out` in `PROFILE.md` and mention `/itworks:checkpoint` re-enables it any time.
