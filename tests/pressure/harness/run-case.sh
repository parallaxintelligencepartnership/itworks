#!/usr/bin/env bash
# Developer-only text simulation. Never activates the installed plugin.
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo 'Usage: run-case.sh <case-dir> <model> [runs]' >&2
    exit 64
fi
bash "$HARNESS_DIR/host-preflight.sh"
exec python3 "$HARNESS_DIR/simulation.py" "$@"
