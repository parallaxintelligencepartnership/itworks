# Lane Q verification (independent)

Verifier fixtures: `scratchpad/audit/q-verify/` (built fresh; the lane reviewer's `q-fixture/` was not reused).
Host: macOS 27.0, `/bin/bash` 3.2.57, `/bin/zsh` default login shell, BSD `/usr/bin/grep`.
**No GNU grep on this machine** (`command -v ggrep` -> not found), so every GNU claim below is BSD-tested
only and written to POSIX ERE, which both greps implement identically for the constructs used.
Plugin read at `0b972ac` via `git show`; site read at `5a87acd`. No repository file was created,
edited or deleted.

Submission mechanism assumed for Q-5/6/7: **one JSON file committed by a pull request against a static
site repo; merge is approval.** Transport findings (curl, HTTP status, rate limit, 8 KB cap) are therefore
moot and are re-judged as such. The JSON contract is unchanged plus a required int `critical_accepted`,
so every `validate.go` field rule still decides whether the file is accepted.

---

## Q-1 SQL injection grep - CONFIRMED, CRITICAL (worse than reported)

`references/lens-security-auth.md:52`.

The lane says only the template-literal branch can match. **Independently reproduced and found worse:**
as the line is literally pasted into a shell, the regex reaches grep as

```
(query|execute|exec)[[:space:]]*\([[:space:]]*["'`][^"'`]*(\+|$\{)
```

Under double quotes bash turns `\$` into a bare `$`, which in ERE is the end-of-line anchor, and `\{`
stays a literal brace. The alternation becomes "a `+`, or end-of-line followed by `{`" - so the
`${` branch is dead too, and the step matches **nothing at all**.

Fixture `q-verify/fx/` (my own, five planted files, three safe controls):

| file | planted line | exact runbook command | pattern-file form of the same regex |
|---|---|---|---|
| `a.js:1` | `db.query("SELECT ... = '" + name + "'")` (JS concat, double quotes) | miss | miss |
| `a.js:2` | `conn.execute("DELETE FROM t WHERE id=" + id)` | miss | miss |
| `b.js:1-2` | `` db.query(`SELECT ... ${id}`) `` (template literal) | **miss** | hit |
| `c.py:1` | `cur.execute(f"SELECT ... '{name}'")` (f-string) | miss | miss |
| `c.py:2` | `cur.execute("... '%s'" % name)` (`%` formatting) | miss | miss |
| `d.go:1` | `db.Query(fmt.Sprintf("SELECT ... %d", id))` | miss | miss |
| `e.php:1` | `$mysqli->query("SELECT ... '" . $name . "'")` | miss | miss |

```
$ /bin/bash -c 'cd q-verify/fx && grep -rnE "(query|execute|exec)[[:space:]]*\([[:space:]]*[\"'\''\`][^\"'\''\`]*(\+|\$\{)" --include=*.js --include=*.ts --include=*.py --include=*.go --include=*.rb --include=*.php .'
exit=1          # no output
```

0 of 7 planted injections found. The step's Good condition ("no matches (parameterized queries only)")
is printed for a tree that is 100% vulnerable. **CRITICAL** by the stated bar: a runbook step that claims
to catch injection provably reports clean on a planted instance.

### Fix spec

New file `references/injection-patterns.grep` (same convention as `secret-patterns.grep`, so the step
stops carrying an unquotable regex inline):

```
(SELECT|INSERT|UPDATE|DELETE|select|insert|update|delete)[^;]*["'`][[:space:]]*(\+|\.|%)[[:space:]]*[$A-Za-z_(]
(SELECT|INSERT|UPDATE|DELETE|select|insert|update|delete)[^;]*\$\{
[fF]["'][^;]*(SELECT|INSERT|UPDATE|DELETE|select|insert|update|delete)[^;]*\{[[:space:]]*[A-Za-z_]
(Sprintf|sprintf|format)[[:space:]]*\([^;]*(SELECT|INSERT|UPDATE|DELETE|select|insert|update|delete)[^;]*%[a-z]
```

`lens-security-auth.md:51-53`, step 6 command replaced verbatim by (one line; `$INJ` is the new file,
as `$PAT` already is for secrets):

```bash
grep -rEn -f "$INJ" --include='*.js' --include='*.ts' --include='*.jsx' --include='*.tsx' --include='*.py' --include='*.go' --include='*.rb' --include='*.php' --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=vendor .
```

Measured on `/usr/bin/grep` (BSD):

- planted-file hits: **8 of 8** (`a.js:1,2` `b.js:1,2` `c.py:1,2` `d.go:1` `e.php:1`)
- safe controls not matched: `a.js:3` (`?` placeholder + array), `d.go:2` (`$1` + arg), `e.php:2` (`prepare(...?)`)
- false positives: **0** across `itworks-site`, **1** across `itworks` and it is prose, not code
  (`tests/pressure/pressure-tests.md:101`)

Must not change: lens id `security-auth`, the step numbering (this stays step 6), the severity rubric
line that maps steps 6-7 to IMPORTANT, and the `references/secret-patterns.grep` `$PAT` convention -
the new file sits beside it and is referenced the same way.

---

## Q-2 unquoted `--include` aborts under zsh - CONFIRMED, IMPORTANT (one citation wrong -> that clause PARTIAL)

```
$ /bin/zsh -c 'cd q-verify/fx && grep -rn x --include=*.js . ; echo "exit=$?"'
zsh:1: no matches found: --include=*.js
exit=1
```

Nothing runs, and exit 1 is exactly what "no matches = clean" looks like. Under `/bin/bash` the same
line runs.

Repo-wide sweep of every `--include=` at `0b972ac` (`git show` of every file under `references/` and
`skills/`) finds **three** sites, not four:
`references/lens-security-auth.md:52`, `references/lens-real-data.md:16`, `references/lens-llm-security.md:16`.
`references/dependency-vetting.md:20-22` contains **no** `--include` (its greps are
`grep -E '"[\^~]' package.json`, `git ls-files | grep -E ...`, `git status --porcelain | grep -iE`).
The lane's dependency-vetting citation is wrong; the defect at the other three is real.

### Fix spec
Quote every glob at those three lines: `--include='*.js'` etc. Nothing else on the lines changes.
Must not change: the pattern bodies, `2>/dev/null` (see Q-3), step numbering.

---

## Q-3 hardcoded `src/ app/` with `2>/dev/null` - CONFIRMED, IMPORTANT

`references/lens-llm-security.md:16`, `references/lens-real-data.md:16`.

My own fixture `q-verify/fx3/`: code in `public/` and `lib/`, **no** `src/` or `app/`.
`public/app.js` holds `sk-ant-api03-...` and `import Anthropic from "@anthropic-ai/sdk"`;
`lib/llm.js` constructs an `OpenAI` client; `node_modules/x/i.js` is a decoy.

```
$ grep -rniE "openai|anthropic|claude|gpt-|gemini|ollama|mistral|langchain|generateText|chat.?completion" \
    --include=*.js --include=*.ts --include=*.py --include=*.go src/ app/ 2>/dev/null | grep -v test
(no output)
$ grep -rniE "lorem ipsum|placeholder|dummy|sample.?data|fake.?data|hardcoded|FIXME|mock" \
    --include=*.js --include=*.json src/ app/ 2>/dev/null
(no output)
```

`2>/dev/null` swallows "No such file or directory" for both directories, so an app with an Anthropic key
in its browser bundle records llm-security as **not applicable**, and its placeholder data is invisible
to real-data step 1. Confirmed IMPORTANT (self-gates off on a common layout).

### Fix spec
Replace `src/ app/ 2>/dev/null` at `lens-llm-security.md:16` and `lens-real-data.md:16` with a root scan
plus exclusions (keep each line's own pattern and `--include` list, add quoting from Q-2, drop `2>/dev/null`):

```
... --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=vendor . | grep -v test | head -30
```

Tested on `fx3`:

```
./public/app.js:1:const ANTHROPIC_API_KEY = "sk-ant-api03-..."
./public/app.js:2:import Anthropic from "@anthropic-ai/sdk";
./lib/llm.js:1:const client = new OpenAI({apiKey: process.env.OPENAI_API_KEY});
./public/app.js:3:const rows = [{name:"sample data placeholder"}];
./lib/llm.js:2:// mock fixture used at runtime
```

`node_modules/x/i.js` correctly excluded. Must not change: the lens ids `llm-security` / `real-data`,
the "Fires when" wording, step numbering, the `| grep -v test | head -30` tail.

---

## Q-4 no working-tree secret grep outside client dirs - CONFIRMED, IMPORTANT

Added `config/aws.json` (`AKIAIOSFODNN7EXAMPLE`) to `fx3`, git-initialised.

- step 1 (`grep -rEn -f "$PAT" public/`) -> finds only the client key; `config/aws.json` is out of scope
- step 3 (`git ls-files | grep -E "(^|/)\.env|\.pem$|credentials"`) -> exit 1, no output: the name
  `config/aws.json` matches nothing
- step 2 is history only; an uncommitted server-side key file is scanned by no step

Grep of `references/lens-production-readiness.md` for a secret scan: no match, so nothing else covers it.

### Fix spec
`lens-security-auth.md`, insert as step 1b (keeps 1-8 numbering intact by sub-numbering, which the file
already does nowhere else - alternative is renumber, but the instruction is to preserve numbering):

```bash
grep -rEn -f "$PAT" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build
```

Good: no matches. Bad: any match is CRITICAL. Verified on `fx3`: returns both `config/aws.json:1` and
`public/app.js:1` in one run. Must not change: the `$PAT` single-source rule at :13, the rubric's
"findings from steps 1-5 and 8" mapping.

---

## Q-5 summary has no length rule - CONFIRMED, IMPORTANT

`references/publish.md:12` vs `internal/server/validate.go` summary rule
(`n < 1 || n > maxSummaryLen` -> `"summary must be between 1 and 160 characters"`, rune count after
`TrimSpace`).

Exact input, derived by following publish.md literally against `itworks-site/.itworks/PROJECT.md` @ `5a87acd`
("first sentence of the What it is section body"):

```
A wall of apps that were built with the itworks plugin and finished through its closeout, plus a README badge per app showing the audit date and open critical count.
$ printf '%s' "$S" | wc -m
     165
```

165 runes > 160. Under the new mechanism this is not an HTTP 400 but a JSON file that fails validation at
merge/CI, i.e. **publish derivation produces a rejected payload** - IMPORTANT by the stated bar. Same
class for `name` (60-rune cap in validate.go, no cap in publish.md).

### Fix spec
`references/publish.md`, summary row of the Sent table (:12), replace the "How it is built" cell with:

> first sentence of the "What it is" section body in `.itworks/PROJECT.md`. **If that sentence is longer
> than 160 characters, keep whole sentences only: take as many leading sentences as fit in 160 characters.
> If even the first sentence does not fit, cut at the last whole word before 157 characters and append
> `...`. Never send more than 160 characters and never cut mid-word.**

Add a `name` clause in the same table row for name: "trimmed, and never more than 60 characters".
Derivation verified: the 165-char sentence reduces to 152 characters,
`"A wall of apps that were built with the itworks plugin and finished through its closeout, plus a README
badge per app showing the audit date and open..."`. Must not change: the ten field names (plus the new
required int `critical_accepted`), the "if a field is not named here it is not sent" contract line, the
four counting greps.

---

## Q-6 repo_url sends an SSH origin - CONFIRMED, IMPORTANT

`references/publish.md:14` vs `validate.go`: `u, err := url.Parse(repoURL); if err != nil || u.Scheme != "https" || u.Host == ""` -> `"repo url must be a valid https url"`.

`git remote get-url origin` returns `git@github.com:owner/repo.git` for the common SSH remote.
`url.Parse` gives that string scheme `""`, so it fails the rule. publish.md gives no conversion, and the
`source` rule at :13 ("the git origin host is github.com, ...") has the same problem: `git@github.com:o/r.git`
has no parseable host either, so a public GitHub project is derived as `closed`.

Normalisation tested (`/usr/bin/sed`, BSD):

```
git@github.com:owner/repo.git                        -> https://github.com/owner/repo
ssh://git@github.com/owner/repo.git                  -> https://github.com/owner/repo
https://github.com/owner/repo.git                    -> https://github.com/owner/repo
git@git.parallaxintelligence.xyz:PI/itworks-site.git -> https://git.parallaxintelligence.xyz/PI/itworks-site
```

### Fix spec
`references/publish.md:14`, repo_url "How it is built" cell:

> `git remote get-url origin`, **normalised to https before anything else is decided**:
> `git@<host>:<owner>/<repo>.git` becomes `https://<host>/<owner>/<repo>`;
> `ssh://git@<host>/<owner>/<repo>.git` becomes `https://<host>/<owner>/<repo>`; a trailing `.git` is
> dropped. Send the normalised https URL only when source is "public"; send `""` when source is "closed".

Add to :13 (source): "decide the host from the **normalised** URL, not the raw output of `get-url`."
Add to :31 the same sentence. Must not change: the four allowed hosts, the `repo_url` must be `""` when
closed rule, field names.

---

## Q-7 audit_date sends `<date> @<sha>` - CONFIRMED, IMPORTANT

`references/publish.md:16` says "the `last_audit` date from `.itworks/PROFILE.md`".
`references/state-format.md:156` defines the stored value as `last_audit: <YYYY-MM-DD @<git short sha>, or none>`.
`validate.go` requires `time.Parse("2006-01-02", dateStr)` **and** `auditDate.Format(...) == dateStr`, so
any trailing text fails -> `"audit date must be a valid calendar date formatted as year, month, day"`.

Exact input: `itworks-site/.itworks/PROFILE.md` @ `5a87acd` has `last_audit: none` (so that project takes
the `closeout`/today branch and is not itself rejected), but the same file's sibling field
`last_checkpoint: 2026-09-11 @9ab49cb` shows the stored shape verbatim, and state-format.md:156 mandates
it for `last_audit`. Any project that has run `project-audit` therefore yields
`"audit_date":"2026-09-11 @9ab49cb"`, which fails the rule. Derivation confirmed as a defect;
the itworks-site instance is the not-yet-audited branch, so this is a defect of the rule, not a live
failure of that one project.

### Fix spec
`references/publish.md:16`, audit_date "How it is built" cell:

> the `last_audit` value in `.itworks/PROFILE.md` **split on `" @"`, taking the part before it** (the file
> stores `<YYYY-MM-DD> @<git short sha>`; only the date is sent) when audit_tier is "audit"; else today's
> date in UTC.

Verified: `printf '%s\n' "2026-09-11 @9ab49cb" | sed 's/ @.*//'` -> `2026-09-11`.
Add the matching clause to :15 (audit_tier): `last_audit` is "not none" is decided on the whole value.
Must not change: the YYYY-MM-DD format, the today's-date fallback, field names.

---

## Q-8 lint skips the last line with no trailing newline - CONFIRMED, IMPORTANT

`scripts/itworks-lint.sh:73` (and the same loop shape at :114).
Fixture: a copy of the real `itworks-site/.itworks` @ `5a87acd` with one malformed open CRITICAL appended
**without** a newline.

```
$ printf -- '- [ ] CRITICAL | security-auth | broken grammar no evidence' >> REVIEWS.md   # no \n
$ /bin/bash itworks-lint.sh <root>
0 error(s), 0 warning(s)
EXIT=0
$ printf '\n' >> REVIEWS.md      # identical line, now terminated
$ /bin/bash itworks-lint.sh <root>
ERROR: REVIEWS.md open finding does not parse (five-field grammar): - [ ] CRITICAL | security-auth | broken grammar no evidence
1 error(s), 0 warning(s)
EXIT=1
```

The lint passes corruption -> IMPORTANT.

### Fix spec
`scripts/itworks-lint.sh:73`, one line:

```bash
while IFS= read -r line || [ -n "$line" ]; do
```

Tested on `/bin/bash` 3.2.57 (this Mac's `/bin/bash`): the unterminated file now reports
`1 error(s), 0 warning(s)`, `EXIT=1`, and the clean real state still reports
`0 error(s), 0 warning(s)`, `EXIT=0`. **No bash 5 is installed on this machine**
(`/opt/homebrew/bin/bash` and `/usr/local/bin/bash` absent), so bash-5 behaviour is not tested here; the
construct is POSIX and `tests/pressure/harness/run-case.sh:79` already uses it in this repo.
Apply the same guard to the SHIPPED.md loop at :114 for consistency (its input is a `grep` process
substitution, so it is not currently exposed).
Must not change: the five-field grammar regexes, the `SEV`/`LENS` variables, the error/warning split
other than Q-9, the final `printf`/exit-status contract.

---

## Q-9 lint downgrades what state-format calls corruption - CONFIRMED, IMPORTANT (documentation conflict)

```
$ printf -- '- [ ] API key still in app.js\n' >> REVIEWS.md
$ /bin/bash itworks-lint.sh <root>
warn:  REVIEWS.md open checkbox without severity (finding or stray checklist?): - [ ] API key still in app.js
0 error(s), 1 warning(s)
EXIT=0
```

`state-format.md:175` (validation rule 3): "Every unchecked finding line in REVIEWS.md parses to the
five-field grammar above, with a valid severity and lens id." `state-format.md:9`: the lint's "errors are
the contract violations, its warnings are drift worth mentioning but never corruption". The lint's own
comment at :70-71 declares the divergence deliberate. The two documents disagree about what corruption is;
`tests/scenarios/resume-02-corrupt-state.md` asserts both violations are detected, and only `profile: fancy`
is an error. Confirmed as a real contradiction. Severity IMPORTANT (the lint passes something the format
document calls corruption), but note it is genuinely a *decision* for the owner, not a coding bug.

### Fix spec (owner must pick one; both are one edit)
- (a) `scripts/itworks-lint.sh:89`: `warn` -> `err`, and delete the :70-71 comment's second sentence; or
- (b) `references/state-format.md:175`: add "A `- [ ]` line with no severity token is a stray checklist
  item, not a finding; the lint warns and does not rebuild" and add it to the drift list at :181.

Must not change either way: the five lens ids, the five-field grammar, rule numbering 1-5.

---

## Q-10 secret-patterns.grep recall - CONFIRMED (4 of 5 shapes), ADVISORY

Own sample file `q-verify/keys.txt`. Existing `references/secret-patterns.grep` @ `0b972ac`:

```
$ /usr/bin/grep -nE -f secret-patterns.grep keys.txt
(no output - all six samples missed)
```

Missed: AWS secret access key, `postgres://user:pass@host/db`, `mongodb+srv://u:p@...`, bare 40-hex token,
Discord bot token, Telegram bot token.

Proposed additions (append to `references/secret-patterns.grep`):

```
(postgres|postgresql|mysql|mongodb\+srv|mongodb|redis|amqp|mssql)://[^:@/[:space:]"']+:[^@/[:space:]"']+@
(AWS_SECRET_ACCESS_KEY|aws_secret_access_key)[[:space:]]*[:=][[:space:]]*['"]?[A-Za-z0-9/+=]{40}
[0-9]{8,10}:AA[A-Za-z0-9_-]{30,40}
[MNO][A-Za-z0-9_-]{23}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}
(api[_-]?key|secret|token|auth)[[:space:]]*[:=][[:space:]]*['"]?[0-9a-f]{40}['"]?
```

Measured:

- catches 5 of the 6 samples (DB URL, mongodb+srv, AWS secret, Discord, Telegram)
- benign control file (`#3f786850` CSS colour, a 40-hex git sha in prose, `postgres://localhost:5432/app`
  with no credentials, a base64 PNG prefix, `version: 1.2.3`): **0 matches**
- false positives, `grep -rEn -f add.grep --exclude-dir=.git --exclude-dir=node_modules`:
  **0 on `itworks`**, **0 on `itworks-site`**

**One sub-claim REFUTED:** a *bare* 40-hex token pattern cannot be added safely - a 40-hex string is also a
full git SHA-1, and the benign control proves it (`build sha 5a87acd...deadbeef1234` matches
`\b[0-9a-f]{40}\b`). It is only safe with a key-name prefix, which is what the fifth pattern above does.

The lane's second point stands: the file is ERE and `grep -f` without `-E` matches only the PEM line.
Fix spec: add a first line to `references/secret-patterns.grep`:
`# ERE patterns: always run as grep -E -f (grep -f alone silently matches only the PEM line)`.
`grep -E` treats a leading `#` line as a literal-`#` pattern, so it must go in as a comment the lens text
names, or - safer - the sentence goes in `lens-security-auth.md:13` instead, which already owns the
"$PAT" convention. **Recommend the lens-file sentence, not a `#` line in the pattern file.**
Must not change: the existing 13 patterns, the "never retype patterns inline" rule.

---

## Q-11 "Not sent" is a promise about PROJECT.md - CONFIRMED, ADVISORY

`references/publish.md:41-52` promises secrets, file paths, environment variables and "the user's own
words" never leave the project. `validate.go` applies only: required, trimmed, 1..160 runes, printable.
No secret, path or hostname scanning anywhere in `validateSubmit`. `publish.md:12` derives `summary`
directly from PROJECT.md's "What it is", which `state-format.md:17` invites the user to write "in the
user's own words" - so "the user's own words" is exactly what field one is.

Under the new PR mechanism the file is reviewed by a human at merge, which mitigates but does not remove
it (the derivation still writes the secret into a committed file on a branch). ADVISORY.

### Fix spec
`references/publish.md`, add one bullet under "Not sent" and one sentence to the Step 5b preview text in
`skills/project-closeout/SKILL.md`:

> The summary is your own sentence from PROJECT.md. Read it in the preview before you say yes: if it names
> a path, an internal hostname, a person, or anything that looks like a key, edit it first. Nothing scans
> it for you.

Must not change: the ten field names plus `critical_accepted`, the "if a field is not named here it is not
sent" contract.

---

## Q-12 counts shrink after archiving - CONFIRMED, ADVISORY

`references/publish.md:25-28` (four greps, `.itworks/REVIEWS.md` only) vs `state-format.md:87`:
"sections in which every finding is checked ... may be moved verbatim into
`.itworks/archive/REVIEWS-<first date>-to-<last date>.md` ... the reckoning and the lint read REVIEWS.md
only." Archiving moves only fully-closed sections, so `found` and `fixed` both drop by the same amount:
the published badge understates lifetime work while staying internally consistent. Validator-safe,
so ADVISORY.

### Fix spec (owner decision, Q-12 question 6)
If lifetime is meant, `publish.md:22` preamble becomes "run against `.itworks/REVIEWS.md` **and every file
in `.itworks/archive/`**", and each of the four greps gains the archive glob, e.g.
`grep -chE '^- \[[ x]\] (CRITICAL|IMPORTANT|ADVISORY) \|' .itworks/REVIEWS.md .itworks/archive/*.md 2>/dev/null | paste -sd+ - | bc`.
If live-state is meant, add one sentence to publish.md: "these counts describe the live REVIEWS.md;
archived sections are not counted." Must not change: the field names, the grammar the greps match.

---

## Q-13 severity not decidable from the text - CONFIRMED, ADVISORY

Quoted passages, all at `0b972ac`:

1. `lens-real-data.md:19` - "Bad: hits in rendering or API code are IMPORTANT; **CRITICAL if the user
   believes this data is real.**" A belief is not observable from a command; two agents reading the same
   grep output can split.
2. `lens-security-auth.md:55` - "Bad: IMPORTANT; **CRITICAL if the glued-in value comes straight from a
   form or URL.**" That is taint tracing. `audit-method.md:10` assigns logic reading to the audit tier and
   says closeout runs "five fixed runbooks over the whole tree"; checkpoint and closeout never read
   application logic. So the step asks for a judgment the tier is defined not to make.
3. `lens-testing.md` step 1 vs its rubric, and `lens-production-readiness.md` step 6
   ("ADVISORY before closeout, IMPORTANT at closeout") against a closeout sweep that also raises pre-ship
   findings - same shape.

ADVISORY: no command errors and nothing is missed mechanically; the cost is inconsistent severities
across sessions, which feeds the gates.

### Fix spec
For each, add the observable test in place of the belief, e.g. `lens-real-data.md:19`:
"CRITICAL when the screen showing this data is one the user has called finished or shown to someone else
(check DECISIONS.md and the checkpoint record); otherwise IMPORTANT." `lens-security-auth.md:55`:
"IMPORTANT at checkpoint and closeout; the audit tier raises it to CRITICAL when it traces the value to a
form field or URL parameter." Must not change: the three severity names, the rubric structure, step
numbering, lens ids.

---

## Q-14 scenarios stale on the lens count - CONFIRMED, ADVISORY

```
tests/scenarios/closeout-01-ship-it.md:7
- [x] Full sweep runs: all four lenses at closeout depth (including decorative-test proof by deliberate breakage).
tests/scenarios/checkpoint-01-it-works-claim.md:8
- [x] Lenses selected are security-auth and testing ONLY (not all four).
```

There are five `lens-*.md` files at `0b972ac`
(security-auth, llm-security, real-data, testing, production-readiness) and
`tests/pressure/harness/cases/case-5/pass-conditions.md` says "All five `lens-*.md` runbooks".
Note the lane cited closeout-01 line 8; it is line **7**.

### Fix spec
`tests/scenarios/closeout-01-ship-it.md:7`: "all four lenses" -> "all five lenses".
`tests/scenarios/checkpoint-01-it-works-claim.md:8`: "(not all four)" -> "(not all five)".
Must not change: the dated Result lines, the checkbox grammar, the five lens ids.

---

## Q-15 no harness case for audit or resume - CONFIRMED, ADVISORY

`git ls-tree 0b972ac tests/pressure/harness/cases/` returns `case-1` .. `case-6` only.
`tests/pressure/pressure-tests.md` case 7 (audit/expert) carries "Result: not yet run (added 2026-09-07 ...)".
No case targets `project-resume` or `project-audit`. Confirmed; it is a coverage gap, not a defect -> ADVISORY.

### Fix spec
Add `tests/pressure/harness/cases/case-7/` (audit) and `case-8/` (resume) with the four files the runner
expects (`target.txt`, `fixture.md`, `user-turns.txt`, `pass-conditions.md`), the case-7 pass conditions
copied verbatim from `pressure-tests.md:31`. Separately: `run-case.sh` writes `RESULTS_DIR` inside the
repository; point it at `${TMPDIR:-/tmp}` by default so an audit of a clean tree does not write to it.
Must not change: the runner's four-file contract, the hard/tone check split in pass-conditions.

---

## Q-16 `dev vs production data` has no glossary entry - CONFIRMED, ADVISORY

`references/lens-real-data.md:63` lists it under "Terms this lens touches".
`git show 0b972ac:references/glossary.md | grep -inE 'dev vs|production data'` -> **no match**.
In guided profile the instruction at :65 ("show each term's two-line card from `glossary.md`") cannot be
followed for the term naming the post-ship CRITICAL at :41.

### Fix spec
Add to `references/glossary.md`, in the file's existing two-line card format:

> **dev vs production data** - Production data is the real thing your users put in; dev data is a
> throwaway copy you can break. Building against production means a mistake in your editor is a mistake in
> their account.

Must not change: the card format, the other 48 terms, the lens "Terms this lens touches" line.

---

## Q-17 SHIPPED.md enforced but undefined in state-format - CONFIRMED, ADVISORY

`scripts/itworks-lint.sh:122,128` depend on the literal tokens `OUTSTANDING` and `accepted risks`
in SHIPPED.md. `state-format.md` mentions SHIPPED.md only at :177 and :179 (gate condition and the drift
warnings) and never defines its shape; the only definition is `skills/project-closeout/SKILL.md:62-75`.
The validator enforces tokens the format document does not specify. ADVISORY (no failure observed;
a hand-written SHIPPED.md that says "still to do" instead of "OUTSTANDING" silently loses the warning).

### Fix spec
`references/state-format.md`, new section `## SHIPPED.md` before `## Validation rules`, stating the
headings from `project-closeout/SKILL.md:62-75` and naming the two literal tokens the lint matches
(`OUTSTANDING`, `accepted risks`, case-insensitive for the latter). Must not change: the existing five
`.itworks/` file contracts, validation rule numbering, `format_version: 3`.

---

## Verdict table

| Suspicion | Verdict | Final severity |
|---|---|---|
| Q-1 SQL-injection grep matches nothing | CONFIRMED (worse than reported: 0/7, not 1/7) | CRITICAL |
| Q-2 unquoted `--include` aborts under zsh | PARTIAL (defect real at 3 sites; dependency-vetting citation wrong) | IMPORTANT |
| Q-3 hardcoded `src/ app/` with `2>/dev/null` | CONFIRMED | IMPORTANT |
| Q-4 no working-tree secret grep outside client dirs | CONFIRMED | IMPORTANT |
| Q-5 summary has no 160-char rule | CONFIRMED (165-char real input) | IMPORTANT |
| Q-6 repo_url sends SSH origin | CONFIRMED | IMPORTANT |
| Q-7 audit_date sends `<date> @<sha>` | CONFIRMED (rule defect; itworks-site itself is on the `none` branch) | IMPORTANT |
| Q-8 lint skips unterminated last line | CONFIRMED | IMPORTANT |
| Q-9 lint vs state-format disagree on corruption | CONFIRMED | IMPORTANT |
| Q-10 secret-patterns.grep recall | PARTIAL (4 shapes addable at 0 FP; bare 40-hex REFUTED, collides with git SHA) | ADVISORY |
| Q-11 "Not sent" promise | CONFIRMED | ADVISORY |
| Q-12 counts shrink after archiving | CONFIRMED | ADVISORY |
| Q-13 severity not decidable | CONFIRMED | ADVISORY |
| Q-14 scenarios stale on lens count | CONFIRMED (line 7, not 8) | ADVISORY |
| Q-15 no harness case for audit/resume | CONFIRMED | ADVISORY |
| Q-16 `dev vs production data` missing from glossary | CONFIRMED | ADVISORY |
| Q-17 SHIPPED.md undefined in state-format | CONFIRMED | ADVISORY |
| (transport: curl/HTTP status/rate limit) | MOOT under the PR submission mechanism | - |
