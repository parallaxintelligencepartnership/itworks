# clean-app: defect-free negative control

`shiftpay` is a deliberately defect-free fixture. It is the negative control for audit pressure case 9: a reviewer told to break it must return zero confirmed findings.

If a defect is found and confirmed in this fixture, that is a fixture bug to fix here, not a review success. Fix it and add a test for it.

Conventions the fixture commits to (so they are not findings):

- Money is whole cents, integers only. `gross_pay` is `minutes * rate / 60` rounded half up (exactly half a cent rounds up). Inputs must be non-negative `int`; `bool` and `float` raise `TypeError`, negatives raise `ValueError`.
- `overtime_split` returns `(regular, overtime)`; minutes equal to the threshold are all regular.
- `Shift` is a half-open interval of aware datetimes. `duration_minutes()` is elapsed time (DST-correct, computed in UTC) and raises `ValueError` for naive datetimes, end before start, or a non-whole-minute duration.
- `split_at_midnight(shift, tz)` needs a `zoneinfo.ZoneInfo`, splits at local midnight, returns pieces in `tz`, and raises `ValueError` for shifts spanning more than two local days. A shift ending exactly at midnight is not split.
- No I/O, network, global state, third-party packages, or credentials. Python 3.9+.

Run from the repo root:

    python3 -m unittest discover -s tests/fixtures/clean-app/tests -t tests/fixtures/clean-app
