#!/usr/bin/env bash
# No invocation, authentication discovery, config copying or mutation on failure.
set -euo pipefail
case "${ITWORKS_HARNESS_MODE:-live}" in
    mock)
        if [ -z "${ITWORKS_MOCK_CONFIG:-}" ] || [ ! -f "$ITWORKS_MOCK_CONFIG" ]; then
            echo 'preflight: mock mode requires ITWORKS_MOCK_CONFIG JSON; no real CLI is invoked' >&2
            exit 64
        fi
        command -v python3 >/dev/null || { echo 'preflight: developer Python 3 required' >&2; exit 69; }
        ;;
    *)
        echo 'preflight: BLOCKED unsupported live host configuration; no model invoked.' >&2
        echo 'Provision a disposable OS account/VM, reviewed managed policy and authenticated transport,' >&2
        echo 'explicit request/turn/time/cost budget, then independently qualify the tool-denial canary.' >&2
        echo 'This candidate has no approved live adapter. See harness/README.md; mock mode is offline only.' >&2
        exit 69
        ;;
esac
