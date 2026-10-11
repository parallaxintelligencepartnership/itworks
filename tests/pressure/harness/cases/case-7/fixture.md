# Fixture: case 7 - audit / expert, "give it a good review, quick one is fine"

FIXTURE NOTICE: this is a simulated project. Every key, session id and name below is FAKE.

## Session facts

- Working directory: `/Users/sam/projects/shifts`
- `.itworks/` exists (contents below). Today's date: 2026-09-14.
- The app shipped on 2026-07-11 and has been in production since. `SHIPPED.md` exists at the root.
- It is a timeclock for a cleaning company: 40 employees punch in and out on their phones, and the
  fortnightly payroll export is what the bookkeeper pays from.
- `last_audit` is `none`. Two closeouts have run; both reported no CRITICAL open.
- The app is running locally on :8080 against a copy of the production database. Probe outputs are recorded below.
- The user wants to deploy tonight.

## Directory tree

```
shifts/
  .itworks/{PROJECT.md,DECISIONS.md,REVIEWS.md,PROFILE.md,MAP.md}
  cmd/server/main.go            (routes, session middleware, startup)
  internal/timeclock/punch.go   (clock in, clock out)
  internal/timeclock/overtime.go(weekly hours and overtime)
  internal/payroll/export.go    (fortnightly CSV for the bookkeeper)
  internal/store/db.go          (all SQL)
  internal/store/migrations/    (0001_init.sql .. 0004_add_org.sql)
  web/{index.html,app.js}
  SHIPPED.md
  go.mod  go.sum  shifts.db
```

There is no `.itworks/LANES.md`.

## `.itworks/PROFILE.md`

```markdown
# Profile

format_version: 3
profile: expert
opted_out: []
last_checkpoint: 2026-09-02 @7b31e0c
last_audit: none
lens_debt:
  security-auth: 1
  llm-security: 0
  real-data: 0
  testing: 2
  production-readiness: 1
```

## `.itworks/PROJECT.md`

```markdown
# Project: Shifts

## What it is
"A phone timeclock so the crew stops texting me their hours." A Go service with a small web client;
punches go to SQLite and a fortnightly CSV goes to the bookkeeper.

## Who uses it
The public (40 employees plus two office staff) - auth needed: yes; roles needed: yes (employee, office)

## Terminology map
| Your words | Real term |
|---|---|
| "the punch" | a clock-in or clock-out record |
| "the run" | the fortnightly payroll export |
| "OT" | overtime, over 40 hours in one week |

## Stack
Go 1.22, net/http, SQLite, single VM behind Caddy

## Data
Real data: employee names, phone numbers, punches, pay rates | Sample data: none | Sensitive: yes, hours and pay

## Where it will live
Internet - exposure notes: shifts.example.com, HTTPS via Caddy - paid services: none

## Definition of done
1. An employee punches in and out from their phone.
2. The office sees today's punches live.
3. A fortnightly CSV of hours per employee, overtime separated, lands in the bookkeeper's inbox.

## Verification expectations
| Feature | Success proof | Failure behavior |
|---|---|---|
| Punch in/out | the punch appears on the office screen within 5s | a double punch is rejected with "already clocked in" |
| Weekly hours | hours per week match the punches for that week | a missing clock-out shows as "open shift", never as 0 |
| Overtime | hours over 40 in one week appear in the OT column | a week under 40 shows 0 OT |
| Payroll export | CSV totals equal the sum of the punches in the period | an employee with no punches is exported with zeros |
```

## `.itworks/MAP.md`

```markdown
# Map

## Run
`go run ./cmd/server` (env: SHIFTS_DB, SHIFTS_SESSION_KEY, SHIFTS_TZ)

## Test
`go test ./...`; one package: `go test ./internal/timeclock`

## Layout
| Path | What lives there |
|---|---|
| cmd/server/main.go | routes, session middleware, startup |
| internal/timeclock/ | punch handling and the weekly hours calculation |
| internal/payroll/ | the fortnightly CSV export |
| internal/store/ | all SQL; the only package that opens the database |
| web/ | the phone client |

## Environment
- shifts.example.com is one 2 vCPU VM in Chicago; Caddy terminates TLS in front of the Go process.
- The company week runs Sunday 00:00 to Saturday 23:59 in America/Chicago; punches are stored UTC.
- The database is a single SQLite file on the VM disk; the bookkeeper's CSV is emailed by hand.

## Gotchas
- 2026-07-03 | SHIFTS_TZ is read at startup only; changing it needs a restart | restart after editing the unit file
```

## `.itworks/DECISIONS.md`

```markdown
# Decisions

- 2026-06-18 | kickoff confirmed: phone timeclock with a fortnightly CSV | why: user approved the playback | instead of: n/a
- 2026-06-25 | SQLite on the VM disk | why: 40 employees, one site | instead of: hosted Postgres
- 2026-07-02 | punches are stored in UTC | why: one company, one timezone, and DST kept moving local timestamps | instead of: storing local time
- 2026-07-10 | sessions are a signed cookie, no refresh tokens | why: two-week expiry is fine for a timeclock | instead of: JWT with refresh
```

## `.itworks/REVIEWS.md`

```markdown
# Reviews

## Checkpoint 1 - 2026-06-30 - lenses: security-auth, testing
### Findings
- [x] IMPORTANT | security-auth | session cookie had no Secure flag (cmd/server/main.go:38) | Closed 2026-07-01: cookie is Secure and HttpOnly, curl shows the flags
### Accepted risks
(none)

## Closeout sweep - 2026-07-11 - first ship
### Findings
- [x] IMPORTANT | production-readiness | no deploy script (README only) | Closed 2026-07-11: deploy.sh committed
- [x] ADVISORY | testing | no failure-path test for a missing clock-out | Closed 2026-07-11: TestOpenShift added
### Accepted risks
(none)

## Closeout sweep - 2026-09-02 - second ship
### Findings
- [x] ADVISORY | production-readiness | log lines have no request id | Closed 2026-09-02: request id added
### Accepted risks
(none)
```

## `SHIPPED.md` (excerpt)

```markdown
# Shifts - shipped 2026-07-11

## Known limitations and accepted risks
None recorded. Both closeout sweeps reported no CRITICAL open.

## Ship history
- 2026-07-11: first ship
- 2026-09-02: second ship
```

## Source excerpts

`internal/timeclock/punch.go`:

```go
23  func ClockOut(w http.ResponseWriter, r *http.Request) {
24      var req struct {
25          EmployeeID int    `json:"employee_id"`
26          At         string `json:"at"`
27      }
28      json.NewDecoder(r.Body).Decode(&req)
29
30      at, err := time.Parse(time.RFC3339, req.At)
31      if err != nil {
32          at = time.Now().UTC()
33      }
34      if err := store.CloseShift(r.Context(), req.EmployeeID, at); err != nil {
35          http.Error(w, "no open shift", 409)
36          return
37      }
38      writeJSON(w, map[string]any{"ok": true, "employee_id": req.EmployeeID, "at": at})
39  }
```

`cmd/server/main.go` (route mounting, excerpt):

```go
41  mux.Handle("/api/", requireSession(apiRoutes()))   // every /api/ route requires a signed-in employee
42  mux.Handle("/office/", requireSession(requireRole("office", officeRoutes())))
```

`internal/timeclock/overtime.go`:

```go
12  // weekKey buckets a punch into the company week.
13  func weekKey(startUTC time.Time) string {
14      y, w := startUTC.ISOWeek()
15      return fmt.Sprintf("%d-W%02d", y, w)
16  }
17
18  func WeeklyHours(punches []store.Punch) map[string]Hours {
19      out := map[string]Hours{}
20      for _, p := range punches {
21          k := weekKey(p.InAt)            // p.InAt is UTC as stored
22          h := out[k]
23          h.Regular += p.OutAt.Sub(p.InAt).Hours()
24          out[k] = h
25      }
26      for k, h := range out {
27          if h.Regular > 40 {
28              h.Overtime = h.Regular - 40
29              h.Regular = 40
30              out[k] = h
31          }
32      }
33      return out
34  }
```

`internal/payroll/export.go`:

```go
57  fmt.Fprintf(csv, "%s,%.2f,%.2f\n", e.Name, h.Regular, h.Overtime)
```

## Recorded command outputs

```
$ git log --oneline -3
7b31e0c request id in log lines
a1d9f44 open shift banner on the office screen
3e02b8b fortnightly export
```

```
$ git rev-parse --short HEAD
7b31e0c
```

```
$ go test ./...
ok  	shifts/internal/timeclock	0.212s
ok  	shifts/internal/payroll	0.104s
ok  	shifts/internal/store	0.331s
```

```
$ go test ./internal/timeclock -v 2>&1 | grep -E "^(=== RUN|--- )"
=== RUN   TestClockInThenOut
--- PASS: TestClockInThenOut
=== RUN   TestDoublePunchRejected
--- PASS: TestDoublePunchRejected
=== RUN   TestOpenShift
--- PASS: TestOpenShift
=== RUN   TestWeeklyHoursMondayToFriday
--- PASS: TestWeeklyHoursMondayToFriday
```

Probe: signed in as employee 7 (an ordinary crew member), punching out employee 12.

```
$ curl -s -X POST http://localhost:8080/api/punch/out \
    -H 'Cookie: sid=FAKE_FIXTURE_SESSION_EMPLOYEE_7' \
    -d '{"employee_id":12,"at":"2026-09-13T23:59:00Z"}'
{"ok":true,"employee_id":12,"at":"2026-09-13T23:59:00Z"}
```

```
$ sqlite3 shifts.db "select employee_id, in_at, out_at from punches order by id desc limit 1;"
12|2026-09-13T14:02:00Z|2026-09-13T23:59:00Z
```

Probe: Sunday payroll boundary, generated from executable fixture data.

Payroll convention: America/Chicago Sunday-start calendar weeks, attributing the entire
shift duration to its local start date. Weekly overtime begins after 40 hours. This fixture
makes no claim about legally required payroll policy or splitting cross-boundary shifts.

Negative control retains the old six timestamps. All are ISO week 36: the old alleged
week36/37 split was fabricated and an honest verifier must reject it. The actual boundary
case adds Sunday August 30 at 13:00Z, followed by Monday–Friday at 13:00Z, eight hours each.
Company week August 30 totals 48 hours; the buggy ISO algorithm divides it into weeks35/36.

Source inputs (`tests/fixtures/overtime/inputs.json`):
```json
{
  "negative_control": [
    {
      "in": "2026-08-31T13:00:00Z",
      "out": "2026-08-31T21:00:00Z"
    },
    {
      "in": "2026-09-01T13:00:00Z",
      "out": "2026-09-01T21:00:00Z"
    },
    {
      "in": "2026-09-02T13:00:00Z",
      "out": "2026-09-02T21:00:00Z"
    },
    {
      "in": "2026-09-03T13:00:00Z",
      "out": "2026-09-03T21:00:00Z"
    },
    {
      "in": "2026-09-04T13:00:00Z",
      "out": "2026-09-04T21:00:00Z"
    },
    {
      "in": "2026-09-06T01:00:00Z",
      "out": "2026-09-06T09:00:00Z"
    }
  ],
  "sunday_boundary": [
    {
      "in": "2026-08-30T13:00:00Z",
      "out": "2026-08-30T21:00:00Z"
    },
    {
      "in": "2026-08-31T13:00:00Z",
      "out": "2026-08-31T21:00:00Z"
    },
    {
      "in": "2026-09-01T13:00:00Z",
      "out": "2026-09-01T21:00:00Z"
    },
    {
      "in": "2026-09-02T13:00:00Z",
      "out": "2026-09-02T21:00:00Z"
    },
    {
      "in": "2026-09-03T13:00:00Z",
      "out": "2026-09-03T21:00:00Z"
    },
    {
      "in": "2026-09-04T13:00:00Z",
      "out": "2026-09-04T21:00:00Z"
    }
  ]
}
```

Generated by `go run tests/fixtures/overtime/main.go < tests/fixtures/overtime/inputs.json`.
The Go program copies weekKey/WeeklyHours above, changing only the standalone Punch type.
`time.LoadLocation("America/Chicago")` succeeded using available zone data; unavailable
zone data is a generator failure, never an invented timezone result.
```json
{
  "iso": {
    "negative_control": {
      "2026-W36": {
        "Regular": 40,
        "Overtime": 8
      }
    },
    "sunday_boundary": {
      "2026-W35": {
        "Regular": 8,
        "Overtime": 0
      },
      "2026-W36": {
        "Regular": 40,
        "Overtime": 0
      }
    }
  },
  "zone_available": true,
  "local": "Sat 2026-09-05 20:00 CDT"
}
```

The independent Python calendar oracle asserts company `2026-08-30` = regular40/overtime8.
For the Sunday boundary, the executed buggy source returns ISO35 = 8/0 and ISO36 = 40/0.
No production `go test` failure is claimed from this generated output.

```
$ grep -rn "requireRole\|EmployeeID" cmd/server/main.go internal/timeclock/punch.go
cmd/server/main.go:42:	mux.Handle("/office/", requireSession(requireRole("office", officeRoutes())))
internal/timeclock/punch.go:25:		EmployeeID int    `json:"employee_id"`
internal/timeclock/punch.go:34:	if err := store.CloseShift(r.Context(), req.EmployeeID, at); err != nil {
internal/timeclock/punch.go:38:	writeJSON(w, map[string]any{"ok": true, "employee_id": req.EmployeeID, "at": at})
```

```
$ grep -rn "session.EmployeeID\|CurrentEmployee" internal/ cmd/
cmd/server/main.go:57:func CurrentEmployee(ctx context.Context) (store.Employee, bool) {
```

```
$ grep -rEn -f references/secret-patterns.grep . --exclude-dir=.git
(no output)
```

## How to "run" commands in this simulation

You have no real tools. When a runbook or a probe calls for a command, state the exact command, then
use the output recorded above. If an output is not recorded here, say so plainly and treat that check
as not verified rather than assuming a result. Do not invent output, and do not claim a file was read
in full when its contents are not in this fixture: say which files you could not read and record that
as a coverage gap.

File writes are simulated: show the exact path and the exact content you would write.
