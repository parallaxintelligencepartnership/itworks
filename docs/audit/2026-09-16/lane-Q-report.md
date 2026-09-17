# Lane Q - Plugin runbooks and contract

Repos: `/Users/matthew/parallax-private/Projects/itworks` @ 0b972ac (read-only),
`/Users/matthew/parallax-private/Projects/itworks-site` @ 5a87acd (read-only cross-check).
Lens id: security-auth. Host: macOS 27.0, bash 3.2.57, default shell zsh, BSD grep.
All scratch work under `.../scratchpad/audit/`. No repository file was created, edited or deleted.

---

## 1. Suspicions

### Q-1 CRITICAL - the SQL-injection step cannot match string concatenation; the `+` branch of its regex is dead
`references/lens-security-auth.md:52`

Command as written:
```
grep -rnE "(query|execute|exec)[[:space:]]*\([[:space:]]*[\"'\`][^\"'\`]*(\+|\$\{)" --include=*.js ... .
```
The character class `[^\"'\`]*` excludes the quote character, so the scan can never reach the `+`:
in `db.query("... = " + name)` the string's own closing quote sits between the opening quote and the `+`.
Only the template-literal form `` `...${x}` `` can ever match.

Probe (`scratchpad/audit/inj.js`, pattern in `inj.re` to avoid shell quoting):
```
$ grep -nE -f inj.re inj.js
3:c = db.query(`SELECT * FROM users WHERE id = ${id}`);
```
Lines 1, 2, 4, 5 - including the planted fixture line
`return db.query("SELECT * FROM users WHERE name = '" + name + "'");`
(`q-fixture/server/db.js:2`) - produce **no output**. Against the fixture the step reports "Good: no matches
(parameterized queries only)".

Why CRITICAL: string concatenation is the dominant injection shape in novice JS/Python, and the lens itself
rates the glued-from-a-form case CRITICAL. The step's own success condition is printed for the exact defect
it claims to find, so a novice ships it with a clean report.

Repro: `cd q-fixture && grep -rnE "(query|execute|exec)[[:space:]]*\([[:space:]]*[\"'\`][^\"'\`]*(\+|\$\{)" --include=*.js .` -> exit 1, no output.

### Q-2 IMPORTANT - four inspect commands abort on the stock macOS shell (zsh NOMATCH)
`references/lens-security-auth.md:52`, `references/lens-real-data.md:16`,
`references/lens-llm-security.md:16`, `references/dependency-vetting.md:20-22` (the `--include` ones)

Correction applied 2026-09-16 while fixing Q-2: there are three sites, not four. `references/dependency-vetting.md:20-22` contains no `--include` at all, so that citation is withdrawn and the file was left untouched.

The `--include=*.js` arguments are unquoted. zsh (the default macOS login shell, and what this session's
shell is) globs them and, finding no file literally named `--include=*.js`, aborts the command:
```
$ zsh -c 'grep -rn x --include=*.js .'
zsh:1: no matches found: --include=*.js
(exit 1, nothing run)
```
Under bash the same line runs. The runbooks are fenced ```bash but a reviewer pasting into a zsh terminal
gets an abort whose exit status (1) is indistinguishable from "no matches = clean". Fix is quoting:
`--include='*.js'`.

### Q-3 IMPORTANT - `src/ app/` is hardcoded; llm-security self-gates OFF on a project that does call an LLM
`references/lens-llm-security.md:16`, `references/lens-real-data.md:16`

Both step-1 greps scan only `src/ app/` with `2>/dev/null`. On the fixture the Anthropic key and the model
client live in `public/app.js`; `app/` does not exist. Result:
```
$ grep -rniE "anthropic|openai" --include=*.js src/ app/ 2>/dev/null ; echo $?
1
```
Exit 1, no output, stderr swallowed - identical to a genuinely clean project. llm-security's "Fires when"
is decided by this grep, so the whole lens records "not applicable" for an app with an Anthropic key in its
browser bundle. Same defect hides placeholder/mock data in `public/`, `pages/`, `components/`, `lib/`,
`internal/`, `cmd/`, or a repo-root layout. A Go or Python project with no `src/` is invisible to both steps.

### Q-4 IMPORTANT - no inspect step greps the current working tree for secrets outside client dirs
`references/lens-security-auth.md:15` (client dirs only), `:26` (git history only), `:34` (`git ls-files` name match only)

Planted `config/aws.json` with `AKIAIOSFODNN7EXAMPLE` is found only because it happens to be committed
(step 2 history grep). Step 1's scope is "every directory served to browsers AND the built bundle"; step 3
matches names (`.env`, `.pem`, `credentials`) not contents, and `config/aws.json` matches none of them.
A server-side key file that is present but not yet committed - and which will ship in the Docker image or
the rsync - is not scanned by any step. One line (`grep -rEn -f "$PAT" . --exclude-dir=.git`) closes it;
the fixture shows it finds all three planted secrets at once.

### Q-5 IMPORTANT - publish.md's summary rule produces a 400 on the plugin's own companion project
`references/publish.md:12` vs `itworks-site/internal/server/validate.go:83` (160-rune cap)

publish.md says summary = "first sentence of the 'What it is' section body in `.itworks/PROJECT.md`".
No length rule, and `state-format.md:17` invites "one or two sentences in the user's own words, then one
sentence in precise terms" - nothing caps it. The real `itworks-site/.itworks/PROJECT.md` first sentence is
**165 characters**. Real POST against a locally run site (see section 4):
```
HTTP 400 {"error":"summary must be between 1 and 160 characters"}
```
Same class: `name` is capped at 60 runes server-side (`validate.go:72`) with no cap in publish.md.

### Q-6 IMPORTANT - publish.md's repo_url rule sends an SSH origin, which the validator rejects
`references/publish.md:14` vs `validate.go:109-112`

"`git remote get-url origin`; the https origin URL only when source is public, else ''" - but `get-url`
returns `git@github.com:u/r.git` for the common SSH remote, and publish.md gives no conversion. Literal
implementation, verified live:
```
{"source":"public","repo_url":"git@github.com:u/r.git",...} -> HTTP 400
{"error":"repo url must be a valid https url"}
```
The `source` rule ("the git origin host is github.com...") has the same problem: an SSH remote is not a
parseable URL host without conversion.

### Q-7 IMPORTANT - publish.md's audit_date rule sends `<date> @<sha>`, which the validator rejects
`references/publish.md:16` vs `state-format.md:156` vs `validate.go:127-130`

publish.md: "the `last_audit` date from `.itworks/PROFILE.md`". state-format stores `last_audit:
2026-09-11 @9ab49cb`. Taken literally:
```
{"audit_date":"2026-09-11 @9ab49cb"} -> HTTP 400
{"error":"audit date must be a valid calendar date formatted as year, month, day"}
```
publish.md must say "the date part, before the `@`".

### Q-8 IMPORTANT - itworks-lint.sh silently skips the last line of REVIEWS.md when the file has no trailing newline
`scripts/itworks-lint.sh:73,99` (`while IFS= read -r line` with no `|| [ -n "$line" ]` guard)

```
$ printf -- '- [ ] CRITICAL | security-auth | broken grammar no evidence' >> REVIEWS.md   # no \n
$ bash itworks-lint.sh <root>
0 error(s), 0 warning(s)     EXIT=0
$ # identical line WITH a trailing newline:
ERROR: REVIEWS.md open finding does not parse (five-field grammar): ...
1 error(s), 0 warning(s)     EXIT=1
```
An unterminated file is exactly what a hand-edit or a truncated write leaves behind - the case
`project-resume` exists for. The grammar check and the `Revisit when:` check both miss it. (The
SHIPPED.md cross-check at :116 uses `grep`, so that half still fires.) Same guard is missing on the
`target.txt` loop's sibling in run-case.sh:79, which *does* have the guard - so the fix pattern is
already in the repo.

### Q-9 IMPORTANT - the lint downgrades to a warning what state-format calls corruption
`state-format.md:175` ("Every unchecked finding line in REVIEWS.md parses to the five-field grammar
above, with a valid severity and lens id") vs `scripts/itworks-lint.sh:84-90`

An open checkbox with no severity - `- [ ] API key still in app.js` - produces
`warn: REVIEWS.md open checkbox without severity`, exit 0. Per validation rule 3 that is a violation and
should force the resume rebuild path. The script's own comment (:70-71) states the intentional divergence,
but state-format.md:9 declares the lint authoritative ("its errors are the contract violations"), so the
two documents disagree about what corruption is. `tests/scenarios/resume-02-corrupt-state.md` asserts the
skill "detects both violations" - with the lint as written, only `profile: fancy` is an error.

### Q-10 ADVISORY - secret-patterns.grep misses five modern shapes, including a DB URL with a password
`references/secret-patterns.grep` (whole file); see matrix in section 3.

Missed: AWS **secret** access key (only the AKIA id is caught), `postgres://user:pass@host/db`,
40-hex generic token, Discord bot token, Telegram bot token. The postgres URL is the one that matters:
`DATABASE_URL` is the single most common thing a novice pastes into a client bundle or commits, and
pattern 13 does not fire on it (`DATABASE_URL=postgres://...` has no quotes and the key name is not
`api_key|secret|password|token`). False positives on both repos: **zero** real ones
(2 hits, both deliberate fixture keys in `tests/pressure/harness/cases/case-4/fixture.md:121,185`).

Also: the file is an ERE file. `grep -f` without `-E` matches **only** the PEM line (1 of 15 shapes).
The lens always uses `-rEn -f` (:18, :26), which is correct - but nothing in the file says so. One
comment line (`# ERE patterns: always grep -E -f`) would prevent the whole-file silent failure.

### Q-11 ADVISORY - publish.md's "Not sent" promise is a promise about PROJECT.md, not about the transport
`references/publish.md:41-52` vs `validate.go:79-88`

`summary` is free text up to 160 printable runes, `name` up to 60, and the server does no secret,
path or hostname scanning. Verified live:
```
{"summary":"deploy key sk-ant-api03-...AA at /Users/matthew/secrets on db.internal", ...}
-> HTTP 201, stored, published on approval
```
So a path, an internal hostname, a person's name or an API key travels fine in a field publish.md lists
as safe, if the user wrote it into PROJECT.md's "What it is" (which the kickoff interview explicitly
invites them to write in their own words). The fix is a line in Step 5b - the payload is already shown to
the user before sending, so the guidance is one sentence: "read the summary for anything that should not
be public before you say yes."

### Q-12 ADVISORY - the found/fixed counts shrink after archiving
`references/publish.md:25-28` vs `state-format.md:87`

The four counting greps read REVIEWS.md only. Once sections are archived to `.itworks/archive/`, the
published `found` and `fixed` drop, so a long-lived project's public badge understates the work done.
Harmless to the validator (the ratios stay consistent), but the number stops meaning what the wall says
it means.

### Q-13 ADVISORY - severity is not decidable from the text in four places
See section 7 detail below. Short version: `real-data` step 1 ("CRITICAL if the user believes this data is
real" - a belief, not an observable), `production-readiness` step 6 ("ADVISORY before closeout, IMPORTANT
at closeout" but the closeout *sweep* also raises pre-ship findings), `testing` step 1 vs the rubric
(step 1 says IMPORTANT/CRITICAL-at-closeout, rubric says "decorative test guarding money, auth, or
data-loss paths" is CRITICAL - two agents split on a decorative auth test found at checkpoint), and
`security-auth` step 6 ("CRITICAL if the glued-in value comes straight from a form or URL" requires
tracing taint, which the audit tier explicitly owns and checkpoint/closeout explicitly do not read).

### Q-14 ADVISORY - scenarios are stale on the lens count
`tests/scenarios/closeout-01-ship-it.md:8` - "Full sweep runs: all four lenses at closeout depth".
`tests/scenarios/checkpoint-01-it-works-claim.md:8` - "(not all four)".
There are five lenses since `llm-security`; `audit-method.md:10` and `project-closeout` both say five,
and `tests/pressure/harness/cases/case-5/pass-conditions.md:9` correctly says "All five `lens-*.md`
runbooks". Result lines in those scenarios are dated 2026-07-29, i.e. pre-llm-security.

### Q-15 ADVISORY - pressure-tests case 7 (audit) has no harness case; resume and audit are untested by the harness
`tests/pressure/pressure-tests.md:31` (case 7, "not yet run") vs `tests/pressure/harness/cases/` which holds
case-1..6 only, targeting kickoff (x2), checkpoint (x2), closeout (x2). `project-resume` and
`project-audit` have no harness coverage at all. The audit tier is the only tier that reads application
logic and it is the newest skill, so it is the one with the most untested wording.

### Q-16 ADVISORY - `dev vs production data` is listed as a guided card but has no glossary entry
`references/lens-real-data.md:63` lists it in "Terms this lens touches"; `references/glossary.md` has no
such entry (checked all 49 card terms across the five lenses plus dependency-vetting; this is the only
miss). In guided profile the instruction "show each term's two-line card from glossary.md" cannot be
followed for the term that names the post-ship CRITICAL.

### Q-17 ADVISORY - SHIPPED.md's shape is enforced by the lint but defined nowhere in state-format.md
`scripts/itworks-lint.sh:113-134` depends on the literal tokens `OUTSTANDING` and `accepted risks` in
SHIPPED.md, and `state-format.md:177` makes SHIPPED.md's existence a gate condition - but state-format.md
never documents SHIPPED.md. Its only definition is `skills/project-closeout/SKILL.md:62-75`. An orphan in
the state contract: the validator enforces a file the format document does not define.

---

## 2. Planted-problem matrix

Fixture: `scratchpad/audit/q-fixture/` (git-initialised, all files committed).
Steps: SA = lens-security-auth, RD = lens-real-data, LS = lens-llm-security, T = lens-testing,
PR = lens-production-readiness, DV = dependency-vetting.

| Planted problem | SA1 client grep | SA2 history | SA3 tracked names | SA4 curl routes | SA6 injection | SA7 xss | RD1 placeholder | LS1 surface | T1/T3 tests | PR4/DV3 pinning | Net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `.env` with `sk-proj-...` + `postgres://user:pass@` | caught (key only, URL missed) | **caught** | **caught** | - | - | - | - | - | - | - | caught |
| committed `config/aws.json` with `AKIA...` | missed (not a client dir) | **caught** | missed (name doesn't match) | - | - | - | - | - | - | - | caught, by history only |
| `sk-ant-api03-...` in `public/app.js` | **caught** | caught | - | - | - | - | - | missed (`src/ app/` only) | - | - | caught |
| unparameterized SQL in `server/db.js` | - | - | - | - | **MISSED (Q-1)** | - | - | - | - | - | **MISSED** |
| unauthenticated `/admin/users` in `src/index.js` | - | - | - | needs PROJECT.md route list + running server; no grep enumerates routes | - | - | - | - | - | - | not found by any command |
| `innerHTML` fed by fetched data in `public/app.js` | - | - | - | - | - | **caught** | - | - | - | - | caught |
| `package.json` caret + tilde ranges | - | - | - | - | - | - | - | - | - | **caught** | caught |
| test asserting nothing (`tests/app.test.js`) | - | - | - | - | - | - | - | - | T1 caught ("no runnable suite"); T3 mutation test needs a runner | - | caught, weakly |

Two rows are the finding: the SQL injection is missed outright, and the unauthenticated admin route has
no command behind it - SA4 depends entirely on the agent having listed the route from PROJECT.md's
"Who uses it", which in a real novice project is prose, not a route table. A `grep -rn "app\.\(get\|post\)"`
style route enumeration would make SA4 mechanical instead of aspirational.

---

## 3. Key-shape matrix for secret-patterns.grep

Input: `scratchpad/audit/keys.txt`, one sample per shape. Invocation as the lens uses it,
`grep -E -f references/secret-patterns.grep`.

| Shape | Sample | `grep -E -f` | `grep -f` (BRE) |
|---|---|---|---|
| Anthropic `sk-ant-api03-...` | yes | **caught** (pattern 1) | missed |
| OpenAI project `sk-proj-...` | yes | **caught** | missed |
| OpenAI legacy `sk-...` | yes | **caught** | missed |
| GitHub classic `ghp_...` | yes | **caught** | missed |
| GitHub fine-grained `github_pat_...` | yes | **caught** | missed |
| AWS access key id `AKIA...` | yes | **caught** | missed |
| AWS secret access key (40 char base64ish) | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` | **MISSED** | missed |
| Slack `xoxb-...` | yes | **caught** | missed |
| Stripe `sk_live_...` | yes | **caught** | missed |
| JWT `eyJ...eyJ...` | yes | **caught** | missed |
| PEM private key block | yes | **caught** | **caught** (only line that is valid BRE) |
| postgres URL with password | `postgres://appuser:Sup3rS3cretPw@db.internal:5432/app` | **MISSED** | missed |
| Google `AIza...` | yes | **caught** | missed |
| generic 40-hex token | `3f786850e387550f...` | **MISSED** | missed |
| Discord bot token | `MTk4NjIyNDgzNDcxOTI1MjQ4.Cl2FMQ.ZnCjm1XVW7vRze4b7Cq4se7kKWs` | **MISSED** | missed |
| Telegram bot token | `123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw` | **MISSED** | missed |

10 of 15 caught with `-E`. 1 of 15 without `-E`.

**False positives.** `grep -rEn -f secret-patterns.grep . --exclude-dir=.git`:

| Repo | Total matches | Real false positives | Examples |
|---|---|---|---|
| itworks @ 0b972ac | 2 | **0** | both are deliberate fixture keys: `tests/pressure/harness/cases/case-4/fixture.md:121` and `:185`, `sk-proj-FAKE_TEST_FIXTURE_NotARealKey000000` |
| itworks-site @ 5a87acd | 0 | **0** | - |

The pattern set is precise. Its problem is recall, not precision - which is the right trade for a novice
tool, but it means the five missed shapes above are silent.

Suggested additions (not applied - read-only lane):
```
(postgres|postgresql|mysql|mongodb(\+srv)?|redis|amqp)://[^:@/[:space:]]+:[^@/[:space:]]+@
[A-Za-z0-9+/]{40}(=|["'[:space:]]|$)      # AWS secret / generic 40-char
[0-9]{8,10}:AA[A-Za-z0-9_-]{33}            # Telegram
[MNO][A-Za-z0-9_-]{23}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}   # Discord
```

---

## 4. publish.md versus validate.go

Endpoint and method: publish.md **does not state them**. They live in
`skills/project-closeout/SKILL.md:89`: `curl -sS -X POST https://itworks.dev/api/entries
-H "Content-Type: application/json" --data @<payload file>`. That matches
`internal/server/server.go:92` (`POST /api/entries`) and `handlers.go:94-99` (Content-Type must start with
`application/json`, else 415). No User-Agent or any other header is required. Body cap 8192 bytes
(`handlers.go:100`, publish.md:56 agrees). Rate limit 5/IP/hour (`handlers.go:87`, publish.md:57 agrees).
Pending-until-approved (publish.md:58) matches `handlers.go:135` `status: pending`.

| Field | publish.md | validate.go | Agrees? |
|---|---|---|---|
| name | project name from `# Project:` line | :68-77 required, trimmed, 1..60 runes, printable | **no cap in publish.md** (Q-5) |
| summary | first sentence of "What it is" | :79-88 required, trimmed, 1..160 runes, printable | **no cap; real project overflows** (Q-5) |
| source | "public"/"closed" by origin host | :90-96 exactly public/closed | yes |
| repo_url | `git remote get-url origin`, https only when public, else "" | :98-113 optional; https scheme, non-empty host, <=200; MUST be "" when closed | **SSH origin sent verbatim -> 400** (Q-6) |
| audit_tier | "audit" or "closeout" | :115-121 checkpoint/closeout/audit | yes (server superset) |
| audit_date | `last_audit` date from PROFILE.md, else today | :123-138 YYYY-MM-DD, real calendar date, >= 2025-01-01, <= today UTC | **`<date> @<sha>` sent -> 400** (Q-7) |
| found | `grep -cE '^- \[[ x]\] (CRITICAL\|IMPORTANT\|ADVISORY) \|'` | :140,154 required int 0..9999 | yes |
| fixed | `grep -cE '^- \[x\] .*\| (Closed\|Verified)'` | :143,157 int 0..9999; fixed+accepted <= found | yes (greps are mutually consistent) |
| accepted | `grep -cE '^- \[x\] .*\| Accepted'` | :146,160 | yes |
| critical_open | `grep -cE '^- \[ \] CRITICAL \|'` | :149,163; critical_open <= found | yes |
| (unknown fields) | n/a | `DisallowUnknownFields` at :51 -> 400 | publish.md's "if a field is not named here it is not sent" is the right contract |

`fixtures/seed-msp-sentinel.json` matches the publish.md example payload byte for byte in field names,
types and values.

**Real POST result.** Site built from `itworks-site` @ 5a87acd into the scratchpad
(`go build -o scratchpad/audit/itworks-q ./cmd/itworks`), run with
`ITWORKS_DB=<scratch>/q.db ITWORKS_ADDR=:18083 ITWORKS_BASE_URL=http://localhost:18083`.
Payload built by following publish.md literally against `itworks-site/.itworks/`
(name `itworks`, found 5, fixed 4, accepted 0, critical_open 0, source `closed` because the origin is
`git.parallaxintelligence.xyz`, tier `closeout` because `last_audit: none`):

```
$ curl -sS -X POST http://localhost:18083/api/entries \
    -H "Content-Type: application/json" --data @payload.json
HTTP 400
{"error":"summary must be between 1 and 160 characters"}
```

**A closeout following publish.md on the plugin's own companion project gets a 400.** With the summary
shortened to 73 characters and nothing else changed:

```
HTTP 201
{"badge_url":"http://localhost:18083/badge/hixyttfjklax.svg",
 "entry_url":"http://localhost:18083/e/hixyttfjklax",
 "id":"hixyttfjklax","status":"pending"}
```

So the wire contract is sound; publish.md's *derivation rules* are what produce a rejected body
(Q-5, Q-6, Q-7). Also confirmed 201 for a summary containing an API key, an absolute path and an internal
hostname (Q-11). Rate limit confirmed by hitting 429 on the sixth POST, matching publish.md:57.

---

## 5. Lint run table

`bash -n scripts/itworks-lint.sh` -> exit 0, no output.

| # | Case | Exit | Output (one line) |
|---|---|---|---|
| a | real `itworks-site/.itworks` | **0** | `0 error(s), 0 warning(s)` |
| b | `profile: fancy` | **1** | `ERROR: PROFILE.md profile is 'fancy', must be guided|brief|expert` |
| c | open finding missing the evidence field | **1** | `ERROR: REVIEWS.md open finding does not parse (five-field grammar): - [ ] CRITICAL | security-auth | missing evidence field` |
| d | PROFILE.md deleted | **1** | `ERROR: missing <root>/.itworks/PROFILE.md` |
| e | project path containing a space | **0** | `0 error(s), 0 warning(s)` (quoting is correct throughout) |
| f | empty directory | **1** | `ERROR: no .itworks directory at <root>` |
| g | Accepted risks entry with no `Revisit when:` | **0** | `warn: REVIEWS.md Accepted risks entry has no 'Revisit when:' (pre-field entry): ...` |
| h (extra) | open malformed finding as the **last line, no trailing newline** | **0** | `0 error(s), 0 warning(s)` - **corruption passes** (Q-8) |
| i (control for h) | same line with a trailing newline | **1** | `ERROR: REVIEWS.md open finding does not parse ...` |

No crash, no stderr, no unbound-variable or word-splitting failure in any case, including the path with a
space. Behaviour matches state-format.md's Validation rules in a-g. Case h is the one divergence.

---

## 6. Questions for the owner

1. **Q-1 is the one to fix before publishing.** Do you want the injection step to stay a grep (then it
   needs two patterns: one for `${...}` and one for `"` ... `"` followed by `+`, e.g.
   `(query|execute|exec)[[:space:]]*\(.*(\+[[:space:]]*[A-Za-z_]|\$\{)`), or should injection move to the
   audit tier where taint can actually be traced? The current step is the worst of both: it looks
   mechanical and it is not.
2. **Are the runbooks meant to be pasted into a terminal, or executed by the agent?** If a human ever
   pastes them, the `--include` quoting (Q-2) is required. If only the agent runs them, it is still worth
   quoting, because the agent's shell is not guaranteed either.
3. **Should llm-security's "Fires when" detection read dependencies rather than `src/ app/`?**
   `package.json` / `go.mod` / `requirements.txt` name the AI client and cannot be hidden by a directory
   layout. That would make Q-3 structural rather than a path list to keep extending.
4. **Does publish.md want a truncation rule, or a "the assistant writes the summary" rule?** Truncating a
   user's first sentence at 160 chars mid-word is ugly; asking the closeout to write one line under 160
   and show it in the Step 5b preview is cleaner and also fixes Q-11 (the user sees exactly what goes out).
5. **Is the lint authoritative or advisory?** state-format.md:9 says its errors *are* the contract
   violations; the script's comments say open-checkbox-without-severity is deliberately a warning. One of
   the two documents should move (Q-9).
6. **Does `found` mean "found ever" or "found in the live REVIEWS.md"?** Archiving changes the published
   number (Q-12). If the wall is meant to be a lifetime record, the counts need to include
   `.itworks/archive/`.
7. **Do you want harness cases for resume and audit before 1.0?** (Q-15.) The audit tier is the only one
   that reads logic and has never been run under pressure.

---

## 7. Coverage

**Files read in full (26):**

itworks @ 0b972ac:
`references/lens-security-auth.md`, `references/lens-llm-security.md`, `references/lens-real-data.md`,
`references/lens-testing.md`, `references/lens-production-readiness.md`, `references/dependency-vetting.md`,
`references/publish.md`, `references/state-format.md`, `references/audit-method.md`,
`references/secret-patterns.grep`, `scripts/itworks-lint.sh`, `tests/pressure/pressure-tests.md`,
`tests/pressure/harness/README.md`, `tests/pressure/harness/run-case.sh`,
all 8 files under `tests/scenarios/`, `tests/pressure/harness/cases/case-1/{target.txt,pass-conditions.md}`.

itworks-site @ 5a87acd:
`internal/server/validate.go` (full), `internal/server/handlers.go` (submit handler `handleAPICreate` +
`finishPost`, plus the route table in `server.go:88-100`), `docs/SPEC.md` (Routes + POST validation +
Publish payload sections), `fixtures/seed-msp-sentinel.json`, `cmd/itworks/main.go` (to run it),
`.itworks/{PROJECT.md,PROFILE.md,REVIEWS.md}` (to build the real payload).

**Read but not in full, and why:**
- `references/glossary.md` (350 lines) - read by targeted lookup of all 49 card terms named in the five
  lenses and dependency-vetting, rather than end to end; the lane's question about it is coverage, and
  that is what the sweep answers. One miss found (Q-16).
- `tests/pressure/harness/cases/case-2..case-6/pass-conditions.md` - read the numbered check headings and
  the hard/tone split for every case (invariant 8's question: are they mechanically checkable), not the
  full prose of each check. `case-1/pass-conditions.md` read in full as the representative.
- `cases/*/fixture.md` and `cases/*/user-turns.txt` - not read; they are the harness inputs, and the lane's
  question about the harness is runnability and checkability, both answered from `run-case.sh` and the
  pass-conditions. The one thing I did check across all fixtures is the secret-pattern false-positive
  sweep, which read them by grep.
- The five `skills/*/SKILL.md` - read the state-write instructions (invariant 6) by targeted grep for
  every state field name plus the full closeout Step 5/5b and resume Step 1; not read end to end, because
  they are other lanes' scope.

**Skipped entirely:** nothing in the named scope.

**Probes run (all under `scratchpad/audit/`, nothing written to either repo):**
1. Built `q-fixture/` - git repo with `.env` (sk-proj + postgres URL), `config/aws.json` (AKIA),
   `public/app.js` (sk-ant + innerHTML), `server/db.js` (concatenated SQL), `src/index.js`
   (unauthenticated `/admin/users`), `package.json` (`^`/`~`), `tests/app.test.js` (asserts nothing).
   Ran every runnable inspect command from all five lenses and dependency-vetting against it.
2. `inj.js` + `inj.re` - isolated the injection regex against 7 injection shapes.
3. `keys.txt` - 16 key shapes through `grep -E -f` and `grep -f`.
4. False-positive sweep of both repos with the pattern file.
5. zsh vs bash reproduction of the `--include` glob abort.
6. Built and ran the real site binary on `:18083` with a scratch SQLite DB; 6 POSTs
   (literal publish.md payload, corrected payload, SSH repo_url, date-with-sha, secret-in-summary,
   rate-limit probe). Server stopped afterwards; `q.db` is scratch only.
7. `bash -n` on `itworks-lint.sh` and `run-case.sh`; 9 lint runs (a-g plus the two newline cases) against
   copies of the real `.itworks` state.
8. Glossary term sweep across all 49 guided-card terms.

**Not run, deliberately:** `tests/pressure/harness/run-case.sh`. The `claude` CLI *is* on PATH and
`bash -n` passes, so it is runnable as written on this machine - but a single case is 7 paid model calls,
and `RESULTS_DIR` is `tests/pressure/harness/results/` **inside the repository** (gitignored, but still a
repo write, which this lane forbids). Instead I verified by reading that each case's pass conditions are
checkable from a transcript alone: the hard checks are (they name exact file:line, exact strings such as
`sk_live`, exact counts, exact grammar), the tone checks are not mechanical and need a judging model,
which is what `harness/README.md` prescribes. Two notes on the runner: `RESULTS_DIR` inside the repo is a
mild trap for anyone auditing a clean tree, and `run-case.sh:79` has the `|| [ -n "$line" ]` read guard
that `itworks-lint.sh:73` is missing (Q-8).
