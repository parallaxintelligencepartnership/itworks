#!/usr/bin/env bash
# Read-only state protocol. Runtime: Bash 3.2+, POSIX awk, find, mktemp, rm.
set -u
if [ "$#" -ne 2 ]; then printf 'usage: itworks-state.sh check|gate|counts <project-root>\n' >&2; exit 64; fi
case "$1" in check|gate|counts) op=$1 ;; *) printf 'unknown state operation\n' >&2; exit 64 ;; esac
fail() { printf 'FORMAT\t1\nERROR\tE_IO\t.itworks\t0\tState input unavailable or unsupported\nSUMMARY\t1\t0\t0\n'; exit 1; }
command -v awk >/dev/null 2>&1 || fail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || fail
cd -- "$2" 2>/dev/null || fail
[ -d .itworks ] || fail
files=()
for name in PROJECT.md DECISIONS.md REVIEWS.md PROFILE.md; do
  [ -f ".itworks/$name" ] && [ -r ".itworks/$name" ] || fail
  files+=("./.itworks/$name")
done
for name in .itworks/MAP.md SHIPPED.md; do
  if [ -e "$name" ] || [ -L "$name" ]; then [ -f "$name" ] && [ -r "$name" ] || fail; files+=("./$name"); fi
done
if [ "$op" = counts ] && { [ -e .itworks/archive ] || [ -L .itworks/archive ]; }; then
  [ -d .itworks/archive ] && [ ! -L .itworks/archive ] || fail
  inventory=$(mktemp "${TMPDIR:-/tmp}/itworks-state.XXXXXXXX") || fail
  trap 'rm -f -- "$inventory"' EXIT
  find ./.itworks/archive -print0 > "$inventory" || fail
  while IFS= read -r -d '' path; do
    case "$path" in *$'\n'*|*$'\r'*|*$'\t'*) fail ;; esac
    [ ! -L "$path" ] || fail
    if [ -d "$path" ]; then [ -r "$path" ] && [ -x "$path" ] || fail; continue; fi
    [ -f "$path" ] && [ -r "$path" ] || fail
    files+=("$path")
  done < "$inventory"
fi
ITWORKS_STATE_OP=$op awk -f "$script_dir/itworks-state.awk" "${files[@]}"
