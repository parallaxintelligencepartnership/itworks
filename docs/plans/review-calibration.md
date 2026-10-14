LT: b7b6359d-832f-416c-b712-e5d38e3f0380
Status: In progress
Approved by Matt: 2026-10-14, all four open questions ("1 yes. 2. yes 3. 1.1 4. keep"): PLAUSIBLE disposition, ADVISORY as a count, version 1.1.0, recurrence loop kept. Covers the 1.1.0 tag, Gitea push and refreshing his local install; GitHub push is handed to Matt as a one-line command.

# Review calibration: make every itworks tier say what counts as a finding

Research and the gap table: `docs/research/2026-10-14-llm-review-calibration.md`
(principles P1 to P12 referenced below).

## Goal

Stop the "ask for bugs, get bugs" drift in all three tiers without weakening the
gates. Every reviewer and verifier itworks launches is told which mode it is in,
what never counts as a finding, that an empty report is a complete report, and
that a finding needs a concrete trigger a real user or attacker can produce. The
record keeps everything; the spoken report ranks and caps.

## Steps

1. **New reference `references/review-calibration.md`** (one source, like the lens
   files; every skill points at it instead of repeating it). Contents:
   - the two modes and which tier runs which: checkpoint and closeout review for
     precision ("a finding a maintainer would act on"); an audit reviewer reviews
     for recall and its verifier for precision (P1);
   - "zero is a valid answer": an empty report with a full coverage list is
     complete; no reviewer is ever asked for more findings after an empty report;
     no floor, no padding (P2);
   - the do-not-flag list, structured, for every tier: pre-existing code outside
     the diff at checkpoint; anything the project's typecheck, lint or build
     catches; settled decisions in DECISIONS.md; intentional changes the task
     asked for; style, naming and taste; "could be cleaner" with no observable
     effect (P5);
   - the reachability rule: every suspicion names who or what produces the
     trigger. A trigger the code or deployment makes impossible (type, constant,
     invariant, guard; quote it) is a refutation. A trigger that needs an
     unrealistic actor (an admin attacking themselves, a config nobody sets, a
     request the front end cannot send AND the API rejects) is ADVISORY at most.
     The existing exception stands unchanged: a defect that changes stored money,
     time or permission outcomes is CRITICAL however rare the trigger (P5);
   - evidence hygiene: a cited file, line, function or commit that does not exist
     refutes the finding; a reviewer that does it twice in one lane is re-run
     from scratch (P9);
   - dedup before verification: same line and mechanism, keep the most concrete
     (P8);
   - re-review of an unchanged target is a gap sweep: only defects not already
     recorded, never a refuted or accepted item, empty when nothing is new, and
     each new CRITICAL or IMPORTANT says which angle missed it last time (P7);
   - the spoken-report shape: ranked most severe first; CRITICAL and IMPORTANT in
     full; ADVISORY as a count plus "see REVIEWS.md" (P6; open question 2).

2. **Audit skill and `audit-method.md`.**
   - Reviewer brief: add the mode line (recall, a verifier filters), the
     do-not-flag list by reference, a "Reachable by:" line per suspicion, "pass
     every candidate with a nameable trigger through, drop any without one", and
     "an empty report with the coverage list is complete".
   - New Step 3b: the orchestrator dedups suspicions across the lane report
     before handing them to the verifier.
   - Verifier brief: keep CONFIRMED / REFUTED / PARTIAL and the control case;
     add the REFUTED-only-with-proof wording from the calibration reference, and
     the PLAUSIBLE disposition if open question 1 is answered yes.
   - Step 5 scope line gains a tally: suspicions raised, deduplicated, confirmed,
     partial, refuted, unresolved (P12).
   - Rationalization table: add "An empty lane means the reviewer was lazy" with
     the reality "An empty lane with a full coverage list is a result. A padded
     lane costs a verifier run per invented item."
   - A re-audit of a sha already audited runs the gap-sweep brief, not a fresh
     recall brief.

3. **Checkpoint and closeout skills.**
   - One line in each Overview: the tier reviews for precision; a runbook step
     that finds nothing records "clean" with the command output and moves on.
   - Closeout Step 1: replace "expects to find things no checkpoint caught" with
     "re-runs every inspect command; what it finds is the output, not the
     expectation".
   - Report shape (Step 4 of checkpoint, the reckoning of closeout): ADVISORY as
     a count in the spoken report, everything in REVIEWS.md (open question 2).
   - Rationalization table in checkpoint: add "A review that finds nothing looks
     like it did nothing" with the reality "The scope line says what ran. Clean
     output from a real command is the evidence."

4. **Lens files.** One line under each `## Severity rubric`: "Reachability and the
   do-not-flag list: `review-calibration.md`." No rubric values change.

5. **Recurrence loop (P11).** In checkpoint Step 5: a finding type that has
   appeared in three checkpoints of the same project gets one line proposing a
   deterministic check (a lint rule, a test, a grep in MAP.md Gotchas) instead of
   a fourth review comment. Recorded in DECISIONS.md if the user takes it.

6. **Pressure tests.**
   - Case 9, audit / expert, negative control: a small fixture with no defects
     and a full test suite; pass means every lane returns an empty report with a
     coverage list, the verifier is not launched on nothing, the scope line and
     tally are written, and the model does not pad or apologize.
   - Case 10, audit / brief, re-review: the same fixture as case 7 after its
     findings are fixed; pass means the second audit runs the gap-sweep brief,
     re-raises nothing refuted or accepted, and either returns empty or names
     the angle that missed each new item.
   - Case 11, checkpoint / guided, reachability: a diff with one real
     failure-path gap and one "bug" guarded by a type the reviewer can see;
     pass means the guarded one is either absent or refuted with the quoted
     guard, never reported as IMPORTANT.
   - `tests/scenarios/audit-02-clean-fixture.md` documenting case 9.

7. **Docs and release.** README tier table gets a "How findings are calibrated"
   paragraph (three sentences). CHANGELOG entry. Version per open question 3.
   Offline suites, tag, Gitea push, Matt's install refreshed, GitHub push handed
   to Matt as a one-line command.

## What done means

The calibration reference exists and all three skills point at it; the audit
reviewer and verifier briefs carry the mode, reachability and empty-report lines;
dedup and the tally are in the audit steps; the closeout wording no longer expects
findings; pressure cases 9 to 11 are written and case 9 has been run once on the
current model and passed; the offline suites pass; the release is tagged and
installed on Matt's Mac.

## Open questions (product decisions for Matt)

1. **PLAUSIBLE as a fourth verifier disposition.** Today a real mechanism whose
   trigger cannot be constructed here (a race, a cold-cache path) is "unresolved",
   and an unresolved CRITICAL or IMPORTANT keeps the audit INCOMPLETE and
   `last_audit` frozen. Anthropic's recipe keeps such items as PLAUSIBLE and
   reports them. Proposal: PLAUSIBLE = mechanism traced with exact values, trigger
   realistic but not reproducible here; recorded as an open finding whose
   evidence-to-close is the probe that would settle it; capped at IMPORTANT
   unless the money/time/permission rule applies; does not keep the audit
   INCOMPLETE. The alternative is to leave the strict rule from 1.0.2 and accept
   that some audits never complete.
2. **ADVISORY as a count in the spoken report.** The record keeps every line;
   the report says "plus 4 advisory, logged". Guided-profile users gain the most.
   The alternative is today's "every finding, one line each".
3. **Version.** This changes review behavior and adds a reference file: 1.1.0.
   A 1.0.3 patch is defensible if Matt wants the state format and tier contract
   untouched in a minor-looking release.
4. **Recurrence loop (step 5).** Keep or drop; it is the only step that adds a
   new behavior rather than calibrating an existing one.

## Where it stands

2026-10-14: research note and this plan written and committed. Nothing in
`skills/`, `references/` or `tests/` has been changed. Next step: Matt answers
the four questions, sets Status to Ready, and steps 1 to 7 run as one batch.
