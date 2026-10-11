# State format: the `.itworks/` directory

Contracts for the `.itworks/` state directory. Skills read these files at start and update them at end. `project-resume` validates against this document and rebuilds on mismatch.

All five files live in `.itworks/` at the project root. They are plain, readable notes that belong to the user, written so a future developer (or the user themselves) can read them without any tooling. Four of them hold intent and judgment (PROJECT, DECISIONS, REVIEWS, PROFILE); the fifth, MAP.md, holds the facts about the code and its environment that a fresh session would otherwise re-derive or guess.

**Current format version: 3.** PROFILE.md carries `format_version: 3`. Files without the field are version 1; version 2 states lack MAP.md. The migrations are adding the field, adding the `llm-security` lens_debt key, and writing MAP.md from the tree and the README; resume does all three in passing. Older states are never treated as corrupt for lacking newer fields.

**Deterministic validation:** the plugin ships `scripts/itworks-lint.sh`. When a shell is available, run it (`bash <plugin-root>/scripts/itworks-lint.sh <project-root>`) instead of eyeballing the rules below; its errors are the contract violations, its warnings are drift worth mentioning but never corruption.

## PROJECT.md

```markdown
# Project: <name>

## What it is
<one or two sentences in the user's own words, then one sentence in precise terms>

## Who uses it
<just the user | the user plus known others | the public> - auth needed: <yes/no>; roles needed: <yes/no, list roles if yes>

## Terminology map
| Your words | Real term |
|---|---|
| "the login thing" | authentication |

## Stack
<languages, frameworks, database, hosting target - one line each>

## Data
Real data: <what> | Sample data: <what, and where it is seeded> | Sensitive: <yes/no, what>

## Where it will live
<local machine | LAN | internet> - exposure notes: <ports, domain if any> - paid services: <none | which APIs, and whether a spend cap + rate limit exist>

## Definition of done
<numbered list of user-confirmed outcomes>

## Verification expectations
For each feature: how success is proven AND what should happen when it fails.
| Feature | Success proof | Failure behavior |
|---|---|---|
```

## MAP.md

The code map and the gotcha list. PROJECT.md says what the project is for; MAP.md says where things are and how the project bites. Kickoff writes it (adoption mode fills it from the inventory; a new project fills in what the structure proposal already decided), every checkpoint patches it, resume replays one line from it and reads it whole before any work, and the audit derives its lanes from the Layout table.

```markdown
# Map

## Run
<the exact command that starts it locally, one line, then the env var NAMES it needs, never values>

## Test
<the exact command that runs the whole suite; the command for one test if it differs>

## Layout
| Path | What lives there |
|---|---|
| cmd/app/main.go | entry point, flag parsing, wiring |
| internal/store/ | all SQL; the only package that opens the database |

## Environment
<facts about where it runs that the code cannot show: what each host name actually is (architecture, OS), what fronts it, where the data volume is, which account deploys; one line each>

## Gotchas
- <YYYY-MM-DD> | <the trap, one sentence> | <how to avoid it>
```

Rules:

- **Layout is a map, not a listing.** One row per place a newcomer would need to find: entry points, where routes or commands are registered, where data is written, where secrets are read, where the tests live. A row per file is a listing, and nobody reads listings.
- **Gotchas are facts that already cost something.** An assumption that turned out wrong and caused a rework, a command that silently does the wrong thing, a name that misleads (a host called `pi3` that is an x86 server). A gotcha is written the moment the user corrects the assistant about the project or its environment, in the same turn, before the work continues. It is not a decision (there was no alternative to weigh) and not a finding (there is nothing to fix); it is a fact the next session must not rediscover the hard way.
- **Only checkable facts.** Every line can be verified against the tree or the environment. Intent goes in PROJECT.md, choices in DECISIONS.md, problems in REVIEWS.md.
- **Size cap: about 60 lines.** A map that needs scrolling is not read. When a row stops being true it is removed, never kept for history; git and DECISIONS.md carry history.
- **Names, never values.** The map says `DATABASE_URL` is needed; it never says what it is set to.

A state without MAP.md is a version 2 state: drift, never corruption. Resume writes the file from the tree and the README in passing and says so in half a line; that write reads for layout only, never for findings.

## LANES.md (optional)

Written the first time `project-audit` runs; the lane manifest for whole-application reviews. Shape and rules in `references/audit-method.md`. Its absence is never an error; the audit derives it.

## Archive (optional)

`REVIEWS.md` grows with every checkpoint. When it passes about 800 lines, sections in which every finding is checked and that hold no `### Accepted risks` entry may be moved verbatim into `.itworks/archive/REVIEWS-<first date>-to-<last date>.md`, oldest first, with one line left in REVIEWS.md under `## Archive` naming the file and its date range. Accepted risks and open findings never move; the reckoning and the lint read REVIEWS.md only. Archived text is never rewritten.

## DECISIONS.md

One line per decision, newest last. A decision line is the ruling and its reason, not the session that produced it: keep it under about 400 characters and put evidence, transcripts and verification detail in the project's docs with a path on the line. Resume reads this file whole at every session start; paragraphs here are paid for every time.

```markdown
# Decisions

- <YYYY-MM-DD> | <decision> | why: <reason> | instead of: <alternative considered>
```

## REVIEWS.md

Checkpoint sections are appended, never rewritten. Sanctioned section headings:

- `## Checkpoint <n> - <YYYY-MM-DD> - lenses: <lens-id, lens-id>` (normal checkpoints)
- `## Checkpoint <YYYY-MM-DD> - <context>` (date-numbered checkpoints; a letter suffix disambiguates two in one day, e.g. `2026-08-04b`)
- `## Baseline checkpoint - <YYYY-MM-DD> - <context>` (the adoption-mode baseline)
- `## Closeout sweep - <YYYY-MM-DD> - <context>` (closeout, including re-closeouts)
- `## Closeout - <YYYY-MM-DD> - <context>` (same thing, short form)
- `## Reopen review - <YYYY-MM-DD> - <context>` (a review that reopens shipped work)
- `## Audit - <YYYY-MM-DD> - <context>` (a whole-application audit, `project-audit`; carries a scope line, findings, `### Refuted`, `### Coverage gaps`)

Trailing text after each form is free. Any other `## ` heading is drift (lint warning), not corruption.

Finding lines follow a strict five-field grammar (the fields are: checkbox, severity, lens id, description, evidence to close):

`- [ ] SEVERITY | lens-id | description (file:line) | Evidence to close: <command or check>`

The `(file:line)` inside the description is included whenever the finding points at code, and omitted when it does not (for example, "no failure-path test for login"). Validation checks severity and lens id, not the presence of file:line.

Severity values, exact: `CRITICAL`, `IMPORTANT`, `ADVISORY`.
Lens ids, exact: `security-auth`, `llm-security`, `real-data`, `testing`, `production-readiness`.

A **deliberate deferral** (the user chose to leave it open) stays an OPEN finding: the deferral, whose call it was, and the date go in the description; the evidence-to-close field keeps the real check that would close it. Never park a deferral in the evidence field.

An **acceptance that leaves work outstanding** (accepted for this ship, remainder still real) is TWO lines: the original finding flipped to `[x] ... Accepted <date>: see Accepted risks`, plus a NEW open finding (usually IMPORTANT) for the remainder with its own evidence to close. One line cannot be both accepted and open.

```markdown
# Reviews

## Checkpoint <n> - <YYYY-MM-DD> - lenses: <lens-id, lens-id>
### Findings
- [ ] CRITICAL | security-auth | API key in client code (src/app.js:12) | Evidence to close: grep of client dirs and built bundle returns no key patterns
- [x] IMPORTANT | testing | no failure-path test for login | Closed <YYYY-MM-DD>: test_login_rejects_bad_password passes
- [x] CRITICAL | security-auth | API key in client code (public/app.js:1) | Accepted <YYYY-MM-DD>: see Accepted risks
### Accepted risks
- <YYYY-MM-DD> | <finding text> | User's words: "<verbatim>" | Revisit when: <condition or date>
```

Checked lines use `Closed <date>: <evidence>` or `Accepted <date>: see Accepted risks`. (`Verified <date>:` appears in older files as a synonym for Closed; readers accept it, writers use Closed.)

`Revisit when:` is required on every Accepted risks entry. It names the thing that would reopen the finding: a condition ("when an off-site storage target exists", "before the next public deploy") or a date. An acceptance is a decision made under today's constraints, and the condition is what makes it expire instead of being forgotten. If the user genuinely has no condition, the recorded default is `Revisit when: next closeout`. Entries written before this field existed lack it: that is drift (lint warning), not corruption; leave the user's words alone and add the field at the next reckoning that touches the entry.

## PROFILE.md

```markdown
# Profile

format_version: 3
profile: guided        # guided | brief | expert
                       # guided: plain words, each new term gets its glossary card, short explanations
                       # brief: one context line per item, terms named with a half-line gloss
                       # expert: terse tables and one-liners, no cards, no explanations
                       # The profile changes wording ONLY. Checks and gates never vary by profile.
opted_out: []          # skill names the user told to stop auto-firing for this project
last_checkpoint: <YYYY-MM-DD @<git short sha>, or none before the first checkpoint>
                       # the sha is what the cadence guard diffs against; date alone cannot measure a diff
last_audit: <YYYY-MM-DD @<git short sha>, or none>
                       # set only by project-audit after its REVIEWS.md section is written; resume and
                       # closeout read it to say whether a whole-application audit is due
lens_debt:             # checkpoints run since each lens last ran; checkpoint hard-fires a lens at 3
  security-auth: 0
  llm-security: 0      # stays 0 forever in projects with no LLM/AI feature; the lens self-gates
  real-data: 0
  testing: 0
  production-readiness: 0
```

`lens_debt` counts CHECKPOINTS, not features: each checkpoint resets the lenses that ran to 0 and increments every other lens by 1. At 3, checkpoint force-includes the lens.

## Validation rules

`project-resume` checks these before trusting state (prefer running `scripts/itworks-lint.sh`, which encodes exactly these):

1. PROJECT.md, DECISIONS.md, REVIEWS.md and PROFILE.md exist in `.itworks/` (a missing MAP.md is drift, see below).
2. `profile:` in PROFILE.md is exactly one of `guided`, `brief`, `expert`.
3. Every unchecked finding line in REVIEWS.md parses to the five-field grammar above, with a valid severity and lens id. Unchecked means still open; a fixed finding is checked with `Closed <date>: <evidence>`, an accepted one is checked with `Accepted <date>: see Accepted risks` (and its verbatim entry under Accepted risks).
4. PROJECT.md contains all eight section headings shown in its template.
5. If `SHIPPED.md` exists at the project root, no CRITICAL finding in REVIEWS.md is still unchecked. A ship record next to an open CRITICAL means the ship gate was recorded and the finding was never flipped.

REVIEWS.md and SHIPPED.md are two halves of one record, so when SHIPPED.md exists the lint also warns (drift, not corruption) when they disagree: SHIPPED.md lists OUTSTANDING work but no finding is open to track it; a CRITICAL or IMPORTANT finding is open but SHIPPED.md never says OUTSTANDING; a finding is Accepted but SHIPPED.md has no accepted risks section.

Drift that is NOT corruption (mention it, fix it in passing, never trigger a rebuild): missing `format_version` (v1 file; add it), missing `MAP.md` (v2 state; write it from the tree and the README, then set `format_version: 3`), a MAP.md missing one of its five headings or running past about 80 lines, missing `llm-security` lens_debt key (add at 0), missing `last_audit` (add as `none`), REVIEWS.md past the archive threshold, DECISIONS.md lines far past the length guide, checked lines missing a closure keyword, Accepted risks entries without `Revisit when:` (pre-field entries; add the condition when the entry is next walked), unsanctioned section headings, `last_checkpoint` without a sha.

On a real violation: do not trust the invalid values, do not crash, do not restart the full kickoff interview. Rebuild per the `project-resume` skill: scan the code, carry over every legible finding and accepted risk verbatim, confirm once with the user, rewrite valid files.
