# LLM code review calibration: what the field says, and where itworks stands

Date: 2026-10-14. Written for the plan in `docs/plans/review-calibration.md`.

## The problem

Ask a frontier coding model to "find bugs" and it finds some. Ask again on the
same code after fixing them and it finds more. Most are worth a look; many are
overblown, unreachable edge cases, pre-existing issues, or style dressed up as
defects. The cost lands on the person reading the review: every finding has to be
judged, and a reader who cannot judge (the itworks user) either fixes noise or
learns to ignore the tool. One practitioner measured the second outcome as a
step function: past roughly half false positives, developers dismiss the tool by
default and accuracy gains no longer win them back (Ulrich, below).

Two things drive it. The model is optimized for plausibility, so a plausible
mechanism reads as a bug even when the trigger cannot occur. And the prompt
asks for findings, so the model's "pull toward reporting a problem" overrides
suppression rules it was given (Ulrich quotes this directly: "A model's strong
instinct to 'find something wrong' overwhelms the suppression rule").

## Sources

First party (read from the installed tooling on this Mac, not from the web):

- **S1. Boris Cherny's original `code-review` plugin** (`~/.claude/plugins/cache/claude-plugins-official/code-review/.../commands/code-review.md`, author line in its README). Five parallel Sonnet finders, then one Haiku scorer per issue using a verbatim 0/25/50/75/100 confidence rubric, filter below 80, and an explicit false-positive list: pre-existing issues, "looks like a bug but is not", nitpicks a senior engineer would not raise, anything a linter, typechecker or compiler catches, general quality issues unless CLAUDE.md requires them, intentional changes, real issues on lines the PR did not touch. "No issues found" is a sanctioned output. The 50 rung is "verified real, but might be a nitpick or not happen very often in practice", and it is filtered out.
- **S2. The built-in `/code-review` recipe in Claude Code 2.1.300** (strings extracted from the binary; the same recipe the `code-review` skill and the `ReportFindings` tool run here). Effort levels set the reviewer's mode explicitly: low is one diff pass, no verify, at most 4 findings; medium is "reviewing for precision: every finding you surface should be one a maintainer would act on", 8 finder angles, one-vote verify, at most 8; high and above are "reviewing for recall, err on the side of surfacing", with a verify pass and a gap sweep, capped at 10 or 15. Every finding carries `file`, `line`, a one-sentence `summary`, and a concrete `failure_scenario` ("inputs/state -> wrong output/crash"). Verifiers return exactly CONFIRMED, PLAUSIBLE or REFUTED; REFUTED only when constructible from the code (quote the line that proves it, show the type or invariant that makes it impossible, cite the guard, or pure style). PLAUSIBLE is the default when the state is realistic (a race, a cold cache, a rare but reachable error path); "speculative" is not a refutation. Candidates are deduplicated by line and mechanism before verification. Finders "that silently drop half-believed candidates bypass the verify step"; the finder's job is recall, the verifier's is precision. Output is ranked most severe first under a cap, "if nothing survives verification, return []", "do not invent to hit the floor", and the gap sweep "returns an empty sweep, do not pad". The security review skill in the same binary says: flag only above 80% confidence of actual exploitability, "better to miss some theoretical issues than flood the report with false positives", and it hard-excludes whole classes (DoS, rate limiting, resource exhaustion).
- **S3. Boris Cherny, The Pragmatic Engineer podcast, 2026-03-04** (transcript fetched). Every Anthropic PR is reviewed by Claude Code, which "catches maybe like 80%" of bugs; "we launch parallel agents to do stuff, and then we launch parallel de-duping agents to check for false positives"; deterministic layers (typecheck, lint, build) run first; recurring review comments become lint rules ("anytime a row had more than three or four instances, I would write a lint rule for it"); a person always approves the change.
- **S4. Boris Cherny on X, 2026** (search snippet only, the post itself is paywalled to fetch): the verification shape he describes is "1. build a model of the program, targeting a tricky state machine or race-prone part 2. find counter-examples in the model; these are suspected bugs 3. reproduce" (https://x.com/bcherny/status/2102898067133595992). Earlier posts (Dec 2025, Jan 2026) say the biggest lever is giving Claude a way to verify its own output; "2-3x the quality". The specific post Matt remembers, about bug reviews always finding something, was not found by two searches; the sources above carry the same advice.

Practitioners and papers (fetched unless marked snippet):

- **S5. Bob Ulrich, "Diagnosing False Positives in AI Code Review", 2026-04-18** (https://tech.bdigitalmedia.io/blog/diagnosing-ai-review-false-positives/). Audited several hundred findings. Clusters: ignoring its own exclusion list (about 40%, the "find something wrong" pull); fabricated evidence (about 15%: invented commit hashes, inflated counts, nonexistent files or functions, context leaking from the review tool's own repo); configuration treated as production code (30 to 42%). Method: collect real findings, give each a binary true/false verdict with a written reason, cluster by root cause, make structural fixes to named sections of the review skill (a mandatory checklist before a finding can emit, structured exclusion categories, evidence verification gates, path-based early exits), then announce the relaunch because a quiet fix does not recover trust.
- **S6. PhotoStructure, "Claude Code review", 2026-03-11** (fetched by the researcher). "No proof, no report": a finding needs a concrete failing scenario; trace callers and read the tests and design docs before flagging; exclude style, speculation and out-of-diff issues; run a reproducer where possible; "three proven bugs beat fifteen maybes".
- **S7. AgentPatterns, "LLM review overcorrection", reviewed 2026-06-12** (fetched by the researcher). LLM reviewers lean toward rejecting correct code; explanation-heavy prompts cause more false rejections than binary-verdict prompts; the fix-guided test: run the original and the proposed fix against the tests, if both pass it was style, if only the original fails it was a defect (weak tests weaken this).
- **S8. Agarwal, "Refute-or-Promote", arXiv 2604.19049, 2026-04-21** (fetched by the researcher). Adversarial reviewers try to disprove each candidate; cold-start reviewers and a cross-model critic; a mandatory empirical gate was added after ten reviewers endorsed a nonexistent OpenSSL bug; about 79% of 171 candidates were killed before disclosure.
- **S9. CR-Bench, Nutanix, arXiv 2603.11078, 2026-03-10** (fetched by the researcher). Precision of LLM review findings against a ground-truth benchmark was 3.5% to 5.1%. A reflexion-style "look again" retry raised recall (27.0% to 32.8%) but cut signal-to-noise from 5.11 to 1.95. High-severity defects were recalled best.
- **S10. Rushi, "Claude Code Review: when the AI reviews its own work", 2026-03-09** (fetched). Relays Anthropic's internal figures (PRs over 1,000 lines: 84% get findings, averaging 7.5; under 50 lines: 31%, averaging 0.5; engineers disagreed with under 1% of surfaced findings; all unverified third-party numbers) and the known misses: it "sometimes flags race conditions that can't actually occur", and misses architectural questions while flagging cosmetic ones.
- **S11. bswen, 2026-03-05** (snippet): one developer's sample found Opus 4.6 with zero false positives and 80% missed real issues. Small sample; it illustrates the precision-recall trade, not a rate.

## The principles, merged

Each one is attributed so the plan can cite it.

- **P1. Declare the mode.** Tell the reviewer whether it is reviewing for precision (every finding one a maintainer would act on) or recall (err on surfacing, a verifier will filter). Never leave it undeclared; an undeclared reviewer defaults to "find something". (S2)
- **P2. Zero is a valid answer, and padding is forbidden.** "No findings" with a full coverage list is a complete report. Never ask for more findings after an empty report; a retry raises recall a little and halves the signal. (S1, S2, S9)
- **P3. No finding without a concrete failure scenario.** Location, the input or state that triggers it, the wrong outcome. A candidate without one is not passed on. (S2, S6)
- **P4. Separate finding from verifying, with a three-state verdict.** The finder is recall-biased and does not self-censor; an independent verifier returns CONFIRMED, PLAUSIBLE or REFUTED. REFUTED only with proof from the code; "speculative" is not a refutation when the state is realistic. Verifiers get a binary or three-state question, not an essay prompt. (S1, S2, S3, S7, S8)
- **P5. An explicit do-not-flag list and a reachability test.** Pre-existing issues outside the change, anything a linter or typechecker catches, settled decisions, intentional changes, style; and a trigger that needs an actor or state the code or deployment makes impossible is a refutation, while one that needs an unrealistic actor is advisory at most. Keep the list structured and near the point of emission, not buried in a long prompt. (S1, S2, S5, S10)
- **P6. Rank by severity, cap the spoken output, record the rest.** Brevity comes from ranking, never from dropping the record. (S2, S6)
- **P7. Re-reviews are gap sweeps.** A second review of unchanged code looks only for defects not already listed, never re-raises refuted or accepted items, and returns empty when there is nothing new. (S2)
- **P8. Deduplicate before verifying.** Same line, same mechanism: keep the most concrete. (S2, S3)
- **P9. Evidence hygiene.** Every cited file, line, function and commit must exist; a fabricated reference refutes the finding and marks the reviewer. (S5)
- **P10. Tests are the ground truth.** A fix carries a test that fails with the fix reverted; a candidate-copy mutation proves the suite is not decorative; the fix-guided test separates defects from style. (S3, S4, S7)
- **P11. Deterministic layers first, and recurring findings become rules.** Typecheck, lint, build and scanners run before the model; a finding that recurs three or four times becomes a lint rule or a recorded gotcha, not a repeated review comment. (S3)
- **P12. Measure the false-positive rate and fix the skill text from it.** Tally confirmed against refuted per run, read the refuted ones, cluster by cause, edit the named section of the skill, and keep a negative control (clean code must come back clean). (S5, S8)

## Where itworks stands

The audit tier was built around P3, P4 and P10 already (reviewer then independent verifier, reproduction with a control case, blind re-check, refuted list, fix-wave tests), and the checkpoint and closeout tiers are fixed runbooks, which is P11 in practice. The gaps are mostly calibration text that the tiers never state, plus one structural question.

| Principle | Checkpoint / closeout | Audit | Gap |
|---|---|---|---|
| P1 mode | Implicit (runbooks) | Implicit | Neither skill tells the model which mode it is in. Checkpoint and closeout are precision tiers; the audit reviewer is recall and its verifier is precision. Say so. |
| P2 zero valid | Not stated; closeout says the sweep "expects to find things no checkpoint caught" | Not stated; rationalization table only pushes toward finding | Add "an empty report with a full coverage list is complete" to every brief; reword the closeout expectation; add "never ask a reviewer for more". |
| P3 failure scenario | Runbook evidence is command output | Reviewer brief asks for concrete input and wrong outcome | Aligned. Make the trigger part of the audit finding description. |
| P4 three-state verdict | n/a | CONFIRMED / REFUTED / PARTIAL plus controls and blind re-check | Stronger than S2 on confirmation. Missing the PLAUSIBLE middle: a real mechanism with a realistic but unconstructible trigger becomes "unresolved" and keeps the audit INCOMPLETE. See open question 1. |
| P5 do-not-flag, reachability | Settled decisions; "only if" rules | Settled decisions; "questions for the owner" list | No do-not-flag list, no reachability line, no rule that an impossible trigger is a refutation. The deliberate exception stays: a stored money, time or permission defect is CRITICAL however rare. |
| P6 rank and cap | Report lists every finding one line each | Same | Add: CRITICAL and IMPORTANT in full, ADVISORY as a count with a pointer, in the spoken report; REVIEWS.md keeps everything. See open question 2. |
| P7 re-review sweep | Cadence guard; gate-forced runs re-run runbooks (deterministic, fine) | Refuted list; next audit reads last coverage | No sweep-mode brief for re-reviewing an unchanged sha; nothing says a re-review must name what it missed before. |
| P8 dedup | n/a | None | Add a dedup step between reviewer and verifier. |
| P9 evidence hygiene | Commands and output | file:line required | No rule for fabricated references. |
| P10 tests as truth | Candidate-copy mutation, failure-path test | Fix-wave test fails when reverted | Aligned. |
| P11 deterministic first, rules from recurrences | Runbooks are greps and commands | n/a | No loop from a recurring finding to a lint rule or MAP.md gotcha. |
| P12 measure | None | Refuted count in the record; blind re-check samples verifier accuracy | No tally across audits; no negative-control pressure case. |
