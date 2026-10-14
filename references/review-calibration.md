# Review calibration: what counts as a finding

The rules every itworks reviewer and verifier follows so that "look for problems"
does not turn into "produce problems". The three tiers, the lens runbooks and the
audit method all point here; this file is the one place these rules live.

Background and sources: `docs/research/2026-10-14-llm-review-calibration.md`.

## The mode comes first

A reviewer that is not told what it is optimizing for defaults to finding
something. Every brief states one of two modes:

- **Precision.** Every finding is one a maintainer would act on today. Checkpoint
  and closeout run in this mode: they execute fixed runbook steps, record what each
  command showed, and report only what the rubric names. A step that finds nothing
  records "clean" with the command and its output, and moves on.
- **Recall, then precision.** An audit lane reviewer surfaces every suspicion that
  has a concrete trigger, because an independent verifier will filter. The
  verifier runs in precision mode: nothing is written down that it did not
  reproduce or trace.

A reviewer never self-censors in recall mode and never speculates in precision
mode. A finder that silently drops half-believed suspicions bypasses the verifier;
a finder that passes on suspicions with no trigger wastes a verifier run each.

## Zero is a valid answer

An empty report with a full coverage list (what was read, what was run, what was
skipped and why) is a complete report. It is not a sign the reviewer was lazy and
it is not padded with advisory notes to look like work. Nobody asks a reviewer,
verifier or runbook for "more" after an empty result: a second look raises recall a
little and roughly halves the signal. There is no floor on findings, at any tier,
at any profile.

## A finding needs a trigger

Every suspicion, finding and verification names:

- **where**: file and line, or the command and its output;
- **the trigger**: the input, state, sequence or timing that produces the problem;
- **the wrong outcome**: what happens that should not, in one sentence;
- **reachable by**: who or what can produce that trigger in the deployment as
  described in PROJECT.md (an anonymous visitor, a logged-in user, an admin, a
  scheduled job, a config change, a dependency upgrade).

A suspicion with no trigger is not passed on: there is nothing to reproduce. A
suspicion whose "reachable by" is missing is passed on marked `reachability:
unstated`, and the verifier supplies it from the trigger; a missing field never
keeps a suspicion from the verifier. A finding is written to REVIEWS.md with its
"reachable by" filled in.

## The do-not-flag list

Checked before a finding is emitted, at every tier:

1. **Reading outside the scope.** A reviewer does not go looking beyond its scope
   (at checkpoint, application logic outside the diff is the audit's job). But a
   runbook step that by design scans the whole tree (the secret scan, the
   protected-route probe) reports what it finds wherever it sits, and anything a
   reviewer actually observed that meets a CRITICAL rung is recorded, never filed
   as "not covered". "Not covered" is for what was not read, not for what was seen.
2. **Caught by the deterministic layers.** Anything the project's typecheck, lint,
   build or the lens greps already catch. Run those; do not re-report them in
   prose.
3. **Settled.** A decision recorded in DECISIONS.md, or a rule in the house
   instructions. A reviewer who disagrees writes a "questions for the owner" line.
4. **Intentional.** A behavior the task asked for or DECISIONS.md records. A test
   asserting a behavior is not by itself proof it is intended; a test that asserts
   a wrong money, time or permission outcome is a testing finding.
5. **Taste.** Style, naming, "could be cleaner", "consider extracting", and any
   change with no observable effect on behavior, data, security or cost.
6. **Out of class.** A category the running lens's rubric does not name. A finding
   with no rubric rung has no severity, and a finding with no severity is not a
   finding; it is at most a question for the owner.

## The reachability rule

Reachability changes the disposition, not just the severity:

- A trigger the code makes impossible is a **refutation**: a type, a constant, an
  invariant established earlier on every path, or a guard. The refutation quotes
  the line that makes it impossible.
- A trigger the deployment makes impossible (PROJECT.md says local machine only,
  no auth, no paid services) is a refutation **for this audit**, recorded with the
  PROJECT.md line it rests on, so the next audit re-checks it when that line
  changes.
- A trigger that needs an unrealistic actor (an admin attacking their own data, a
  config nobody sets, a request the front end cannot send and the API rejects, a
  state only a code change could produce) is **ADVISORY at most**.
- A trigger that is realistic but rare (a race, a cold cache, a retry storm, a
  missing optional field, an error path) is **not** refuted for being rare.
  "Speculative" and "depends on runtime state" are not refutations.

One exception stands unchanged from `audit-method.md`: a logic defect that changes
stored money, time or permission outcomes for real users is CRITICAL however rare
the trigger looks, because the record is wrong and nobody is told.

## Verifier verdicts

A verifier returns exactly one disposition per item, with the evidence attached:

- **CONFIRMED**: a named concrete input or sequence, and either the reproduction
  ran (a failing test that names it, a probe transcript) or the path was traced
  from that input with exact values at each step to the wrong outcome; plus the
  control case passed (the same test, or the same trace, on a safe input). Final
  severity from the lens rubric.
- **PLAUSIBLE**: the mechanism is real (traced with exact values) but no concrete
  input or sequence that reaches it could be named or produced here; what is
  known is the condition (a timing window, an environment, hardware, a live
  system). It still carries a control: the traced safe path. Recorded as an open
  finding whose evidence to close is the exact probe that would settle it. Capped
  at IMPORTANT unless the money, time or permission exception applies; then it is
  recorded as an open CRITICAL and gates ships like any other open CRITICAL. A
  PLAUSIBLE item does not keep an audit INCOMPLETE. The line between the two is
  the input: CONFIRMED names it, PLAUSIBLE names the condition.
- **PARTIAL**: part of the claim holds and part does not; the record says which.
- **REFUTED**: only with proof from the code or the deployment, per the
  reachability rule. "Looks fine", "unlikely" and "the framework probably handles
  it" refute nothing.

A verifier is asked a short question with a fixed answer set, not for an essay.
Explanation-heavy verification prompts produce more false rejections of correct
code than binary ones.

## Evidence hygiene

A cited file, line, function, commit, ticket or count that does not exist refutes
the finding on the spot. A reviewer that does it twice in one lane is re-run from
scratch with a fresh context, and the orchestrator records why. Context from
another repository, including the plugin's own, never leaks into a finding.

## Deduplicate before verifying

Before suspicions go to a verifier, the orchestrator folds items that name the
same line and the same mechanism into one, keeping the most concrete trigger. The
tally records both counts (raised, deduplicated).

## Re-reviews are gap sweeps

A second review of a target that has not changed (same sha, or the same diff
already checkpointed) runs as a gap sweep, not a fresh hunt:

- it reads the previous findings, refuted list and accepted risks first;
- it looks only for defects not already recorded;
- it never re-raises a refuted or accepted item (a changed PROJECT.md line that
  invalidates a deployment refutation is the one exception, and it says so);
- it returns empty when nothing is new;
- each new CRITICAL or IMPORTANT it does find says which angle or file the
  previous review missed, so the miss is a fact about the method, not a mystery.

## What the user hears

The record (REVIEWS.md) keeps every finding, one line each. The spoken report is
ranked most severe first: CRITICAL and IMPORTANT in full, ADVISORY as a count
("plus 3 advisory, logged in REVIEWS.md"), then the refuted and coverage-gap
counts. Brevity comes from ranking, never from leaving the record short.

## Measure it

Every audit scope line carries a tally: suspicions raised, after dedup, confirmed,
plausible, partial, refuted, unresolved. A lane whose verifier refuted none of at
least three items (PARTIAL and PLAUSIBLE are not refutations) gets the blind
re-check `audit-method.md` describes, sampled from its confirmed and plausible
items. A refuted item is read, not just
counted: when the same cause refutes three items across audits of one project,
the reviewer brief for that project (LANES.md "Never re-flag") gets the line that
would have stopped it.

## Recurrences become rules

A finding type that has appeared at three checkpoints of the same project is
cheaper as a deterministic check than as a fourth review comment. Checkpoint
proposes one (a lint rule, a test, a grep line under MAP.md Gotchas) in one line;
if the user takes it, DECISIONS.md records it and the lens step points at the
check from then on.
