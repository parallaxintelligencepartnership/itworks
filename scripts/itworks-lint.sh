#!/usr/bin/env bash
# Read-only human rendering of the shared parser. Bash, awk and core Unix tools.
[ "$#" -le 1 ] || { printf 'usage: itworks-lint.sh [project-root]\n' >&2; exit 1; }
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 1
result=$(bash "$script_dir/itworks-state.sh" check "${1:-.}")
status=$?
printf '%s\n' "$result" | awk -F '\t' '
$1 == "FORMAT" && $2 == "1" { format=1; next }
$1 == "ERROR" || $1 == "WARN" { printf "%s: %s:%s [%s] %s\n", ($1=="WARN" ? "warn" : "ERROR"),$3,$4,$2,$5 }
$1 == "SUMMARY" && NF == 4 { printf "%d error(s), %d warning(s)\n",$2,$3; summary=1 }
END { if(!format || !summary) { print "ERROR: incomplete state protocol"; exit 1 } }' || exit 1
[ "$status" -eq 0 ]
