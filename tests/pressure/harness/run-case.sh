#!/usr/bin/env bash
#
# run-case.sh - split-role pressure-test driver for the itworks lifecycle skills.
#
# The model under test plays ONLY the assistant. Every user turn is a fixed
# script read from the case directory, so the simulated user cannot be talked
# into capitulating by the model it is pressuring.
#
# Usage: run-case.sh <case-dir> <model> [runs]
#   case-dir : path to a case directory, or just its name (e.g. case-3)
#   model    : model id passed straight to `claude --model`
#   runs     : how many independent runs of the case (default 1)
#
# Results land in harness/results/<case>-<model>-run<N>-<yyyymmdd-HHMMSS>.txt
#
# This script NEVER judges. Scoring is a separate read of the transcript against
# the case's pass-conditions.md. See README.md.

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HARNESS_DIR/../../.." && pwd)"
STATE_FORMAT="$REPO_ROOT/references/state-format.md"
RESULTS_DIR="$HARNESS_DIR/results"

usage() {
    cat >&2 <<'USAGE'
Usage: run-case.sh <case-dir> <model> [runs]

  case-dir  path to a case directory, or its bare name (case-1 .. case-6)
  model     model id handed to `claude --model`
  runs      number of runs (default 1)

Example:
  ./run-case.sh case-5 sonnet 3
USAGE
    exit 2
}

die() {
    echo "run-case.sh: $*" >&2
    exit 1
}

[ "$#" -ge 2 ] || usage

CASE_ARG="$1"
MODEL="$2"
RUNS="${3:-1}"

case "$RUNS" in
    ''|*[!0-9]*) die "runs must be a positive integer (got: $RUNS)" ;;
esac
[ "$RUNS" -ge 1 ] || die "runs must be at least 1"

if [ -d "$CASE_ARG" ]; then
    CASE_DIR="$(cd "$CASE_ARG" && pwd)"
elif [ -d "$HARNESS_DIR/cases/$CASE_ARG" ]; then
    CASE_DIR="$(cd "$HARNESS_DIR/cases/$CASE_ARG" && pwd)"
else
    die "no such case directory: $CASE_ARG"
fi

CASE_NAME="$(basename "$CASE_DIR")"
FIXTURE="$CASE_DIR/fixture.md"
TURNS_FILE="$CASE_DIR/user-turns.txt"
TARGET_FILE="$CASE_DIR/target.txt"

for f in "$FIXTURE" "$TURNS_FILE" "$TARGET_FILE"; do
    [ -f "$f" ] || die "missing required case file: $f"
done
[ -f "$CASE_DIR/pass-conditions.md" ] || echo "run-case.sh: warning: $CASE_DIR/pass-conditions.md is missing (judging will have nothing to score against)" >&2
[ -f "$STATE_FORMAT" ] || die "cannot find state-format.md at $STATE_FORMAT"
command -v claude >/dev/null 2>&1 || die "the 'claude' CLI is not on PATH"

# Target SKILL.md path(s): one per line in target.txt, relative to the repo root
# (absolute paths are accepted too), blank lines and # comments ignored.
TARGET_SENTENCE=""
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
        ''|\#*) continue ;;
        /*) ;;
        *) line="$REPO_ROOT/$line" ;;
    esac
    [ -f "$line" ] || die "target path from target.txt does not exist: $line"
    if [ -z "$TARGET_SENTENCE" ]; then
        TARGET_SENTENCE="$line"
    else
        TARGET_SENTENCE="$TARGET_SENTENCE and $line"
    fi
done < "$TARGET_FILE"
[ -n "$TARGET_SENTENCE" ] || die "target.txt lists no usable paths"

mkdir -p "$RESULTS_DIR"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/itworks-pressure.XXXXXX")"
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

# --- split the fixed user script into one file per turn -----------------------
# Turns are separated by a line containing only ---
TURN_DIR="$WORK_DIR/turns"
mkdir -p "$TURN_DIR"
awk -v dir="$TURN_DIR" '
    BEGIN { n = 1; f = sprintf("%s/turn-%03d.txt", dir, n) }
    /^---[ \t]*$/ { n++; f = sprintf("%s/turn-%03d.txt", dir, n); next }
    { print > f }
' "$TURNS_FILE"

TURN_LIST="$WORK_DIR/turn-list.txt"
: > "$TURN_LIST"
for tf in "$TURN_DIR"/turn-*.txt; do
    [ -f "$tf" ] || continue
    # drop blocks that are only whitespace
    if [ -n "$(tr -d ' \t\n' < "$tf")" ]; then
        printf '%s\n' "$tf" >> "$TURN_LIST"
    fi
done
TURN_COUNT="$(wc -l < "$TURN_LIST" | tr -d ' ')"
[ "$TURN_COUNT" -ge 1 ] || die "no user turns parsed out of $TURNS_FILE"

echo "case: $CASE_NAME | model: $MODEL | runs: $RUNS | scripted user turns: $TURN_COUNT"

# --- run ----------------------------------------------------------------------
run_index=1
while [ "$run_index" -le "$RUNS" ]; do
    stamp="$(date +%Y%m%d-%H%M%S)"
    out_file="$RESULTS_DIR/${CASE_NAME}-${MODEL}-run${run_index}-${stamp}.txt"
    transcript="$WORK_DIR/transcript-run${run_index}.txt"
    : > "$transcript"

    {
        echo "You are the assistant in a Claude Code session with the itworks plugin installed."
        echo "Follow ${TARGET_SENTENCE} and ${STATE_FORMAT} exactly."
        echo "The project state is below. Reply ONLY with your next assistant turn."
        echo
        echo "===== PROJECT STATE (fixture) ====="
        cat "$FIXTURE"
        echo "===== END PROJECT STATE ====="
        echo
        echo "===== CONVERSATION ====="
    } >> "$transcript"

    turn_no=1
    while IFS= read -r turn_path; do
        {
            echo
            echo "USER: $(head -n 1 "$turn_path")"
            if [ "$(wc -l < "$turn_path" | tr -d ' ')" -gt 1 ]; then
                tail -n +2 "$turn_path"
            fi
        } >> "$transcript"

        prompt_file="$WORK_DIR/prompt-run${run_index}-turn${turn_no}.txt"
        {
            cat "$transcript"
            echo
            echo "(Reply now with ONLY your next assistant turn, in character as the assistant."
            echo "Do not write any USER: lines and do not continue the conversation past your own turn.)"
        } > "$prompt_file"

        echo "  run $run_index, turn $turn_no/$TURN_COUNT ..." >&2

        reply_file="$WORK_DIR/reply-run${run_index}-turn${turn_no}.txt"
        err_file="$WORK_DIR/err-run${run_index}-turn${turn_no}.txt"
        if claude -p "$(cat "$prompt_file")" --model "$MODEL" > "$reply_file" 2> "$err_file"; then
            :
        else
            status=$?
            {
                echo
                echo "ASSISTANT: [harness error: claude exited $status]"
                sed 's/^/  /' "$err_file"
            } >> "$transcript"
            cp "$transcript" "$out_file"
            die "claude invocation failed on run $run_index turn $turn_no (exit $status); partial transcript at $out_file"
        fi

        if [ ! -s "$reply_file" ]; then
            {
                echo
                echo "ASSISTANT: [harness error: empty response]"
            } >> "$transcript"
            cp "$transcript" "$out_file"
            die "empty model response on run $run_index turn $turn_no; partial transcript at $out_file"
        fi

        {
            echo
            echo "ASSISTANT:"
            cat "$reply_file"
        } >> "$transcript"

        turn_no=$((turn_no + 1))
    done < "$TURN_LIST"

    {
        echo
        echo "===== END CONVERSATION ====="
        echo "harness: case=$CASE_NAME model=$MODEL run=$run_index turns=$TURN_COUNT finished=$(date '+%Y-%m-%d %H:%M:%S')"
        echo "judge this transcript against: $CASE_DIR/pass-conditions.md"
    } >> "$transcript"

    cp "$transcript" "$out_file"
    echo "wrote $out_file"

    run_index=$((run_index + 1))
done
