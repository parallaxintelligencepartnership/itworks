# Offline patch tests

Run from the repository root with development Python 3 (standard library only):

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
/bin/bash -n scripts/itworks-lint.sh hooks/session-start.sh tests/pressure/harness/run-case.sh
```

The inherited bytecode setting prevents Python and nested test processes from writing cache files into the checkout. It does not modify Python configuration files.

The patch runtime remains shell/awk. Python is a test dependency only. Default suites use temporary synthetic projects, bounded subprocesses and real shell entry points. They do not run real model clients, require credentials, or access the network. Static instructions and mocked CLI checks do not qualify installed hosts or prove model adherence.

`unit/support.py` provides `REPO`, `run(args, cwd=None, env=None, timeout=15)`, `tree_snapshot(root)`, `git_snapshot(root)`, `build_state(root, version=3, shipped=True)` (returns `.itworks` path), and `StateProject` with `root`, `state`, `put(name, text)`, `lint()`. Arguments after `args` / `root` are keyword-only. Tree snapshots retain paths, modes, file hashes and symlink targets; Git snapshots add HEAD, index bytes and tracked/untracked status. Neither helper changes the caller's HOME or repository. Timeouts and setup errors are infrastructure failures, never intended regression RED.

`fixtures/state/v1`, `v2`, and `v3` are **synthetic contract controls**, not historical exports. Historical artifact qualification belongs to U01/U02 and must use pinned actual artifacts. Hook tests copy the actual script and replace only its global-disable path operand with a private fixture path; this makes opt-out controls deterministic without modifying HOME or global configuration. It is not installed-host evidence.

The historical audit reproducer is preserved unchanged. P01 assertions intentionally expose baseline defects and must merge together with dependent fixes; do not hide failures behind expectedFailure or claim an intentionally red required CI job is complete. CI defines Linux/macOS offline checks, with explicit `/bin/bash` for macOS Bash 3.2. A configured job is not evidence that either remote platform ran.
