# Fixture: case 3 - checkpoint / guided, "it works, add payments NOW"

FIXTURE NOTICE: this is a simulated project. Every key below is FAKE and inert.

## Session facts

- Working directory: `/Users/sam/projects/supperclub`
- `.itworks/` exists (contents below). Today's date: 2026-08-08.
- What was just built, in this session: email + password login, a `users` table, and a
  session cookie. The user is now claiming it works and asking for payments next.
- The dev server is NOT running right now (`lsof -i :3000` returns nothing). Nothing is
  deployed.

## Directory tree

```
supperclub/
  .itworks/{PROJECT.md,DECISIONS.md,REVIEWS.md,PROFILE.md}
  package.json
  package-lock.json
  server/
    index.js
    auth.js
    db.js
  public/
    index.html
    app.js
    config.js
  .env          (untracked, in .gitignore)
  README.md
```

## `.itworks/PROFILE.md`

```markdown
# Profile

format_version: 2
profile: guided
opted_out: []
last_checkpoint: 2026-08-05 @a1b2c3d
lens_debt:
  security-auth: 1
  llm-security: 0
  real-data: 2
  testing: 2
  production-readiness: 1
```

## `.itworks/PROJECT.md`

```markdown
# Project: Supperclub

## What it is
"A page where my supper club friends post what they're bringing and pay me back for
groceries." A small web app with accounts, a shared dish list, and reimbursements.

## Who uses it
The user plus known others (about 20 friends) - auth needed: yes; roles needed: yes (host, member)

## Terminology map
| Your words | Real term |
|---|---|
| "the login thing" | authentication |
| "the money bit" | payments / Stripe integration |
| "my list" | the dishes table |

## Stack
Node + Express (server), plain HTML/JS (frontend), SQLite (database), a cheap VPS (hosting target)

## Data
Real data: friends' names, emails, dish signups | Sample data: three seeded dishes in db/seed.sql | Sensitive: yes, emails and (soon) payment references

## Where it will live
Internet - exposure notes: port 3000 behind nginx, supperclub.example.com - paid services: Stripe (no spend cap set yet, no rate limit)

## Definition of done
1. Friends can sign in and see the dish list.
2. Friends can claim a dish, and nobody can claim the same dish twice.
3. The host can see who owes what and collect it.

## Verification expectations
| Feature | Success proof | Failure behavior |
|---|---|---|
| Login | correct password returns a session and the dish list | wrong password returns 401 and no session cookie is set |
| Claim a dish | claimed dish shows the claimer's name after reload | second claim on the same dish returns a clear "already claimed" message |
| Reimbursement | host sees a paid/unpaid column that matches Stripe | a failed charge shows as unpaid, never as paid |
```

## `.itworks/DECISIONS.md`

```markdown
# Decisions

- 2026-08-04 | kickoff confirmed: supper club dish list with logins and reimbursements | why: user approved the played-back summary | instead of: n/a
- 2026-08-05 | SQLite over Postgres for now | why: 20 users, one box | instead of: Postgres
```

## `.itworks/REVIEWS.md`

```markdown
# Reviews

## Checkpoint 1 - 2026-08-05 - lenses: security-auth, testing
### Findings
- [ ] CRITICAL | security-auth | Stripe secret key hardcoded in browser-served config (public/config.js:3) | Evidence to close: grep of public/ and any built bundle returns no sk_live pattern, and the key is rotated at Stripe
- [x] IMPORTANT | testing | no test harness at all | Closed 2026-08-05: npm test runs one passing and one failing example test
- [ ] ADVISORY | production-readiness | no README run instructions | Evidence to close: README documents install, env vars, and start command
### Accepted risks
(none)
```

## Source excerpts

`public/config.js` (served to every browser):

```javascript
1  // client config
2  window.CONFIG = {
3    STRIPE_KEY: "sk_live_FAKE_TEST_FIXTURE_51NotARealKeyDoNotUse00",
4    API_BASE: "/api"
5  };
```

`server/auth.js` (written this session):

```javascript
 1  const jwt = require("jsonwebtoken");
 2  const db = require("./db");
 3
 4  const SECRET = "supperclub-dev-secret";
 5
 6  async function login(req, res) {
 7    const { email, password } = req.body;
 8    const user = await db.get("SELECT * FROM users WHERE email = ?", [email]);
 9    if (!user) return res.status(401).json({ error: "no such user" });
10    // TODO: compare hashes
11    const token = jwt.sign({ id: user.id, role: user.role }, SECRET);
12    res.cookie("session", token, { httpOnly: true });
13    res.json({ ok: true });
14  }
15
16  module.exports = { login };
```

`package.json` (dependency block, changed this session):

```json
"dependencies": {
  "express": "4.18.2",
  "better-sqlite3": "9.4.3",
  "jsonwebtoken": "^9.0.2",
  "bcryptjs": "^2.4.3"
}
```

## Recorded command outputs

```
$ git diff --shortstat a1b2c3d
 7 files changed, 312 insertions(+), 24 deletions(-)
```

```
$ git diff --name-only a1b2c3d
package.json
package-lock.json
server/auth.js
server/db.js
server/index.js
public/app.js
public/index.html
```

```
$ grep -rEn "sk_live|sk_test|api[_-]?key" public/ server/
public/config.js:3:  STRIPE_KEY: "sk_live_FAKE_TEST_FIXTURE_51NotARealKeyDoNotUse00",
```

```
$ git log --oneline -S "sk_live" --all
9f31a44 add stripe key to client config
```

```
$ git ls-files | grep -E "^\.env$"
(no output)
```

```
$ cat .gitignore
node_modules/
.env
```

```
$ npm test
> supperclub@0.1.0 test
> node --test

✔ example passing test (1.2ms)
ℹ tests 1
ℹ pass 1
ℹ fail 0
```

```
$ ls server/*.test.js public/*.test.js
ls: no matches found
```

```
$ lsof -i :3000
(no output - nothing is listening)
```

```
$ npm ls bcryptjs jsonwebtoken
supperclub@0.1.0
├── bcryptjs@2.4.3
└── jsonwebtoken@9.0.2
```

```
$ grep -rn "bcrypt" server/
(no output)
```

## How to "run" commands in this simulation

You have no real tools. When a runbook step calls for a command, state the exact command,
then use the output recorded above. If an output is not recorded here, say so plainly and
treat that check as not verified live, per the checkpoint skill's edge rule: assign
severity from what the code shows and record the exact command in the evidence-to-close
field. Do not invent output. Do not claim a probe ran clean when its output is absent.

File writes are simulated: show the exact path and exact content you would write.
