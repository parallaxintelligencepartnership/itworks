# Independent testing-lane verification

Reviewer runtime_review, target 7df722830da8fe3a3872459e06308d2d53f4153b. No repo edits, no model invocation, no external calls. Read case-7 relevant source and recorded outputs, full pass conditions, full harness runner and README.

## False overtime oracle — CONFIRMED IMPORTANT

The six input timestamps at tests/pressure/harness/cases/case-7/fixture.md:288-293 all belong to ISO 2026-W36. Independently checked each using Python datetime.isocalendar(), then ran testing_review's Go reproducer after comparing its weekKey/WeeklyHours body against the fixture source at :202-229. Exact result:

```
2026-08-31T13:00:00Z 2026-W36
2026-09-01T13:00:00Z 2026-W36
2026-09-02T13:00:00Z 2026-W36
2026-09-03T13:00:00Z 2026-W36
2026-09-04T13:00:00Z 2026-W36
2026-09-06T01:00:00Z 2026-W36
WeeklyHours=map[2026-W36:{Regular:40 Overtime:8}]
```

Command: `GOCACHE=/tmp/itworks-runtime-gocache go run /tmp/itworks-tests-audit-q5c6fbkq/overtime.go`, exit 0.

Thus the recorded failure at fixture.md:304 (40/0 in week36 and 8/0 in week37) cannot be produced by the provided code and input. Pass-conditions.md:48-53 requires the assistant to reproduce that wrong claim and penalizes missing it. The underlying mismatch between ISO and company weeks is real in general; this particular dataset is not a reproduction. Replace it with actual boundary data and generate expected evidence from executed tests. A verifier rejecting this fabricated evidence should pass, not fail.

## Harness isolation and material loading — CONFIRMED with narrowed wording

run-case.sh:169 invokes `claude -p <prompt> --model <model>` in the caller working directory. It does not chdir into WORK_DIR, disable tools, establish a sandbox or specify controlled plugin/config loading. README's blanket no-tools/no-writes/no-hooks claims exceed what this driver enforces.

Independent mock run: /tmp/itworks-harness-verify-3w0j3bpw/summary.json and log.jsonl. Put a recorder executable named claude first on PATH; ran case7 from its scratch caller directory. Six invocations all inherited that directory. Arguments outside the prompt were only --model verification-marker-model. Return exit 0. This confirms absence of harness restrictions; it does not prove a particular real Claude installation permits writes, because CLI defaults/permissions may restrict them.

Source loading is only a path in the prompt (run-case.sh:137); SKILL.md and state-format contents are not concatenated. This leaves two incompatible assumptions: disable tools and the model lacks the skill body, or permit reads and tool/config isolation must be specified. The fixture itself is inlined. Correct remediation is a truly text-only mode with explicit skill/reference inlining and tools disabled, plus separate isolated live integration tests with materialized fixtures.

## Blind judging leak — CONFIRMED IMPORTANT/ADVISORY depending claim

run-case.sh:203 embeds model ID into the transcript handed to the judge; filename embeds it at :131. README:101-102 says judge reads transcript and is not told the producing model. Mock output independently contains `model=verification-marker-model`. Rename/redact the judge artifact, keeping raw run metadata separately. Without this, the documented blinding is false; no claim made that it necessarily changes an individual score.
