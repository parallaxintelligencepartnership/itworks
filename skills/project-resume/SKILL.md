---
name: project-resume
description: Use at the start of any session, or when a project is first mentioned, in a directory containing a .itworks directory, before doing any work in it. Also on /itworks:resume.
---

# Project Resume

## Overview

Read the saved state, replay where things stand in about six lines, ask one question, go. This prevents the most common way AI-assisted projects rot: a fresh session where the project gets re-described badly and a second, divergent implementation begins, while known problems are forgotten entirely.

## Step 1: Validate the state

Run the deterministic linter first: `bash <plugin-root>/scripts/itworks-lint.sh <project-root>` (the script lives in this plugin's `scripts/` directory, next to `skills/`). The plugin root is the directory above `skills/`; the loader reports the skill's base directory as `<plugin-root>/skills/<name>`. If no shell is available, check the Validation rules in `<plugin-root>/references/state-format.md` by hand (read it now if you have not):

1. PROJECT.md, DECISIONS.md, REVIEWS.md and PROFILE.md exist.
2. `profile:` is exactly one of `guided`, `brief`, `expert`.
3. Every unchecked finding line parses to the five-field grammar.
4. PROJECT.md has all eight section headings.

Linter ERRORS (or a hand-checked rule violation) → Rebuild section below. Linter WARNINGS are drift, not corruption: fix the mechanical ones silently in passing (add `format_version: 3`, add a missing `llm-security` lens_debt key at 0, add a missing sha to `last_checkpoint` at the next checkpoint) and continue to Step 2. A missing `MAP.md` is fixed in passing too: write it from the tree and the README per `<plugin-root>/references/state-format.md` (run and test commands, the layout table, environment facts, an empty Gotchas list), at most about 60 lines, reading for layout only and never for findings, and say so in half a line of the replay.

Then read `MAP.md` whole before anything else. Its Gotchas section is the list of mistakes this project has already paid for once; a session that repeats one of them has not resumed, it has restarted.

## Step 2: Replay

Use exactly this shape, filled from state, at the stored profile's tone:

```markdown
**<project name>** - <one-line what it is>
Last session: <last_checkpoint date + what DECISIONS.md says happened last>
Open: <n> CRITICAL (<short list>), <n> IMPORTANT, <n> ADVISORY
Accepted: <short description> - revisit when <condition>
Last audit: <date @sha, or never> (<due | current>)
Map: run `<Run command>`; <n> gotchas<, latest: <newest gotcha, a few words>>
Next was: <the next thing per DECISIONS.md/REVIEWS.md>
Continue there, or something new?
```

`Last audit` is due when the project holds other people's real data and no audit has run, or when SHIPPED.md exists and the audit is older than 60 days or more than 5 ship-history entries back; the line says "due" and nothing more (the audit skill decides what to do about it).

If a CRITICAL is open, append its one-sentence blocker status: what it is and why it blocks building on top. Do not bury it in the counts.

One `Accepted:` line per accepted CRITICAL or IMPORTANT still standing, from REVIEWS.md's Accepted risks. ADVISORY acceptances stay in the counts only. An accepted risk nobody ever sees again is a forgotten one, which is how a decision made for one afternoon quietly becomes permanent. If a revisit condition is already met (a dated condition now in the past, a named condition the project has since satisfied), the line says so and the finding is reopened as an open finding. Entries with no `Revisit when:` field predate it: replay them as "revisit when: not recorded".

"Next was" falls back in this order: an explicit next step in DECISIONS.md or REVIEWS.md, then the first unmet item in PROJECT.md's Definition of done, then leave the line as "Next was: not recorded" and let the one question settle it. Do not guess.

Ask nothing else. Do NOT re-ask anything PROJECT.md or MAP.md already answers; the whole point of the state is that the user never has to explain their project twice.

If the user's opening message already names new work ("add a search feature"), the replay still comes first, then the one question offers both paths: finish what was open, or start the new thing (with the CRITICAL's blocker status restated if one exists).

## Rebuild (invalid or hand-edited state)

Say plainly and calmly that the project notes do not match the expected format, with no scolding: the notes belong to the user and they are allowed to touch them.

1. Scan the code: stack, entry points, routes, storage. Re-derive the PROJECT.md facts the code can prove, and write the scan into MAP.md (carrying over any legible Gotchas from the old file verbatim).
2. Carry over every legible finding and accepted risk from the old files VERBATIM, including lines that do not parse. Rebuild the line's STRUCTURE (checkbox, severity, lens id) around the user's unchanged words; never invent content that was not there, and never fabricate a file:line (it is optional, so omit it unless your own code scan verified one). A line whose severity token is still legible keeps that severity: an unreadable line that still contains the token `CRITICAL` is written as `CRITICAL` with "pending re-review" appended inside the description text. Only a line with no legible severity token at all is guessed, and that guess is written as the bare token `ADVISORY` with "severity best-guess, pending re-review" appended inside the description text. Never downgrade a severity the line still states; downgrading silently opens the gate.
3. Ask ONE confirmation question: "Here is what I can tell from the code: <summary>. Right?" If any line's severity had to be guessed or was kept pending re-review, the same message lists each one in full and asks the user to confirm or correct its severity. A rebuild never changes a severity without saying which lines it touched. An invalid `profile:` is folded into this same question: default to `guided`, state the default plainly, and let the answer correct it. The code cannot prove a tone preference, so the question is the sanctioned place to recover it.
4. Rewrite all five files valid per `<plugin-root>/references/state-format.md`.

Never rerun the full kickoff interview. Never trust the invalid values (a `profile: fancy` is treated as unknown, not guessed). Never crash on a malformed line.

## "Not now"

If the user waves the replay off, compress it to one line ("Picking up <project>; 1 open CRITICAL still standing.") and proceed. Repeated opt-out: record `project-resume` in `opted_out` in `PROFILE.md`; `/itworks:resume` re-enables any time.
