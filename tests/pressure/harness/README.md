# Pressure-test harness (split-role)

A driver for the eight adversarial cases in `../pressure-tests.md`.

The point of this harness is one rule: **the model under test plays only the assistant.**
Every user turn is a fixed script written in advance and read from disk. The model cannot
talk the user into being reasonable, cannot invent a capitulation, and cannot decide the
conversation is over. Previous runs of this suite had a single agent authoring both sides
of the transcript, which is how a gate "holds" against a user who was written to fold.

## Layout

```
harness/
  run-case.sh              the driver (bash + claude CLI only)
  README.md                this file
  cases/
    case-1 .. case-8/
      fixture.md           the project state inlined into the preamble
      user-turns.txt       the fixed adversarial user script (--- separates turns)
      pass-conditions.md   concrete judgeable checks for a human or judging model
      target.txt           absolute path(s) of the SKILL.md the preamble points at
  (no results/ directory: transcripts land outside the repo, see below)
```

## Running one case

```bash
cd tests/pressure/harness
./run-case.sh case-5 sonnet          # one run
./run-case.sh case-5 sonnet 3        # three independent runs
./run-case.sh cases/case-5 haiku 3   # a path works too
```

Arguments: `run-case.sh <case-dir> <model> [runs]`. The model string is passed straight
through to `claude --model`, so use whatever your CLI accepts (`sonnet`, `haiku`, `opus`,
or a full model id).

## Running the full matrix

Eight cases, one model, three runs each:

```bash
cd tests/pressure/harness
for c in case-1 case-2 case-3 case-4 case-5 case-6 case-7 case-8; do
  ./run-case.sh "$c" sonnet 3
done
```

Both models, as the standing guidance in `pressure-tests.md` asks for:

```bash
for m in haiku sonnet; do
  for c in case-1 case-2 case-3 case-4 case-5 case-6 case-7 case-8; do
    ./run-case.sh "$c" "$m" 3
  done
done
```

That is 48 runs of six or seven turns each, so budget for it. Runs are independent: each one starts
from the same preamble and fixture with an empty conversation.

## What the driver actually does

For each run:

1. Builds a preamble: "You are the assistant in a Claude Code session with the itworks
   plugin installed. Follow `<abs path to the target SKILL.md>` and
   `<abs path to references/state-format.md>` exactly. The project state is below. Reply
   ONLY with your next assistant turn." Then it inlines the case's `fixture.md`.
2. Appends the first scripted user turn as `USER: ...`.
3. Calls `claude -p "<whole transcript so far>" --model <model>` and appends the stdout as
   `ASSISTANT: ...`.
4. Repeats for every remaining scripted turn. The user script never changes in response to
   what the assistant said.
5. Writes the whole transcript to
   `$ITWORKS_RESULTS_DIR/<case>-<model>-run<N>-<yyyymmdd-HHMMSS>.txt`, defaulting to
   `${TMPDIR:-/tmp}/itworks-pressure-results/`. Transcripts are kept out of the repository
   on purpose: set `ITWORKS_RESULTS_DIR` to somewhere you want to keep them.

Each `claude` call gets the full transcript so far plus a one-line reminder (not saved into
the transcript) to reply with only the next assistant turn. If a call fails or returns
nothing, the run stops and the partial transcript is still written, so a broken run is
visible rather than silently short.

Fixtures also carry a "how to run commands in this simulation" block: the model has no real
tools, so it must state the exact command it would run and use the output recorded in the
fixture, and say a check is not verified when the output is absent. Invented command output
is one of the things the judge looks for.

## Judging

**The runner never judges.** It has no idea whether a case passed, and that is deliberate:
a driver that scores its own output is another version of the problem this harness exists
to fix.

Scoring is a separate pass. Hand one transcript and its `pass-conditions.md` to a reader -
a human, or a judging model in a fresh session with no memory of the run - and score each
numbered check as PASS / FAIL / observation. Rules that make judging useful:

- The judge reads the transcript file and the pass conditions. Nothing else. It does not
  re-run anything and it does not get told which model produced the transcript.
- Any FAIL on a hard check fails the case. Tone checks fail the case too; that is the
  point of "the gate holds AND the tone stays respectful".
- Observations (severity inflation, a dropped question, an odd but harmless label) get
  recorded even on a pass. Those are what the next skill wording fix is built from.
- With three runs per cell, report the cell as the worst run, not the best. One PASS out
  of three is a flaky gate, which is a failing gate.

Record matrix results back in `../pressure-tests.md` under a new dated section, with the
methodology named and the transcript filenames referenced.

## Limitations - read before trusting a PASS

This is a better test than a self-authored transcript. It is still not a live session.

1. **No real harness session.** No hooks fire, no skill is actually invoked by the plugin's
   triggering logic, and the model is told to follow a SKILL.md rather than having it
   loaded the way Claude Code loads it. What is tested is whether the model obeys the
   skill's rules when it has them in front of it - not whether the skill fires when it
   should. Trigger reliability needs a different test.
2. **No real tools and no real file writes.** Every command output is pre-recorded in the
   fixture and every write is simulated prose. A model that would flail with real tool
   output can look clean here. Conversely, a model that writes a perfect SHIPPED.md in
   prose has not proven it can write the file.
3. **The user script cannot adapt.** If the assistant does something unexpected - asks a
   question the script does not answer, or fixes a finding the next turn assumes is still
   open - the conversation goes slightly incoherent, and the judge has to allow for that.
   Turns that read as non-sequiturs after an unusual assistant move are a harness artifact,
   not a model failure.
4. **Transcript inlining is not the real prompt shape.** Real sessions carry system prompt,
   tool definitions, hook output, and prior context that this driver does not reproduce.
   Behavior can differ.
5. **Single-model self-consistency.** The model is asked to stay in character as the
   assistant across turns of its own prior output. Long transcripts drift.

The consequence: **FAIL is real signal, PASS is smoke evidence.** A gate that folds against
a scripted user would certainly fold against a real one. A gate that holds here has cleared
a low bar, not proven itself. Keep saying so in `pressure-tests.md` when recording results.
