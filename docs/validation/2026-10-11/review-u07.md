# Independent U07 matrix review

Reviewer: compatibility delegate; did not implement matrix validator or initial
matrix tests. Read actual `tests/support/validate_release_matrix.py` and
`tests/unit/test_release_matrix.py`; ran maintained suite: 5 PASS before adding
review regression. Inspected CLI: it reads JSON/evidence and prints a readiness or
BLOCKED result, without subprocess, publication, installation, or filesystem writes.
It does not claim approval is already granted; PASS means ready for explicit approval.

Independent real CLI probes (disposable evidence/matrices):

| Probe | Observed result |
|---|---|
| Required NOT RUN | exit1, identity: NOT RUN |
| Missing required process cell | exit1, missing required cells: process |
| Wrong candidate identity | exit1, identity: candidate mismatch |
| Wrong evidence hash | exit1, identity: evidence hash mismatch |
| Skipped=1 under PASS | exit1, missing, failed or skipped checks |
| Missing evidence file | exit1, identity: missing evidence |
| Symlinked evidence | direct validator ValueError: linked evidence |

Finding: failure/skip counts used equality against zero without exact integer type
validation. `failed=False, skipped=0.0` passed the matrix. This is a schema-validation
loophole, not evidence that a positive skipped count bypasses the gate. Added two
independent regression assertions in
`test_review_failure_and_skip_counts_require_integers`; recorded real intended
assertion failures in `u07-review-red.txt`. Root owns the implementation correction.
Recheck all count types exactly as integers; retain passed>=1/failed=0/skipped=0.

Limit: a matrix validator authenticates neither human review nor truth of arbitrary
log prose. Its claims depend on independently reviewed real evidence per cell;
hashes bind bytes and identity, not the truth of a forged status. No live host,
Linux or paid-model qualification was performed by this review.

Resolved: root changed all three counters to require exact integer types. Independent
rerun: matrix suite 6 PASS; separate direct probes for `failed=False` and
`skipped=0.0` both raise ValueError with `missing, failed or skipped checks`.
No outstanding behavioral finding from this matrix review. This does not turn
missing real platform/host/process evidence into PASS.
