# Verification: lane A (shiftpay), precision mode

Target: tests/fixtures/clean-app, working tree at 72221e3 (clean). Python 3.9.6. Baseline suite: 54 tests, OK.
Note on the lane header: it says "at 035640f", but `git log -- tests/fixtures/clean-app` shows the fixture first exists in 72221e3. No item cites a commit, so no item is refuted for this; all line citations below were checked against 72221e3 and exist.
Probes: scratchpad/case9/verifyA/probe.py (imports shiftpay from the fixture, read-only). Mutation runs: throwaway copies under scratchpad/case9/verifyA/mut (deleted after each run).
Summary: A1 REFUTED, A2 PARTIAL (ADVISORY), A3 REFUTED, A4 PARTIAL (ADVISORY), A5 REFUTED, A6 PARTIAL (ADVISORY), A7 CONFIRMED (ADVISORY). Nothing reaches IMPORTANT or CRITICAL.

## A1. Ambiguous and nonexistent wall times resolved by fold: REFUTED

Reproduction (numbers hold):
- `Shift(ny(2026,10,31,22), ny(2026,11,1,1,30)).duration_minutes()` -> 210; same end with `fold=1` -> 270. The two ends are 05:30Z and 06:30Z respectively.
- `Shift(ny(2026,3,8,1), ny(2026,3,8,2,30)).duration_minutes()` -> 90 (02:30 fold=0 maps to 07:30Z); `fold=1` -> 30.
- Split of a shift starting at nonexistent 02:30: piece start prints 03:30 EDT, and `piece.start.astimezone(UTC) == shift.start.astimezone(UTC)` -> True (same instant, re-expressed in tz).
Control: `Shift(ny(2026,10,31,22), ny(2026,11,1,6))` -> 540 (02:00Z to 11:00Z, correct over the 25-hour night); the same 270-minute interval entered in UTC -> 270.

Why refuted: each returned value is the exact elapsed time between the instants the caller passed, which is the stated design.
- README: "`Shift` is a half-open interval of aware datetimes. `duration_minutes()` is elapsed time (DST-correct, computed in UTC) and raises `ValueError` for naive datetimes, end before start, or a non-whole-minute duration." Ambiguous or nonexistent wall times are not in that error list. Under PEP 495 an aware datetime with a `fold` value is one exact instant.
- README: split "returns pieces in `tz`". The "03:30" start is the same instant shown in `tz`, so the stored instant is unchanged.
- The proposed fix cannot be built without breaking the suite's own design: `test_fall_back_repeated_hour` (tests/test_shifts.py:66-69) passes an explicit `fold=0` 01:30 and expects 60. An explicit `fold=0` cannot be told apart from the default, so "refuse ambiguous times without an explicit fold" would reject that test's valid input.
- Deciding what a user meant by "01:30" happens where the caller builds the datetime, not in this library.
Final severity: none. Keep it as an owner question (lane Q1): should the library refuse nonexistent (gap) times, which can be detected without guessing? The README does not cover them.

## A2. Shift equality and hashing compare wall time: PARTIAL

What holds (reproduced with a control):
- Test: `a = Shift(ny(2026,11,1,1,0), ny(2026,11,1,1,45))`, `b` = same with `fold=1` (instants 05:00Z-05:45Z and 06:00Z-06:45Z). `a == b` -> True and `len({a, b})` -> 1. A test asserting `a != b` fails today.
- `split_at_midnight` does produce the pair: split pieces of UTC shifts 05:00Z-05:45Z and 06:00Z-06:45Z compare equal (True; folds 0 and 1).
- Control: `Shift(ny(2026,11,1,3,0), ny(2026,11,1,3,45))` against `Shift(ny(2026,11,1,4,0), ny(2026,11,1,4,45))` (outside the fold) -> unequal, and the set has 2 members. That passes.

What does not hold:
- Input 2 (`split_at_midnight(s, NY)[0].start == s.start` -> False) is stdlib `datetime` comparison, not library code. A raw `ny(2026,11,1,1,30,fold=1) == datetime(2026,11,1,6,30,tzinfo=UTC)` is also False (PEP 495 inter-zone rule), and the instants are equal (`astimezone(UTC)` comparison -> True). Pieces being in a different zone from the input is README-stated ("returns pieces in `tz`"). Control: the June case (`split(...)[0].start == s.start`) -> True.
- The lost-pay outcome needs a caller that deduplicates `Shift` values, and no such caller exists in this code. The README defines no equality semantics for `Shift`. The collision needs one worker with two shifts whose wall start and end are identical in both occurrences of the repeated hour. The library computes no stored money or time from equality.
Final severity: ADVISORY (the generated dataclass equality inherits `datetime`'s same-zone wall-time equality). Owner question (lane Q4): should `Shift` define `__eq__`/`__hash__` on UTC instants? Doing so would also make a UTC shift and an NY shift for the same instants equal, which changes current behavior.

## A3. Shift constructor accepts naive datetimes: REFUTED

Reproduction: `Shift(datetime(2026,6,1,9), datetime(2026,6,1,17))` constructs; `.duration_minutes()` -> `ValueError: shift start and end must be timezone-aware`. Control: the aware version -> 480.
Why refuted: the README puts the check on the method: "`duration_minutes()` ... raises `ValueError` for naive datetimes, end before start". The suite builds naive and reversed Shifts on purpose and expects the method to raise (tests/test_shifts.py:28-41, :168-176). Both computing functions reject the value through `_validate` (shifts.py:41-48). No wrong number can come out.
Final severity: none. Owner question (lane Q3): the class docstring "between two aware datetimes" (shifts.py:17) reads as a construction guarantee that the README does not make.

## A4. Year-9999 edge raises OverflowError: PARTIAL

What holds:
- Test: `split_at_midnight(Shift(datetime(9999,12,30,12,tzinfo=UTC), datetime(9999,12,31,2,tzinfo=UTC)), ZoneInfo("Asia/Tokyo"))` -> `OverflowError: date value out of range`, raised at shifts.py:74 (`first_day + timedelta(days=2)` = 10000-01-01). The same shift's `duration_minutes()` -> 840, so the input is a valid datetime pair.
- Control: the same shape in 2026 (`2026-12-30 12:00Z` to `2026-12-31 02:00Z`, Tokyo) -> two pieces of [180, 660] minutes.

What does not hold:
- The cited promise. The docstring (shifts.py:61) promises ValueError only "if the shift would need more than two pieces", and the README only for "shifts spanning more than two local days". This shift spans two local days (9999-12-30 21:00 to 9999-12-31 11:00 JST), so the correct result is two pieces, not ValueError. The lane's proposed test (`assertRaises(ValueError)`) would lock in the wrong behavior.
- Reachability: the input has to be within two days of `datetime.max`. A timesheet user entering clock times does not produce that, so this is an unrealistic input.
Final severity: ADVISORY. If the owner fixes it: when computing `limit` overflows, treat the limit as unbounded (any valid `end` is below it). Test: the shift above returns two pieces whose durations sum to 840. Fails today; passes after. The 2026 control and `test_spans_three_local_days_rejected` must not change.

## A5. Sub-minute zone offset yields pieces duration_minutes rejects: REFUTED

Reproduction: Africa/Monrovia on 1970-01-01 has offset -0:44:30. The shift 23:00Z to 03:00Z (240 minutes) splits at 00:44:30Z, and each piece's `duration_minutes()` raises "must be a whole number of minutes". Control: the same shift on 2026-01-01 (offset 0) gives pieces [60, 180].
Why refuted: each half follows a README-stated rule. "`split_at_midnight` ... splits at local midnight", and local midnight here is 00:44:30Z. "`duration_minutes()` ... raises `ValueError` for ... a non-whole-minute duration", so the pieces are correctly refused rather than truncated. The trigger needs a pre-1972 date: a weekly scan of all 598 IANA zones from 1972-06 to 2030 found no sub-minute offset.
Final severity: none. Possible owner note: whole-minute pay per local day is undefined for historical sub-minute zones.

## A6. Test gaps in tests/test_shifts.py: PARTIAL

Reproduction method: a mutant that the suite should kill but does not shows a gap. The control is a sibling mutant in the same code that the suite does kill. Each run used a fresh copy, and the unmutated copy ran 54 tests, OK.
- Gap holds (pieces' `end` not checked in tz): mutant `end_local = end` (shifts.py:71) -> 54 OK (survives). Control: `start_local = start` -> FAIL test_results_expressed_in_tz.
- Gap holds (no one-minute-past-limit test): mutant `if end > limit + timedelta(minutes=1)` (shifts.py:75) -> survives. Control: `if end >= limit` -> ERROR test_exactly_two_full_days_after_start_midnight_ok.
- Gap holds (no equality or hash test): mutant `@dataclass(frozen=True, eq=False)` -> survives. Control: same as above.
- Gap holds (1-microsecond remainder): mutant `delta % _ONE_MINUTE >= timedelta(seconds=1)` (shifts.py:36) -> survives. Control: removing the check -> FAIL test_sub_minute_rejected.
- Gaps hold by inspection (no NY gap or fold input without explicit fold, no zone with a midnight DST change, no first piece inside the repeated hour, :164-166 asserts only `len == 2`). All tests use NY only, and :66-69 is the only fold case.
Does not hold:
- "No test ends exactly at ... the second local midnight". `test_exactly_two_full_days_after_start_midnight_ok` (:164-166) ends at `ny(2026,6,3)`, which is the second local midnight after a 2026-06-01 12:00 start.
- "Split naive rejection tested only with both ends naive" is a nominal gap only. The split path uses the shared `_validate`, and the mutant that checks only `start` is killed by test_naive_end_rejected.
- The proposed IMPORTANT severity rested on A1 (refuted) and A2 (ADVISORY).
Final severity: ADVISORY. These are regression gaps to batch into the close commit; no fix round.

## A7. Test gaps in tests/test_pay.py: CONFIRMED

Reproduction (mutants survive, controls killed, fresh copy each time):
- No range sweep: the mutant adding 1 cent when `rate % 97 == 41 and minutes % 89 == 7` (pay.py:23) -> 54 OK (survives). Control: half-down `(2*m*r + 59)//120` -> FAIL test_exact_half_cent_rounds_up.
- No `regular + overtime == minutes` invariant over a range: the mutant returning overtime 0 when `minutes >= 10000` (pay.py:31) -> survives. Control: the same mutant at `minutes >= 2400` -> FAIL test_one_over_threshold.
- No test documents per-piece rounding versus whole-shift rounding: `gross_pay(1,30)*2` -> 2 and `gross_pay(2,30)` -> 1 (probe). Nothing in test_pay.py covers this.
- No `int`-subclass test: `gross_pay(IntEnum 60, IntEnum 1500)` -> 1500. No test covers it.
The current arithmetic is right: sweeping minutes 0-599 by rate 0-399 against `floor(Fraction(m*r, 60) + 1/2)` gave 0 mismatches.
Final severity: ADVISORY (regression gaps only; no wrong value comes out today).
Fix spec (test-only, for the close batch):
- Add a sweep test of `gross_pay` against the Fraction reference (at least minutes 0-599 by rate 0-399). It must kill the rare-rate mutant above and pass on the current code.
- Add an `overtime_split` invariant test over a range that crosses the default and custom thresholds (`r + o == m`, `r == min(m, t)`). It must kill the minutes-10000 mutant and pass on the current code.
- Optionally add one test that pins `gross_pay(1,30) + gross_pay(1,30) == 2` and `gross_pay(2,30) == 1` as documented behavior, pending owner answer Q2.
Must not change: shiftpay/pay.py, or any existing assertion.

## Questions for the owner carried forward (not defects)
- Q1 (from A1): refuse nonexistent (gap) wall times?
- Q3 (from A3): the docstring wording versus construction-time validation.
- Q4 (from A2): should `Shift` equality mean "same instants"?
- Q2, Q5, Q6 from the lane stand as written; they were not verified as defects.

END OF VERIFICATION: lane A
