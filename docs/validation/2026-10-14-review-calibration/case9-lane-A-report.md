# Lane A review: shiftpay (shift timing and pay arithmetic)

Project: tests/fixtures/clean-app at 035640f (working tree), read-only. Mode: recall.
Python used for probes: 3.9.6 (system zoneinfo database).

## Suspicions

### A1. Nonexistent and ambiguous local wall times are accepted silently and resolved by `fold`, changing paid minutes

- Where: shiftpay/shifts.py:11-12 (`_is_aware`), :41-48 (`_validate`), :28-38 (`duration_minutes`), :55-78 (`split_at_midnight`). Nothing checks that an aware local time actually exists or is unambiguous in its zone.
- Input: a clock-out entered as `datetime(2026, 11, 1, 1, 30, tzinfo=ZoneInfo("America/New_York"))` for a shift starting 2026-10-31 22:00 NY. The default `fold=0` picks the first 01:30 (EDT). Probe: `duration_minutes()` returns 210; with `fold=1` (the 01:30 after fall-back, which is what a worker clocking out at the end of the night usually means) it returns 270. Same for spring-forward: end `2026-03-08 02:30` NY (a time that never existed) is accepted; `fold=0` gives 90 minutes from 01:00, `fold=1` gives 30. `split_at_midnight` on a shift starting at the nonexistent 02:30 silently returns a piece starting 03:30, so the stored start differs from what was entered.
- Wrong outcome: one hour of work lost or invented on the two DST nights, with no error, from wall-clock input. The duration invariant ("never silently ...") is met only in the narrow sense that the arithmetic on the chosen instants is exact; the choice of instant is silent.
- Reachable by: any caller that builds `Shift` from user-entered local clock times (the normal path for a time-clock or timesheet form) on 2026-03-08 or 2026-11-01 in America/New_York.
- Proposed severity: CRITICAL (wrong stored paid time for a real user, rare). Verifier may judge this a design choice; see question Q1.
- Lens: real-data
- Reproduction as a test: build `Shift(ny(2026,10,31,22), datetime(2026,11,1,1,30,tzinfo=NY))` and assert that `duration_minutes()` raises ValueError (or otherwise refuses an ambiguous wall time without an explicit fold); today it returns 210. Likewise assert `Shift(ny(2026,3,8,1), ny(2026,3,8,2,30)).duration_minutes()` raises ValueError for a nonexistent time; today it returns 90.

### A2. `Shift` equality and hashing compare wall time, so two different shifts in the fall-back hour are "equal", and a split piece is "not equal" to the shift it came from

- Where: shiftpay/shifts.py:15-20 (`@dataclass(frozen=True)` generates `__eq__`/`__hash__` from the raw datetimes) combined with shiftpay/shifts.py:70-78 (`split_at_midnight` re-expresses every piece in `tz`).
- Input 1: `a = Shift(datetime(2026,11,1,1,0,tzinfo=NY,fold=0), datetime(2026,11,1,1,45,tzinfo=NY,fold=0))` and `b` = same with `fold=1`. These are 05:00Z-05:45Z and 06:00Z-06:45Z, two different 45-minute shifts. Probe: `a == b` is True and `len({a, b}) == 1`. `split_at_midnight` produces exactly this pair from two distinct UTC-entered shifts (05:00Z-05:45Z and 06:00Z-06:45Z on 2026-11-01), so the library itself manufactures the collision.
- Input 2: `s = Shift(datetime(2026,11,1,5,30,tzinfo=UTC), datetime(2026,11,1,10,tzinfo=UTC))`; `split_at_midnight(s, NY)[0].start == s.start` is False although the instants are equal (inter-zone comparison of a time in the fold is always unequal under PEP 495). A caller checking that pieces concatenate to the original by `==` rejects a correct split.
- Wrong outcome: a caller that deduplicates, keys, or diff-checks shifts by `Shift` equality drops one real shift (lost pay) or flags a valid split as broken, only on the fall-back night.
- Reachable by: any caller storing shifts in a set/dict or comparing them for duplicates, with shifts in America/New_York on 2026-11-01 01:00-02:00 local.
- Proposed severity: IMPORTANT (wrong behavior from a normal use of a public value type; becomes lost money only through a caller's dedupe).
- Lens: real-data
- Reproduction as a test: assert `Shift(ny_fold0(2026,11,1,1,0), ny_fold0(2026,11,1,1,45)) != Shift(ny_fold1(2026,11,1,1,0), ny_fold1(2026,11,1,1,45))` (different instants must not compare equal); fails today. Assert `split_at_midnight(s, NY)[0].start == s.start` for the UTC-entered `s` above; fails today.

### A3. `Shift(...)` accepts naive datetimes; rejection happens only later, when a method is called

- Where: shiftpay/shifts.py:22-26 (`__post_init__` checks only `isinstance(..., datetime)`); awareness is checked in `_validate` (shifts.py:44-45), which runs only inside `duration_minutes` and `split_at_midnight`.
- Input: `Shift(datetime(2026,6,1,9), datetime(2026,6,1,17))` constructs without error (probe confirmed). The class docstring (shifts.py:17) says it is an interval "between two aware datetimes".
- Wrong outcome: a public constructor exported in `__all__` produces an invalid value that can be stored, queued or compared before anything rejects it; comparing it with an aware `Shift` silently returns False, and ordering its fields against aware datetimes raises TypeError far from the input. The invariant "every public function rejects naive datetimes" does not hold for the `Shift` constructor. Ends-before-start is also accepted at construction.
- Reachable by: a caller that builds Shifts from parsed input (for example an ISO string without an offset) and persists them before computing pay.
- Proposed severity: ADVISORY (no wrong number comes out of this lane; the bad value is caught by every computing function).
- Lens: real-data
- Reproduction as a test: `with self.assertRaises(ValueError): Shift(datetime(2026,6,1,9), datetime(2026,6,1,17))`; fails today (no exception). The suite's own `test_naive_start_rejected` builds a naive Shift, so this may be a deliberate choice; see Q3.

### A4. Date-range edges raise OverflowError instead of the documented ValueError

- Where: shiftpay/shifts.py:51-52 (`_local_midnight_utc`) and :69/:74 (`first_day + timedelta(days=1|2)`).
- Input: `split_at_midnight(Shift(datetime(9999,12,30,12,tzinfo=UTC), datetime(9999,12,31,2,tzinfo=UTC)), ZoneInfo("Asia/Tokyo"))` raises `OverflowError: date value out of range` (probe confirmed). The docstring promises ValueError for shifts it cannot split.
- Wrong outcome: a caller catching ValueError to report bad input crashes instead.
- Reachable by: only a caller passing a year-9999 date (typo or sentinel "open-ended" end date).
- Proposed severity: ADVISORY
- Lens: real-data
- Reproduction as a test: `with self.assertRaises(ValueError): split_at_midnight(<shift above>, ZoneInfo("Asia/Tokyo"))`; fails today with OverflowError.

### A5. Splitting in a zone with a sub-minute UTC offset produces pieces that `duration_minutes` then rejects

- Where: shiftpay/shifts.py:51-52 and :77-78 (boundary is local midnight, which is not on a whole UTC minute when the zone offset has seconds); shiftpay/shifts.py:36-37 rejects such pieces.
- Input: `split_at_midnight(Shift(datetime(1970,1,1,23,tzinfo=UTC), datetime(1970,1,2,3,tzinfo=UTC)), ZoneInfo("Africa/Monrovia"))` (offset -0:44:30 then). The whole shift is 240 minutes, but each piece's `duration_minutes()` raises "shift duration must be a whole number of minutes" (probe confirmed).
- Wrong outcome: a valid whole-minute shift cannot be paid per local day.
- Reachable by: historical dates only (no current IANA zone has a seconds offset), so an unrealistic caller such as a back-pay import of pre-1972 records.
- Proposed severity: ADVISORY
- Lens: real-data
- Reproduction as a test: assert `sum(p.duration_minutes() for p in split_at_midnight(s, ZoneInfo("Africa/Monrovia"))) == 240` for `s` above; raises ValueError today.

### A6. Test gaps: what tests/test_shifts.py does not prove

- Lens: testing. Proposed severity: IMPORTANT for the first two bullets (they cover A1 and A2, the money-affecting paths), ADVISORY for the rest.
- No test feeds an ambiguous (2026-11-01 01:xx without explicit fold) or nonexistent (2026-03-08 02:xx) wall time to `duration_minutes` or `split_at_midnight`; the DST tests either use exact hours outside the gap/fold or set `fold` explicitly (test_shifts.py:66-69). Test to add: the A1 reproduction.
- No test of `Shift` equality or hashing, and `assertInstants` (test_shifts.py:73-76) converts everything to UTC, which hides A2. Test to add: the A2 reproduction.
- The fall-back and spring-forward split tests (test_shifts.py:131-157) assert only piece durations, not the boundary instant or that each piece is in `tz`; `test_results_expressed_in_tz` (:126-129) checks only `start.utcoffset()` on a June date and never `end` or a DST date. Test to add: for `Shift(ny(2026,10,31,22), ny(2026,11,1,6))` assert the boundary equals `datetime(2026,11,1,4,tzinfo=UTC)` and every piece's start and end have `tzinfo is NY`.
- No test of a shift whose first piece starts inside the repeated hour (input in UTC 2026-11-01 06:00Z-07:00Z), where the output must carry `fold=1`.
- No test of a zone whose DST change happens at local midnight (America/Havana, America/Santiago, Africa/Cairo, America/Asuncion), where `datetime(day, 00:00, tzinfo=tz)` does not exist or repeats. My brute-force probe over every IANA zone near every 2026 transition found the code correct (121,479 splits, 0 problems), but nothing in the suite would catch a regression there.
- Limit edge is tested only far from it: `test_spans_three_local_days_rejected` ends 12 hours past the limit. No test ends exactly at, and one minute past, the second local midnight, and none does so across a DST day (e.g. start 2026-11-01 12:00 NY, end 2026-11-03 00:00 accepted, 00:01 rejected).
- `test_exactly_two_full_days_after_start_midnight_ok` (:164-166) asserts only `len == 2`, not the pieces' instants or durations.
- Sub-minute rejection is tested only with 30 seconds (:43-46); a 1-microsecond remainder is not tested.
- `split_at_midnight` naive rejection is tested only with both ends naive (:168-171), not one end.

### A7. Test gaps: what tests/test_pay.py does not prove

- Lens: testing. Proposed severity: ADVISORY (my exhaustive probe found the arithmetic correct, so these are regression gaps only).
- Rounding is checked at a handful of points (test_pay.py:16-31). No test sweeps a range against an exact reference; I ran minutes 0-599 x rate 0-399 against `floor(Fraction(m*r,60) + 1/2)` with 0 mismatches, but the suite would not catch a regression in, say, rates not divisible by small factors. Test to add: that sweep.
- `overtime_split` is checked at a few points; no test asserts the invariant `regular + overtime == minutes` and `regular <= threshold` across a range (my probe: 0 violations).
- No test documents that per-piece rounding differs from whole-shift rounding (`gross_pay(1,30) + gross_pay(1,30) == 2` but `gross_pay(2,30) == 1`); see Q2.
- No test of `int` subclasses (`IntEnum` is accepted and used as an int; probe returns 1500 for `IntEnum` 60 at 1500).

## Questions for the owner

- Q1. Should `Shift` (or `duration_minutes`/`split_at_midnight`) refuse wall times that are ambiguous or nonexistent in their zone, or is the caller responsible for setting `fold` from what the user meant? Today `fold=0` is applied silently, which pays the first-occurrence reading of 01:xx on 2026-11-01 (A1).
- Q2. When a shift is split at midnight, is pay rounded per piece or once per shift/pay period? Rounding each piece half-up and summing can pay up to one cent more per piece than rounding the total (`gross_pay(1,30)*2 == 2` vs `gross_pay(2,30) == 1`). The lane has no function that sums pieces, so the policy lives with the caller.
- Q3. Is deferring the awareness check from `Shift` construction to the methods deliberate (tests construct naive Shifts on purpose)? If so, the class docstring "between two aware datetimes" overstates it (A3).
- Q4. Should `Shift` equality mean "same instants"? The generated dataclass equality compares wall times in a shared zone and returns False across zones during a fold (A2).
- Q5. `split_at_midnight` rejects `datetime.timezone` objects, including `timezone.utc` (shifts.py:64-65, tested). Is UTC-day splitting intentionally unsupported? `ZoneInfo("UTC")` works, so this looks like a deliberate narrowing.
- Q6. `overtime_split` defaults to 2400 minutes (40 hours). Is that a per-week threshold, and is the caller expected to pass a week's total? A daily-overtime jurisdiction would need a different threshold and grouping; nothing here groups minutes by week or day.

## Coverage

- Read in full: shiftpay/__init__.py (6 lines); shiftpay/shifts.py (78 lines: `_is_aware`, `Shift`, `Shift.__post_init__`, `Shift.duration_minutes`, `_validate`, `_local_midnight_utc`, `split_at_midnight`); shiftpay/pay.py (31 lines: `_require_int`, `gross_pay`, `overtime_split`); tests/test_shifts.py (191 lines, `DurationTests`, `SplitTests`); tests/test_pay.py (99 lines, `GrossPayTests`, `OvertimeSplitTests`).
- Ran: `python3 -m unittest discover -s tests -t .` (54 tests, OK). Scripted probes via `python3 -c` and one probe script in my scratchpad (not in the repo): every IANA zone scanned for local dates going backward in 2026 (none); `split_at_midnight` brute-forced around every 2026 offset transition in every zone, shifts of 1h to 25h starting -30h..+30h from the transition, checking concatenation by instant, pieces in `tz`, boundary is a real local-day start, no piece spans two local days, durations sum, and that rejections really span three days (121,479 splits, 0 problems); NY gap/fold inputs; `Shift` equality and hashing in the fold; naive construction; year-9999 and year-1 edges; Africa/Monrovia 1970; `gross_pay` exhaustive against `Fraction` for minutes 0-599 x rate 0-399 (0 mismatches); `overtime_split` invariant sweep (0 violations); int-subclass inputs.
- Invariants that held under attack: `duration_minutes` never truncated (sub-minute raises) or returned negative; `gross_pay` exact integer half-up, rejects float and bool; `overtime_split` never loses or double-counts a minute; `split_at_midnight` pieces concatenate by instant and are in the requested zone, including NY 2026-03-08 and 2026-11-01; naive datetimes are rejected by both computing functions (not by the constructor, A3).
- Not flagged (judged not a realistic defect): an `int` subclass that overrides `__mul__` can make `gross_pay` return anything, since `_require_int` trusts any `int` subclass; that needs a hostile caller inside the process.
- Skipped: README.md (as instructed, and not needed after the code review); tests/__init__.py (outside the listed scope); everything outside clean-app.

END OF REPORT: lane A
