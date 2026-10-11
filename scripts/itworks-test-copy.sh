#!/usr/bin/env bash
# Explicit candidate inventory; Bash 3.2 / core Unix only. Does not execute tests.
set -euo pipefail
umask 077
fail() { printf '%s\n' 'candidate copy failed: unsupported input or identity changed' >&2; exit 1; }
[ "$#" -eq 2 ] || fail
root=$(cd -- "$1" && pwd -P) || fail
manifest=$2
[ -f "$manifest" ] && [ ! -L "$manifest" ] || fail
if command -v shasum >/dev/null 2>&1; then raw_hash() { shasum -a 256 < "$1"; }
elif command -v sha256sum >/dev/null 2>&1; then raw_hash() { sha256sum < "$1"; }
else fail; fi
hash() {
  local value
  value=$(raw_hash "$1" | awk '{print $1}') || return 1
  [ "${#value}" -eq 64 ] || return 1
  case "$value" in *[!0123456789abcdefABCDEF]*) return 1 ;; esac
  printf '%s\n' "$value"
}
owned=$(mktemp -d "${TMPDIR:-/tmp}/itworks-copy.XXXXXXXX") || fail
complete=0
cleanup() { if [ "$complete" -ne 1 ]; then rm -rf -- "$owned"; fi; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir "$owned/candidate"
paths=()
while IFS= read -r -d '' path; do
  case "$path" in ''|/*|.|..|./*|../*|*/../*|*/..|*/./*|*/.|*//*|.git|.git/*|*/.git|*/.git/*|*$'\n'*|*$'\r'*|*$'\t'*) fail ;; esac
  for previous in "${paths[@]+${paths[@]}}"; do [ "$previous" != "$path" ] || fail; done
  paths+=("$path")
done < "$manifest"
# A non-NUL terminated final entry is invalid rather than silently omitted.
[ -z "${path:-}" ] || fail
[ "${#paths[@]}" -gt 0 ] || fail
safe_file() {
  local base=$1 relative=$2 cursor=$1 part
  while [ -n "$relative" ]; do
    part=${relative%%/*}
    cursor=$cursor/$part
    [ ! -L "$cursor" ] || fail
    if [ "$relative" = "$part" ]; then relative=''; else relative=${relative#*/}; fi
  done
  [ -f "$cursor" ] && [ -r "$cursor" ] || fail
}
if stat -f '%Lp' "$root" >/dev/null 2>&1; then
  mode() { stat -f '%Lp' "$1"; }
else
  mode() { stat -c '%a' "$1"; }
fi
inventory() {
  local base=$1 target=$2 path digest permissions
  : > "$target"
  for path in "${paths[@]}"; do
    safe_file "$base" "$path"
    digest=$(hash "$base/$path") || fail
    permissions=$(mode "$base/$path") || fail
    case "$permissions" in ''|*[!0-7]*) fail ;; esac
    [ "${#permissions}" -le 4 ] || fail
    printf '%s\t%s\t%s\n' "$path" "$permissions" "$digest" >> "$target"
  done
  LC_ALL=C sort "$target" > "$target.sorted"
  mv "$target.sorted" "$target"
}
safe_git() {
  GIT_OPTIONAL_LOCKS=0 git -c core.fsmonitor=false -C "$root" "$@"
}
git_identity() {
  local target=$1 index filter_status
  # Status may invoke clean/process filters even with optional locks disabled.
  # Read configuration keys only and refuse executable filters before status.
  if safe_git config --name-only --get-regexp '^filter\..*\.(clean|process)$' >/dev/null 2>&1; then
    fail
  else
    filter_status=$?
    [ "$filter_status" -eq 1 ] || fail
  fi
  safe_git rev-parse HEAD > "$target.head" || fail
  index=$(safe_git rev-parse --git-path index) || fail
  case "$index" in /*) ;; *) index=$root/$index ;; esac
  if [ -f "$index" ]; then hash "$index" > "$target.index" || fail; else printf 'absent\n' > "$target.index"; fi
  safe_git status --porcelain=v1 -z --untracked-files=all > "$target.status" || fail
}
inventory "$root" "$owned/before"
git_identity "$owned/before"
for path in "${paths[@]}"; do
  safe_file "$root" "$path"
  parent=${path%/*}
  [ "$parent" != "$path" ] || parent=.
  mkdir -p -- "$owned/candidate/$parent"
  cp -p -- "$root/$path" "$owned/candidate/$path" || fail
done
inventory "$root" "$owned/after"
git_identity "$owned/after"
inventory "$owned/candidate" "$owned/copied"
for suffix in '' .head .index .status; do cmp -s "$owned/before$suffix" "$owned/after$suffix" || fail; done
cmp -s "$owned/before" "$owned/copied" || fail
complete=1
printf '%s\n' "$owned/candidate"
