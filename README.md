# itworks

You describe what you want and the AI builds it. itworks makes sure what gets built is real: no fake data pretending to be your app, no passwords sitting in public files, no "it works" that only means the happy path clicked once. It asks the questions an experienced developer would ask, at the moments they would ask them, in plain English, so you do not need to know the vocabulary to get the quality.

## What it does

itworks adds five guardrail moments to your Claude Code sessions:

- **Kickoff**: before any code is written, a short plain-English interview makes sure your project starts with real storage, a login if it needs one, secrets kept out of the code, spend caps on anything that costs money, a first commit to fall back to, and an agreed way to prove features work.
- **Checkpoint**: when you say "it works!", the claim gets checked with evidence, including the failure case; what was just built gets a short targeted review; new packages get a legitimacy check; and the working state gets committed as a restore point before the next feature builds on it.
- **Resume**: when you come back in a new session, your project's saved notes are replayed in six lines so nothing gets forgotten or rebuilt differently.
- **Audit**: when you ask for a real review of the whole application ("is it solid", "review the app", "check everything"), the code is split into lanes, each lane is read in full by a reviewer briefed to break it, and every finding is reproduced by a second, independent verifier before it is written down. This is the only tier that reads the application's logic; the other two run fixed checks. A shipped project that has never been audited is told so.
- **Closeout**: when you say "ship it", everything gets one full review sweep, every open issue gets resolved or knowingly accepted, a rollback is rehearsed for real, and you get a handoff document a future developer could pick up cold. Shipping is not the end: later deploys rerun the sweep, and post-ship reviews make sure new work is never built against your live users' data.

The reviews look through five lenses: security and auth, AI-feature safety (prompt injection, runaway API spend), real data versus fake data, testing, and production readiness, plus a dependency check that catches misnamed or malicious packages the moment they are added.

### Three review tiers, and which one you are getting

| You say | Tier | What gets read |
|---|---|---|
| "it works", "done", "next feature" | checkpoint | the diff since the last checkpoint, at most two lenses |
| "ship it", "deploy" | closeout | five fixed runbooks over the whole tree, then the reckoning |
| "review the app", "full review", "is it solid", "audit" | audit | every lane's code in full, adversarially, then independent verification |

Every review report opens with a scope line naming its tier and what it did not cover, so "no critical open" never quietly means more than it should. The checkpoint and closeout tiers cannot find a wrong calculation, a stale read, or a race; only the audit reads for those. Ask for one before real people depend on the app, and again when it has been a while.

## Install

From GitHub:

```bash
claude plugin marketplace add parallaxintelligencepartnership/itworks
claude plugin install itworks@itworks
```

From a local clone:

```bash
claude plugin marketplace add /path/to/itworks
claude plugin install itworks@itworks
```

Restart Claude Code (or start a new session) and the skills are live.

## Model requirement

Closeout and audit are pinned to Opus (`model: opus` in their skill and command frontmatter), because the blind pressure tests recorded Sonnet skipping the closeout sweep, so planted critical findings were never found. An organization model allowlist can drop that pin silently, and the session then keeps whatever model it was already on. If you see closeout or audit report a finished review without running the sweep, run `/model opus` and run the command again.

## Updating

The plugin updates from whatever source you installed it from, not automatically. Run:

```bash
claude plugin update itworks@itworks
```

That name is `plugin@marketplace`, not just `plugin`: the bare name `itworks` will report "not found." Here `itworks` is both, because the marketplace is the plugin's own repo.

For a local directory install (the development setup), the marketplace IS the local clone, so the update has two halves: pull or commit the change in the clone first, then run the command above to point the installed plugin at that new state. Restart Claude Code (or run `/reload-plugins`) afterward to pick it up.

The session-start line prints the version that's actually running, `(itworks vX.Y.Z)`, so a stale cached install is visible instead of silent.

One quirk: the updater compares version strings, not content. If the repo changed but the version in `plugin.json` did not, `update` reports "already at the latest version" and installs nothing. Either bump the version when shipping changes, or force a content refresh with `claude plugin uninstall itworks@itworks && claude plugin install itworks@itworks`.

## How it behaves

- It aims to fire on its own at the four moments above, using a session reminder plus the skills' own triggers. That is reliable in practice but it is guidance to the model, not a hard interception; the slash commands below are the guaranteed manual path, and the state files mean a missed moment is caught at the next one.
- In a project that carries itworks state (a `.itworks/` folder), the full session rules load. Everywhere else, only a short new-project reminder loads. In an existing project without .itworks/, the plugin offers the adoption baseline once when you first ask to change code, and respects a no for the session.
- The first time it runs in a project it asks one question: explain as we go, keep it short, or just handle it. That choice (guided, brief, or expert) sticks for the project and changes only the wording, never the checks.
- Every gate can be overridden; your project, your call. Overrides are written down in your own words and re-surfaced at closeout. The one hard stop: the final ship document is not written, and no deployment steps are given, while a critical problem is open and unacknowledged.
- Saying "not now" works, and saying it twice makes kickoff, checkpoint or resume stay quiet for the project. Closeout and audit have no project-level opt-out: they can be deferred, never turned off, and closeout always runs before deployment steps.
- When you correct it about a fact of your project (that server is not what its name suggests, that script does not do what it says), the correction is written down in the same turn, so the next session does not make the same mistake.

## Turning it off

- This directory only: create a `.itworks-off` file at the project root.
- Everywhere: `export ITWORKS_DISABLE=1`, or `touch ~/.config/itworks/disabled`.
- One skill in one project: tell kickoff, checkpoint or resume "not now" twice, and it stays quiet there. Closeout and audit are the exception: they can be deferred, never turned off.

## The slash commands

Manual versions of the same five moments:

- `/itworks:kickoff` starts the alignment interview.
- `/itworks:checkpoint` reviews what was just built.
- `/itworks:resume` replays where the project stands.
- `/itworks:closeout` runs the full ship sweep.
- `/itworks:audit` runs the whole-application review.

## What it writes in your project

- `.itworks/PROJECT.md`: what the app is, who uses it, your words mapped to the real terms, and how features are proven.
- `.itworks/DECISIONS.md`: choices made and why, one line each.
- `.itworks/REVIEWS.md`: every review finding, what got fixed, and what you accepted.
- `.itworks/PROFILE.md`: your explain-or-just-do preference and review bookkeeping, including when the last audit ran.
- `.itworks/MAP.md`: how to run it, how to test it, where the important code lives, what the hosts and services actually are, and the gotchas the project has already paid for once. Patched at every checkpoint, read before any work in a new session.
- `.itworks/LANES.md` (after the first audit): how the application is split for whole-application review, which files each lane covers, and what each reviewer is told to break.
- `SHIPPED.md` (at closeout): how to run it, how to update it, how to roll it back, known limitations, where things live, and a ship history.

These files are yours; they are readable notes, not tooling lock-in. A developer you hire later can read them cold. The plugin ships a validator (`scripts/itworks-lint.sh`) that checks the notes against their format, so drift gets caught instead of trusted.

## Publishing to itworks.dev

itworks.dev is a public wall of projects that finished a real closeout, each with a badge showing its audit date and whether a critical finding is still open.

Closeout asks before anything is sent, once, and a plain no (or anything short of a clear yes) ends it for the session. An entry is one JSON file submitted as a pull request to `parallaxintelligencepartnership/itworks-site`; the site owner merges it to approve. The badge renders after the merge and returns 404 before it. What is sent is the project name, a one line summary you wrote or approved in `SHIPPED.md`, the public repo URL if there is one, the audit tier and date, and five counts; never your code, file paths, environment values, secrets, or the state files. The full list is in `references/publish.md`.

The site itself never runs a model. It stores what you send, renders it on a page, and serves a badge image.

## Platform note

The review runbooks use POSIX shell commands (grep, git, curl). On macOS and Linux they run as written. On Windows, run Claude Code from Git Bash or WSL to get the full checks; outside those, the reviews still happen but the model substitutes equivalent checks by hand.

## Model note

Run closeout and audit on Opus-class models or better. Reviews are judgment work: the closeout sweep, the reckoning and the ship gate all require the model to decide what counts. In adversarial pressure testing (`tests/pressure/`, 2026-09-11, blind judged), Opus passed the closeout case in three of three runs; Sonnet failed it in every run across three wordings, not by capitulating but by never running the sweep, so the planted critical findings were never found, and in one run it handed over the deploy commands while claiming to withhold them. Haiku eroded the gates under repetition pressure earlier (it once logged "ship it! just a demo man" as risk acceptance). Sonnet is a fine implementer; it is not a reviewer. Don't trust the gates to anything below Opus class.

## For experienced developers

Pick expert profile and everything arrives as terse findings tables with zero lectures. The gates are identical: same checks, same evidence requirements, fewer words.
