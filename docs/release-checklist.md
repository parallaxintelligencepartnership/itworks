# Compatibility patch release gates

Release remains blocked until required evidence is tied to one immutable
candidate. No skipped required cell can become PASS from a successful process
exit. Publishing, tags, installation and deployment require explicit authorization.

| Gate | Evidence required |
|---|---|
| Identity | Clean external candidate commit, version1.0.1, archive/file hashes, full v1.0.0-to-candidate diff review |
| Deterministic tests | Unit and integration suites on macOS and Linux, exact Bash/awk/Python/Go versions |
| Preservation | Real released/audited → candidate → old roundtrips, fixture hashes, candidate/index preservation |
| Recovery | Exact documented shell operations, fault/interrupt/concurrent-edit tests, verified independent backup |
| Correctness | Audit regressions, exact acceptance gates/counts, corrected executable overtime oracle |
| Simulation | Mock mechanics plus separately provisioned live canary; no fake transcript as observation |
| Installed Claude | Exact host/version/source-type fresh-session loaded bytes; local and cached paths separate |
| Workflow behavior | Independent isolated-host scenarios for secret/staging, closure evidence and lifecycle transitions |
| Performance | Shared benchmark5 warmups/30 measured trials, comparable runtime/workload identities, investigated regressions |
| Notes and process | Reviewed advisory, no unsupported claims, explicit deviations/remaining requirements |
| Approval | Explicit maintainer action for this exact qualified artifact; no automatic publishing |

Run from the frozen candidate repository, with `ITWORKS_CANDIDATE_SHA` set to its
full commit for strict artifact compatibility tests:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tests/unit -p 'test_*.py' -v
python3 -m unittest discover -s tests/integration -p 'test_*.py' -v
for file in scripts/*.sh hooks/*.sh tests/pressure/harness/*.sh; do /bin/bash -n "$file"; done
```

Build the external evidence artifact with `tests/support/build_release_evidence.py`.
Record each matrix cell with candidate, command, evidence hash, reviewer and
PASS/FAIL/BLOCKED/NOT RUN. Validate the matrix with
`tests/support/validate_release_matrix.py`; a required gap blocks eligibility.
The final bundle is external to the archive it hashes. Reuse a preliminary
benchmark only with explicitly identical runtime-file/workload/toolchain/platform
hashes and a documented old/final artifact association; otherwise rerun.

A copy is not an OS sandbox. Host qualification requires a disposable OS account
or VM, authorized credentials/budget and explicit installation permission. The
ordinary suites must never invoke real model or transport CLIs. Current host
instructions live in [tests/host](../tests/host/README.md).
