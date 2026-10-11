# Independent recovery hash review

Reviewer: compatibility delegate; root implemented the latest SHA-utility fixes.
Inspected current helper and root regression. Independent real subprocess probes
used a PATH-local `shasum` shim that fails only for selected stdin content and
otherwise delegates to `/usr/bin/shasum`:

- Source-file content matching `^# Decisions`: snapshot exit1, no VERIFIED;
  original complete byte/mode manifest unchanged.
- Recovery-runtime content matching `^# Explicit recovery operations only`:
  snapshot exit1, no VERIFIED; original manifest unchanged.
- Existing verified backup, identity content matching `^project=`: verification
  exit1 with the original nonempty digest sidecar.
- Same last probe after truncating `identity.sha256` to empty: verification exit0.

The fourth result is a remaining masking defect: `verified_backup` compares
`"$(digest identity.txt)"` directly with the stored sidecar, so a failed digest with
empty stdout equals an empty stored digest. This is corruption plus selective
utility failure, not a claim that an attacker controlling a trusted hash executable
can be prevented from inventing a plausible digest. Fix explicit hash-error
propagation for metadata too, and validate stored digest length/hex before comparing.

Reproducer uses only a disposable Recovery fixture, calls its ordinary snapshot
first, writes empty `backup/identity.sha256`, then invokes real
`bash scripts/itworks-recovery.sh verify-before-write PROJECT BACKUP` with shim:

```sh
#!/bin/bash
set -eu
f=$(mktemp)
trap 'rm -f "$f"' EXIT
cat > "$f"
if grep -q '^project=' "$f"; then exit 42; fi
/usr/bin/shasum "$@" < "$f"
```

No product edits made by reviewer. Full relevant recovery suite running separately;
a green preexisting suite cannot overrule this independently reproduced issue.

Additional analogous utility-failure probe: PATH-local `stat` script containing
`#!/bin/bash` and `exit 42` yielded snapshot exit0 and VERIFIED=true, with source
unchanged. Mode values were empty because stat errors inside printf substitutions
were masked. Preservation is not fully verified if file modes cannot be read.
Request explicit mode assignment/error propagation plus valid octal-token checking
before emitting any manifest row. This finding does not claim source corruption;
it identifies incorrect success when required metadata evidence is unavailable.

Follow-up implementation assignment: after root independently reproduced the two
remaining findings, this delegate became implementer for their fixes. Therefore
subsequent delegate GREEN runs are implementation checks, not independent approval
of these new changes. Root retains both REDs and must review final correction.
Additional root final-inventory RED is also fixed by explicit status checks on
both source and staged inventories before equality. Targeted five checks PASS.

Resolved: root independently reviewed final checked substitutions and ran three
reported hash/mode/final-inventory regressions, all PASS (`u03-root-final-green.txt`).
Delegate full recovery suite: 40 PASS. Independent root verification, rather than
this delegate's change of role, supplies acceptance of the corrected implementation.
