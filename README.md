# itworks

**1.1.0 review calibration.** Every tier now says what counts as a finding, an empty review is a valid result, and audits record plausible-but-unreproduced items instead of stalling on them; see the [release note](docs/releases/1.1.0.md). Upgrading from 1.0.0: read the [1.0.1 upgrade advisory](docs/releases/1.0.1.md) before your next deploy.

You describe what you want and the AI builds it. itworks adds checks for common gaps: no fake data pretending to be your app, no passwords sitting in public files, no "it works" that only means the happy path clicked once. It asks the questions an experienced developer would ask, at the moments they would ask them, in plain English, so you do not need to know the vocabulary to get the quality.

## What it does

itworks adds five guardrail moments to your Claude Code sessions:

- **Kickoff**: before any code is written, a short plain-English interview makes sure your project starts with real storage, a login if it needs one, secrets kept out of the code, spend caps on anything that costs money, a first commit to fall back to, and an agreed way to prove features work.
- **Checkpoint**: when you say "it works!", the claim gets checked with evidence, including the failure case; what was just built gets a short targeted review; new packages get a legitimacy check; and an authorized restore point includes only reviewed task-owned paths; unrelated work and credential material stay out.
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

Every review report opens with a scope line naming its tier and what it did not cover, so "no critical open" never quietly means more than it should.

### How findings are calibrated

A model asked to find problems will find some, so every reviewer itworks launches is told what counts. Checkpoint and closeout report only what a runbook step and its rubric name, and a clean command is recorded as clean rather than dressed up. The audit's reviewers surface every suspicion with a concrete trigger and who can reach it, and an independent verifier then confirms, refutes with the guard quoted, or records it as plausible with the probe that would settle it; an empty report with a full coverage list is a complete report. The rules are in [references/review-calibration.md](references/review-calibration.md). The checkpoint and closeout tiers cannot find a wrong calculation, a stale read, or a race; only the audit reads for those. Ask for one before real people depend on the app, and again when it has been a while.

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

## Model configuration

Closeout and audit retain `model: opus` in skill/command frontmatter. This is
configuration, not proof of reviewer fitness. The historical simulations had
limited samples, incomplete model identities and harness limitations; see the
[corrected evidence note](docs/releases/1.0.1.md#historical-model-evidence).
Always check the actual commands, observations and coverage in a review.

## Updating

Run `claude plugin marketplace update itworks` then
`claude plugin update itworks@itworks`, and start a new session. The session-start
message should report the new version. 1.0.1 was checked on Claude Code 2.1.296
as a 1.0.0 to 1.0.1 cached upgrade with every installed file matching the release.
The [host smoke procedure](tests/host/claude-upgrade-smoke.md) lists the checks.

After an authorized update, start a fresh session, verify its session-start
version and loaded artifact path, then run the installed linter read-only:

```bash
bash "<installed-plugin-root>/scripts/itworks-lint.sh" "<project-root>"
```

Keep `.itworks`, accepted quotations and SHIPPED history. Newly detected malformed
findings need review before another deployment; they do not authorize erasing or
rebuilding user notes. See [upgrade recovery](references/upgrade-recovery.md)
before any repair. Do not uninstall/reinstall solely to force a green result.

## How it behaves

- It aims to fire on its own at the five moments above, using a session reminder plus the skills' own triggers. These are instructions to the host model, not hard interception. The slash commands are explicit entry points; their execution still requires evidence and coverage checks.
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

## Publishing to itworks.build

itworks.build is a public wall of projects that finished a real closeout, each with a badge showing its audit date and whether a critical finding is still open.

Closeout asks before anything is sent, once, and a plain no (or anything short of a clear yes) ends it for the session. An entry is one JSON file submitted as a pull request to `parallaxintelligencepartnership/itworks-site`; the site owner merges it to approve. The badge renders after the merge and returns 404 before it. What is sent is the project name, a one line summary you wrote or approved in `SHIPPED.md`, the public repo URL if there is one, the audit tier and date, and five counts; never your code, file paths, environment values, secrets, or the state files. The full list is in `references/publish.md`.

The site itself never runs a model. It stores what you send, renders it on a page, and serves a badge image.

## Platform and qualification

The patch runtime uses Bash 3.2+, POSIX awk and standard Unix tools. Python and
Go are developer test tools, not plugin runtime requirements. macOS and Linux
are the test matrix; a configured CI job is not evidence that it ran. See the
[release checklist](docs/release-checklist.md) for platform and host gaps.
Windows and other host adapters are not qualified by this patch.

## Model evidence

The September case5 wording-A record includes three Sonnet reruns where the sweep
ran. Other wording cells failed differently. Three reported Opus passes were
text-simulation smoke evidence, not a general audit guarantee. Exact effective
model versions were not retained reliably. No corrected live-host pass rate or
universal model-role recommendation is claimed by this candidate.

## For experienced developers

Pick expert profile and everything arrives as terse findings tables with zero lectures. The gates are identical: same checks, same evidence requirements, fewer words.
