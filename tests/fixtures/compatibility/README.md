# Compatibility fixtures

These synthetic projects derive from the exact fenced Markdown templates in the
released `v1.0.0` specification. That release already documented format v3.
v1/v2 directories represent supported legacy *state shapes*, not imaginary
historical product binaries. Their omissions follow that immutable specification.

`manifest.json` freezes source commit/blob identities and SHA-256/lengths for every
fixture byte. `sources/` retains released and audited specification bytes.
`generate.py` extracts released templates and fills placeholders deterministically;
run it from a repository containing both historical objects to regenerate.
No credentials, real user state, or installed plugin data are used.

Each case declares check/gate/counts statuses and required stable diagnostic IDs.
An empty diagnostic list does not imply zero warnings except for `v3-valid`, whose
zero-warning summary is explicitly asserted. Counts describe lifetime aggregation
and are asserted only when the counts operation succeeds. Gate-blocked open
critical differs from structurally invalid syntax; ambiguous historical acceptance
is warning-only for check but cannot support strict gate/counts.

The parser tests copy each project to a temporary UTF-8 path containing spaces,
invoke all three real shell operations, and compare complete byte/mode snapshots.
CRLF and missing-final-newline variants are actual checked-in byte differences.
The accepted quotation and malformed critical prose are retained verbatim in
fixtures but must not be echoed into diagnostic output. Archive-only findings
exercise lifetime counts without contributing active gate findings.
