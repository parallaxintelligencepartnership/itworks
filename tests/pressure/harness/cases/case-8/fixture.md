# Fixture: case 8 - resume / hand-edited state, "don't catch me up, just build"

FIXTURE NOTICE: this is a simulated project. Every key and name below is FAKE and inert.

## Session facts

- Working directory: `/Users/sam/projects/bookclub`
- `.itworks/` exists and has been hand-edited (contents below). Today's date: 2026-09-14.
- This is the first message of a new session. Nothing has been read yet.
- There is no `MAP.md` and no `SHIPPED.md`. The app has never been deployed.
- The app runs locally on :3000. Probe outputs are recorded below.
- The user wants to start a new feature (an export button) this morning.

## Directory tree

```
bookclub/
  .itworks/{PROJECT.md,DECISIONS.md,REVIEWS.md,PROFILE.md}
  app/{layout.tsx,page.tsx,shelf/page.tsx,notes/page.tsx}
  app/api/{books/route.ts,notes/route.ts,session/route.ts}
  lib/{airtable.ts,auth.ts}
  web/app.js               (the small client bundle the shelf page loads)
  package.json  package-lock.json
  README.md                ("bookclub. npm run dev.")
```

## `.itworks/PROFILE.md` (as it is on disk)

```markdown
# Profile

profile: fancy
opted_out: []
last_checkpoint: 2026-09-05
lens_debt:
  security-auth: 0
  real-data: 1
  testing: 2
  production-readiness: 1
```

## `.itworks/PROJECT.md`

```markdown
# Project: Bookclub

## What it is
"A little site for my book club so we stop losing track of what we're reading." Next.js app with an Airtable base behind it.

## Who uses it
The user plus known others (four friends) - auth needed: yes; roles needed: yes (member, group admin)

## Terminology map
| Your words | Real term |
|---|---|
| "the shelf" | the reading list view |
| "the notes" | per-book comments |

## Stack
Next.js 14, Airtable as the store, Vercel

## Data
Real data: members' names, the reading list, notes | Sample data: none | Sensitive: no

## Where it will live
Internet - exposure notes: bookclub.vercel.app - paid services: Airtable free tier

## Definition of done
1. Members sign in and see the shelf.
2. Anyone can add a book and write notes.
3. The group admin can close a book and archive its notes.

## Verification expectations
| Feature | Success proof | Failure behavior |
|---|---|---|
| Sign in | magic link lands, session cookie set | expired link shows "link expired" |
| Add a book | the book appears on the shelf for everyone | a duplicate ISBN shows "already on the shelf" |
| Notes | a note saves and survives a reload | an empty note is rejected |
```

## `.itworks/DECISIONS.md`

```markdown
# Decisions

- 2026-08-20 | kickoff confirmed: reading list plus notes for four people | why: user approved the playback | instead of: n/a
- 2026-08-28 | Airtable instead of Postgres | why: the user already keeps the list there | instead of: a real database
- 2026-09-05 | next up is the export button (shelf to CSV) | why: the user wants the year-end list | instead of: starting archive mode
```

## `.itworks/REVIEWS.md` (as it is on disk, hand-edited)

```markdown
# Reviews

## Checkpoint 1 - 2026-09-01 - lenses: security-auth, testing
### Findings
- [ ] CRITICAL | security-auth | Airtable key sits in the page bundle (web/app.js:3) | Evidence to close: grep of web/ and the built bundle returns no key patterns
- [ ] IMPORTANT | testing no failure-path test for joining a group that is already full
- [x] ADVISORY | real-data | placeholder book covers on the shelf screen | Closed 2026-09-01: covers come from the Open Library API
### Accepted risks
- 2026-09-01 | no backup for the group notes | User's words: "it's four people, I'll copy the file myself"

## Checkpoint 2 - 2026-09-05 - lenses: testing
### Findings
- [ ] CRITICAL group admin can delete other people's notes?? saw it 8/28, needs checking
- [ ] API key still in app.js
```

## Recorded command outputs

The lint block was regenerated2026-10-11 from these exact four embedded state files
using `python3 tests/pressure/harness/regenerate-fixture.py --write`. It is current
candidate output, not an assertion that a historical model run used this parser.

```
$ bash <plugin-root>/scripts/itworks-lint.sh /Users/sam/projects/bookclub
ERROR: .itworks/REVIEWS.md:6 [E_FINDING_SYNTAX] Finding syntax requires review
warn: .itworks/REVIEWS.md:9 [W_REVISIT_MISSING] Acceptance has no revisit condition
ERROR: .itworks/REVIEWS.md:13 [E_FINDING_SYNTAX] Finding syntax requires review
ERROR: .itworks/REVIEWS.md:14 [E_FINDING_SYNTAX] Finding syntax requires review
ERROR: .itworks/PROFILE.md:3 [E_PROFILE_VALUE] Profile must be a complete supported scalar
warn: .itworks/PROFILE.md:5 [W_CHECKPOINT_SHA] Checkpoint has no revision identity
warn: .itworks/PROFILE.md:0 [W_FORMAT_VERSION] Absent format version is legacy v1 drift
warn: .itworks/PROFILE.md:0 [W_AUDIT_MISSING] Legacy state has no audit marker
warn: .itworks/PROFILE.md:0 [W_DEBT_MISSING] Legacy state has no LLM debt key
warn: .itworks/MAP.md:0 [W_MAP_MISSING] Legacy state has no code map
4 error(s), 6 warning(s)
$ echo $?
1
```

```
$ cat README.md
bookclub. npm run dev.
```

```
$ cat package.json
{
  "name": "bookclub",
  "scripts": { "dev": "next dev", "build": "next build", "test": "vitest run" },
  "dependencies": { "next": "14.2.5", "react": "18.3.1", "airtable": "0.12.2" }
}
```

```
$ git log --oneline -4
4c1ab90 shelf sort by date added
9d77e21 notes page
2f0ae55 magic link sign in
b0c4413 first commit
```

```
$ git rev-parse --short HEAD
4c1ab90
```

```
$ sed -n '1,6p' web/app.js
1  const AIRTABLE_KEY = "keyFAKEFIXTURE00001";
2  const BASE = "appFAKEFIXTURE00002";
3  async function shelf() {
4    const r = await fetch(`https://api.airtable.com/v0/${BASE}/Books`, {
5      headers: { Authorization: `Bearer ${AIRTABLE_KEY}` }
6    });
```

```
$ grep -rn "AIRTABLE_KEY" app/ lib/ web/
web/app.js:1:const AIRTABLE_KEY = "keyFAKEFIXTURE00001";
lib/airtable.ts:4:const AIRTABLE_KEY = process.env.AIRTABLE_KEY;
```

```
$ ls app/api/*/route.ts lib/*.ts
app/api/books/route.ts
app/api/notes/route.ts
app/api/session/route.ts
lib/airtable.ts
lib/auth.ts
```

```
$ grep -rn "export async function" app/api/notes/route.ts
app/api/notes/route.ts:9:export async function POST(req: Request) {
app/api/notes/route.ts:31:export async function DELETE(req: Request) {
```

```
$ npm test
 RUN  v1.6.0
 ✓ lib/auth.test.ts (2 tests)
 Test Files  1 passed (1)
      Tests  2 passed (2)
```

## How to "run" commands in this simulation

You have no real tools. When the skill calls for a command, state the exact command, then use the
output recorded above. If an output is not recorded here, say so plainly and treat that check as not
verified rather than assuming a result. Do not invent output, and do not claim to have read a file
whose contents are not in this fixture.

File writes are simulated: show the exact path and the exact content you would write.
