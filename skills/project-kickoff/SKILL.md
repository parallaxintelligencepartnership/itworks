---
name: project-kickoff
description: Use when the user asks to build a new app, site, tool, bot, or script and no .itworks directory exists yet, or before writing the first code in any project without one. Also on /itworks:kickoff. Fires BEFORE any scaffolding, file creation, or code.
---

# Project Kickoff

## Overview

This skill runs a short alignment interview in plain English, records the answers as durable project state, and gates all coding on a confirmed summary. It exists because the most expensive mistakes in AI-assisted projects happen in the first ten minutes: no real storage, no auth where auth was needed, secrets in the code, and no agreed way to prove anything works.

<HARD-GATE>
Write NO code and create NO files except `.itworks/` until PROJECT.md exists and the user confirms the summary in their own words. This holds at every profile level.
</HARD-GATE>

## Step 0: Calibrate (only if `.itworks/PROFILE.md` is missing)

Ask exactly one question, in these words or very close:

> "Before we start: I can explain things as we go, keep explanations short, or just quietly handle things the professional way. Which do you want?"

Map the answer to `guided`, `brief`, or `expert` and write it to `.itworks/PROFILE.md` per `references/state-format.md` (read that file now if you have not). Do not re-ask in later sessions.

If the opening message already answers this plainly ("just handle it", "explain everything as you go"), do not ask again: state the inferred profile in half a line with an open correction ("Taking that as just-handle-it; say the word if you want explanations") and move on. Infer only from an explicit preference statement, never from apparent skill level: a hurried beginner also says "just build it," and they still need guided wording once things get technical.

## Step 1: Detect mode

- Empty or near-empty directory (no meaningful source files): **new project**. Continue to Step 2.
- Substantial code already present: **adoption mode**. Jump to the Adoption section below.

"Substantial" means any working entry point or more than stub files. When in doubt, pick adoption mode: its inventory is cheap and it degrades gracefully into the new-project flow if the code turns out to be nothing.

## Step 2: The interview

Ask these six questions, ONE per message, in plain words. Do not batch them for beginners. If an expert-profile user volunteers several answers at once, accept them and ask only what is still missing. In brief profile, when the user is visibly pushing on pace, closely related questions may be grouped (2-3 per message); all six still get answered.

Before the Step 5 playback, tick off all six against the answers actually given. Batched expert replies routinely skip one (usually roles, question 3, or paid services in question 5); the missing ones get asked, never assumed from the stack or the vibe.

1. What should it do, in one sentence?
2. Who uses it: just you, or others too?
3. Do different people need to see or do different things?
4. What information does it hold, and is any of it real or sensitive?
5. Where will it live: your machine, or the internet? And will it use paid services (AI, payments, texting, maps)?
6. What does "done" look like, and how would we prove a feature works, including what should happen when it fails?

Question 2 decides whether authentication matters. Question 3 decides whether roles matter. Question 4 decides how carefully data and secrets are handled. Question 5 decides exposure AND whether spend caps and rate limits are required from day one: an app that calls a paid service from a public page with no cap is a surprise bill waiting to happen. Question 6 fills the Verification expectations table, and it is not optional: every feature gets a success proof AND a failure behavior before it is built.

## Step 3: Translate and record

Write all five state files per `references/state-format.md`. MAP.md at kickoff holds what is already known: the run and test commands the Step 4 structure proposal settles on, and the environment facts the interview surfaced (the host from question 5, and what that host actually is). Its Layout table fills in at the first checkpoint, once the scaffold exists. Build the terminology map from the user's actual phrases: if they said "the login thing," that exact phrase goes in the map next to "authentication."

In guided profile, introduce each new term with its two-line card from `references/glossary.md` the first time it naturally comes up, including mid-interview (at most one card per message during the interview, so questions stay questions). In brief profile, name the term with a half-line gloss. In expert profile, just use the term.

Propose a working project name from the user's own description; it gets confirmed as part of the Step 5 playback, not with its own question.

## Step 4: Structure proposal

Step 4 is PROPOSAL ONLY. Nothing here is executed (no git init, no files, no harness) until the Step 5 confirmation lands; the gate covers all of it. Propose the real structure the answers imply, at profile depth:

- A frontend/backend split where the answers warrant one (others use it, data is shared, or it lives on the internet).
- Real persistence from the first feature. Never "we'll wire the database later": later is when the fake data has already fooled everyone.
- Secrets in environment variables from the first commit, with `.env` in `.gitignore` before any key exists to leak.
- git initialized before the first file, if it is not already, and the scaffold committed the moment it exists: that first commit is the first restore point, and every checkpoint adds another. An AI rewrite gone wrong with no committed base is how beginners lose working apps.
- Dependencies pinned to exact versions with the lockfile committed, from the very first install. New packages get the quick legitimacy check in `references/dependency-vetting.md` before they land; AI-suggested package names are sometimes wrong or actively malicious, and the check is cheaper than the incident.
- If paid services are involved (question 5): a spend cap set at the provider and a rate limit on any route that triggers paid calls, from the first such route, not later.
- A test harness scaffolded with one passing test and one intentionally failing test. Run both, show the failure being reported, then fix the failing one. This proves the harness can actually catch problems, which is the whole point of having it.

## Step 5: Confirm gate

Play the summary back in the user's own vocabulary (use the terminology map). Proceed only on explicit confirmation. Log the confirmation in `DECISIONS.md`:

`- <date> | kickoff confirmed: <one-line summary> | why: user approved the played-back summary | instead of: n/a`

**Versioning rule, stated in the same playback.** This is part of the summary, not a seventh question: the playback names the default and invites a change, and confirming the summary confirms it. The default is: builds and patches move as work ships, minor and major bumps only when the user says so. Nothing ever renumbers a release on the assistant's own initiative. Wording follows profile:

- `guided`: "One more thing I'll assume unless you tell me otherwise: the small build number can tick up as we ship, but the version people see only changes when you say so. Change that if you want it different."
- `brief`: "Versioning: builds and patches move as work ships, minor and major bumps only when you say so. Change that if you want it different."
- `expert`: "Versioning: build/patch auto, minor/major on your word. Say if you run a different scheme."

If the user names their own scheme (CalVer, date tags, no versions at all), that is the rule; record it in their words. Write the confirmed rule to `DECISIONS.md` alongside the kickoff-confirmed line:

`- <date> | versioning: <rule> | why: kickoff default accepted / user's own scheme | instead of: ad-hoc bumps`

## Adoption mode (existing code, no `.itworks/`)

1. **Inventory first, questions second.** List the tree, read the entry points, detect the stack, and run the tracked-secrets check from `references/lens-security-auth.md` (inspect step 3). Write the inventory into `MAP.md` as it is taken (Run, Test, Layout, Environment), so it survives the session instead of evaporating into the transcript. The code answers most interview questions; asking the user things the code already answers wastes their trust.
2. Ask only the questions the code cannot answer (usually: who uses it, is the data real, where will it live, what does done look like).
3. Write the remaining four state files, reverse-engineered from code plus answers, then play the summary back and get confirmation exactly as in Step 5. The HARD-GATE applies in adoption mode too.
4. **Run a baseline checkpoint immediately** (after the confirmation): follow `skills/project-checkpoint` behavior with ALL lenses at brief length (every `lens-*.md` in `references/`; a lens whose "Fires when" condition is absent records one "not applicable" line), plus `references/dependency-vetting.md` over the existing dependency list. Findings go into `REVIEWS.md` under a `## Baseline checkpoint` heading. This baseline is one of the two sanctioned exceptions to checkpoint's two-lens cap. This is where already-shipped problems surface, and they surface now, before new work is stacked on top of them.
5. Present the baseline findings BEFORE starting whatever feature the user asked for. A CRITICAL found in baseline blocks the new feature until fixed or accepted in writing, same as any checkpoint.

## Rationalization table

| Thought | Reality |
|---------|---------|
| "The user is in a hurry" | The interview is six questions. Rework is slower. |
| "They said make no mistakes, so build carefully" | Careful building on wrong assumptions is still wrong. Ask first. |
| "This project is too simple to need it" | Simple projects ship the worst secrets. Run it. |
| "They're clearly an expert" | Experts get expert profile, not skipped gates. |
| "I'll just scaffold while we talk" | Scaffolding IS code. The gate says no. |

## "Not now"

If the user declines, suppress this skill for the rest of the session and say so in one line. On a second opt-out in the same project, add `project-kickoff` to `opted_out` in `PROFILE.md` and tell them it will stay quiet and can be run any time with `/itworks:kickoff`.
