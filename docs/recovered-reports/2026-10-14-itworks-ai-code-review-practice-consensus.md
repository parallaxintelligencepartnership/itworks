# Recovered: ai code review practice consensus (itworks, 2026-10-14)

| Field | Value |
|---|---|
| Source | `/Users/matthew/.claude/projects/-Users-matthew-parallax-private-Projects-itworks/eb4581b7-d4ea-484f-b4b9-25670bb1295a.jsonl` |
| Source kind | main |
| Date | 2026-10-14 |
| Session id | eb4581b7-d4ea-484f-b4b9-25670bb1295a |
| Agent type | main |
| Original brief | Research and plan are written and committed in the repo. Nothing in the skills was changed; the plan |
| KB copy | `claude-knowledge-base/recovered-reports/2026-10-14-itworks-ai-code-review-practice-consensus.md` |

Recovered 2026-10-30; not re-verified. Tags: recovered-report, itworks, research.

---

Research and plan are written and committed in the repo. Nothing in the skills was changed; the plan needs your yes first.

**What I found.** I could not locate the exact Boris post you remember, but the same advice is on record in three first-party places I read directly: his original `code-review` plugin (cached on this Mac), the current built-in `/code-review` recipe inside Claude Code 2.1.300, and his March 2026 Pragmatic Engineer interview. The practitioner write-ups and two 2026 papers agree with them. The consensus mitigations:

- **Declare the mode.** Anthropic's recipe tells the reviewer per effort level whether it reviews for precision ("a finding a maintainer would act on") or recall ("err on surfacing, a verifier filters"). An undeclared reviewer defaults to "find something".
- **Zero is a valid answer.** "If nothing survives, return an empty list", "do not invent to hit the floor". Asking for a second look raised recall slightly and halved the signal in the CR-Bench paper.
- **No finding without a concrete trigger.** Every finding carries the input or state that produces the wrong outcome. Boris's 0 to 100 rubric filters below 80, and the 50 rung ("real but might not happen in practice") is dropped.
- **Three-state verification.** CONFIRMED, PLAUSIBLE or REFUTED, and REFUTED only with proof quoted from the code. A realistic race or rare path is not refuted as "speculative".
- **An explicit do-not-flag list and a reachability test.** Pre-existing issues, linter-caught issues, intentional changes, style, and triggers the code makes impossible.
- **Deduplicate, rank by severity, cap the spoken output.** Record the rest.
- **Evidence hygiene.** One audit of several hundred findings put about 15 percent down to fabricated commits, files or counts, and about 40 percent to the model ignoring its own exclusion list.
- **Measure it.** Tally confirmed against refuted, read the refuted ones, fix the named section of the skill, keep a clean-code negative control.

**How itworks compares.** The audit tier already does the hard part better than Anthropic's recipe does: reviewer then independent verifier, reproduction with a control case, a blind re-check, a refuted list. The checkpoint and closeout tiers are fixed runbooks, which is the "deterministic layers first" advice in practice. The gaps are calibration text the tiers never state: no mode line, no "an empty report is complete" line (closeout even says the sweep "expects to find things"), no do-not-flag list, no reachability rule, no dedup step, no gap-sweep brief for re-reviewing an unchanged sha, no fabricated-reference rule, no tally across audits, and no clean-code pressure case. The full table is in `docs/research/2026-10-14-llm-review-calibration.md`.

**The plan** in `docs/plans/review-calibration.md` has seven steps: one new `references/review-calibration.md` that all three skills point at; brief and step edits to the audit skill and method; wording and report-shape edits to checkpoint and closeout; one pointer line per lens rubric; an optional recurrence loop that turns a finding seen three times into a lint rule or gotcha; three new pressure cases including the negative control; docs and a release.

Four decisions are yours before I touch the skills:

1. Add a PLAUSIBLE verifier disposition so a real mechanism with an unreproducible trigger is recorded as an open finding instead of freezing the audit as INCOMPLETE forever.
2. Report ADVISORY findings as a count in the spoken report, with every line still in REVIEWS.md.
3. Version it as 1.1.0 or as a 1.0.3 patch.
4. Keep or drop the recurrence loop.

Answer those and set the plan to Ready, and I will run steps 1 to 7 as one batch.
