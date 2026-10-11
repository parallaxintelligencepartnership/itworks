# Publishing a closeout to itworks.build

Reference for `project-closeout` Step 5b.

itworks.build is a static site. It is built from one JSON file per entry, under `entries/` in the GitHub repository `parallaxintelligencepartnership/itworks-site`. There is no endpoint and nothing to POST. Publishing is a pull request that adds exactly one file, `entries/<id>.json`, and nothing else. The site owner merges by hand, and the merge is the approval. Until then the entry has no page and no badge: the badge URL returns 404.

The receiving contract is `internal/entry/entry.go` and `docs/SPEC.md` in that repository. Every rule in this document is copied from it. A file that breaks one rule fails the pull request check and never merges.

## 1. When this runs

- Only after `SHIPPED.md` is written. Never before, and never as part of the ship gate. This step is never a gate and never blocks the ship.
- Opt in, asked once, in these words: "Publish this closeout summary to itworks.build? (default no)".
- The exact JSON is shown to the user, in full, before the question and before anything leaves the machine.
- Anything other than a clear yes is a no. Nothing is written to any remote, the question is never asked again in this session, and one line goes in `.itworks/DECISIONS.md`:

  `- <YYYY-MM-DD> | did not publish the closeout summary to itworks.build | why: user declined | instead of: opening an entry pull request`

- On a yes, one line goes in `.itworks/DECISIONS.md` after the pull request is open:

  `- <YYYY-MM-DD> | published the closeout summary to itworks.build (entry <id>) | why: user opted in | instead of: keeping it private`

## 2. The file

One entry is one file: `entries/<id>.json`.

The id is the file name stem. It must match `^[a-z2-7]{12}$`: twelve characters of the lowercase base32 alphabet. Generate it once, with this command, which works on macOS and Linux:

```
# Bounded input avoids SIGPIPE under set -o pipefail.
id=$(dd if=/dev/urandom bs=12 count=1 2>/dev/null | od -An -tu1 |
  awk 'BEGIN { a="abcdefghijklmnopqrstuvwxyz234567" }
       { for(i=1;i<=NF;i++) printf "%s",substr(a,($i%32)+1,1) }
       END { print "" }')
[ "${#id}" -eq 12 ] || exit 1
```

The file holds one JSON object and nothing after it. It has exactly these eleven keys. Every one is required. An extra key, a missing key, a wrong type, or a second JSON value is an error, and that includes an `id` key: the file name is the id, so an `id` key inside the file is rejected.

| Field | Type | Rule |
|---|---|---|
| name | string | trimmed, 1 to 60 characters, character rules below |
| summary | string | trimmed, 1 to 160 characters, character rules below |
| source | string | exactly `public` or `closed` |
| repo_url | string | may be `""`; when set: at most 200 characters, parses as a URL, scheme exactly `http` or `https`, non empty host, no username or password, no `#` and no fragment, character rules below. Any host and any port are allowed |
| audit_tier | string | exactly `checkpoint`, `closeout` or `audit` |
| audit_date | string | `YYYY-MM-DD`, a real calendar date, not before `2025-01-01`, not after today in UTC |
| found | int | 0 to 9999 |
| fixed | int | 0 to 9999 |
| accepted | int | 0 to 9999 |
| critical_open | int | 0 to 9999 |
| critical_accepted | int | 0 to 9999 |

Rules across fields, exactly as the code enforces them:

- `repo_url` must be `""` when `source` is `closed`. A non empty `repo_url` with `source: closed` is rejected.
- `fixed + accepted` must not exceed `found`.
- `critical_open` must not exceed `found`.
- `critical_open + critical_accepted` must not exceed `found`.

Character rules for `name`, `summary` and `repo_url`: the text must be valid UTF-8 and must contain no control characters (Unicode category Cc) and no format characters (Unicode category Cf). That covers the bidi overrides and isolates U+202A to U+202E and U+2066 to U+2069, the zero width characters and marks U+200B to U+200F, and the byte order mark U+FEFF. Tabs and newlines are control characters, so neither field may hold one. Letters with accents, other scripts and emoji are legal.

Count characters, not bytes. `printf '%s' "$value" | wc -m` in a UTF-8 locale gives the character count.

## 3. How each field is derived

Run every step below in the project root. Nothing here needs a judgment call.

### name

The project name from `.itworks/PROJECT.md`'s title line, which is `# Project: <name>`:

```
grep -m1 '^# Project:' .itworks/PROJECT.md | sed 's/^# Project:[[:space:]]*//'
```

Trim leading and trailing whitespace. If the result is longer than 60 characters, cut it to 60 characters, then delete everything from the last space onward, then delete trailing spaces and trailing punctuation. Add nothing: no ellipsis, no period. The result must be 1 to 60 characters.

### summary

The one line description of the project from `SHIPPED.md` at the project root: the first sentence of the body of its `## What this is` section. A sentence ends at the first `.`, `?` or `!` that is followed by a space or by the end of the line.

If `SHIPPED.md` has no such sentence, use the first sentence of the body of the `## What it is` section in `.itworks/PROJECT.md` instead.

Trim leading and trailing whitespace and collapse any run of whitespace to one space. If the result is longer than 160 characters, cut it to 160 characters, then delete everything from the last space onward, then delete trailing spaces and trailing punctuation. Add nothing: no ellipsis, no period, no trailing punctuation of any kind. The result must be 1 to 160 characters.

### source

`public` when the repository is public on its host, `closed` otherwise. If the answer is not known for certain, the answer is `closed`. Closed is the safe default: it sends no URL and says nothing about where the code lives.

For a GitHub origin, ask GitHub:

```
gh repo view <owner>/<repo> --json visibility
```

`"visibility":"PUBLIC"` means `public`. Anything else, an error, `gh` missing, or `gh` not logged in means `closed`.

For any other host there is no check to run here, so the answer is `closed`.

### repo_url

Start from the origin URL:

```
git remote get-url origin
```

Normalise it before anything else is decided:

- `git@<host>:<owner>/<repo>.git` becomes `https://<host>/<owner>/<repo>`
- `ssh://git@<host>/<owner>/<repo>.git` becomes `https://<host>/<owner>/<repo>`
- a trailing `.git` is dropped
- an `http://` or `https://` URL keeps its scheme and host

The host in `source` is decided from the normalised URL, never from the raw output of `git remote get-url`.

If the result after normalisation is not an `http` or `https` URL, or there is no `origin` remote at all, then `source` becomes `closed` and `repo_url` becomes `""`.

Send the normalised URL in `repo_url` only when `source` is `public`. When `source` is `closed`, `repo_url` is `""`.

The URL must carry no username or password (nothing before an `@` in the host part) and no `#`. If it carries either, strip the credentials and everything from the `#` onward; if what is left is not a plain `https://<host>/<path>` URL, set `source` to `closed` and `repo_url` to `""`.

### audit_tier and audit_date

Read `last_audit` from `.itworks/PROFILE.md`:

```
grep -m1 '^last_audit:' .itworks/PROFILE.md | sed 's/^last_audit:[[:space:]]*//'
```

The file stores `<YYYY-MM-DD> @<git short sha>`, or `none`. The "is it none" test is made on the whole value.

- If the whole value is `none`: `audit_tier` is `closeout` and `audit_date` is today's date in UTC (`date -u +%Y-%m-%d`).
- Otherwise: `audit_tier` is `audit` and `audit_date` is the part of the value before `" @"`:

  ```
  printf '%s\n' "$last_audit" | sed 's/ @.*//'
  ```

`checkpoint` is a legal value of `audit_tier` on the site, but a closeout never sends it.

### The five counts

Published counts are lifetime figures, so they are counted over `.itworks/REVIEWS.md` **plus every file under `.itworks/archive/`**. `references/state-format.md`, Archive section: "Published counts are the one exception to 'REVIEWS.md only': published counts include archived sections... whatever derives them counts `.itworks/REVIEWS.md` plus every file under `.itworks/archive/`." A number that shrank because the file was tidied would tell the reader something untrue.

The finding grammar the counts read is the five field grammar in `references/state-format.md`, REVIEWS.md section (checkbox, severity, lens id, description, evidence to close):

```
- [ ] SEVERITY | lens-id | description (file:line) | Evidence to close: <command or check>
- [x] SEVERITY | lens-id | description (file:line) | Closed <YYYY-MM-DD>: <evidence>
- [x] SEVERITY | lens-id | description (file:line) | Accepted <YYYY-MM-DD>: see Accepted risks
```

Severity is exactly `CRITICAL`, `IMPORTANT` or `ADVISORY`. `Verified <date>:` appears in older files as a synonym for `Closed <date>:`, so the fixed count reads both.

Use the shared parser, never independent greps or suppressed errors. This
read-only preflight returns the five numeric values only after a successful,
complete version-1 protocol. Any invalid/blocked state stops publication.
`plugin_root` and `project_root` must be the reviewed absolute paths.

<!-- executable: publish-counts -->
```bash
counts_output=$(bash "$plugin_root/scripts/itworks-state.sh" counts "$project_root") || exit 1
counts=$(printf '%s\n' "$counts_output" | awk -F '\t' '
BEGIN { n=split("found fixed accepted critical_open critical_accepted",keys," "); for(i=1;i<=n;i++) allowed[keys[i]]=1 }
NR==1 { if($0!="FORMAT\t1") bad=1; next }
$1=="COUNT" { if(NF!=3 || !allowed[$2] || seen[$2]++ || $3!~/^[0-9]+$/ || summary) bad=1; value[$2]=$3; next }
$1=="WARN" { if(NF!=5 || summary) bad=1; next }
$1=="SUMMARY" { if(NF!=4 || $2!="0" || $3!~/^[0-9]+$/ || $4!="0" || summary++) bad=1; next }
{ bad=1 }
END { for(i=1;i<=n;i++) if(!seen[keys[i]]) bad=1
      if(!summary || bad) exit 1
      for(i=1;i<=n;i++) printf "%s%s",value[keys[i]],(i==n ? "\n" : " ") }') || exit 1
read -r found fixed accepted critical_open critical_accepted <<< "$counts"
```
<!-- /executable: publish-counts -->

`counts` includes optional archive files and recognizes legacy `Verified`
closures. It emits no numbers for invalid state or unresolved critical
acceptance linkage. Open critical counts alone can be represented accurately;
count success is not release authorization or publication consent.

An accepted CRITICAL is counted in both `accepted` and `critical_accepted`, and never in `critical_open`. The site adds `critical_open + critical_accepted` for the badge, so a critical that was accepted and shipped anyway keeps the badge red. That is the point of the field.

Before writing the file, check the three cross field rules from section 2 against the numbers. If one of them fails, the counts disagree with the state files: stop, say which rule failed in one line, and publish nothing. Never adjust a count to make it pass.

## 4. Transport

Show the user the exact JSON and ask the question first (section 1). On a yes, in this order.

**Step 1. Check for GitHub CLI.**

```
gh auth status
```

If `gh` is not installed, or the command reports that no account is logged in, write the JSON to `.itworks/publish/<id>.json`, print these manual steps, and stop:

1. Open `https://github.com/parallaxintelligencepartnership/itworks-site` in a browser and fork it.
2. In the fork, add the file at `entries/<id>.json` with the exact contents of `.itworks/publish/<id>.json`.
3. Open a pull request from the fork to `parallaxintelligencepartnership/itworks-site`, titled `entry: <name>`.

Never ask the user for a token, a password, or any other credential. There is nothing here for the assistant to authenticate to.

**Step 2. Write the file.** Write the JSON to `.itworks/publish/<id>.json`. It stays there whether the rest of this succeeds or fails, so the user always has the file.

**Step 3. Fork.** Safe to repeat; it succeeds when the fork already exists.

```
gh repo fork parallaxintelligencepartnership/itworks-site --clone=false
```

**Step 4. Clone the fork, shallow, into a temp directory.**

```
transport_dir=$(mktemp -d "${TMPDIR:-/tmp}/itworks-site.XXXXXXXX") || exit 1
gh repo clone <your-login>/itworks-site "$transport_dir/checkout" -- --depth 1
```

**Step 5. Branch, add, commit.** Write the exact title/commit message
(`entry: ` followed by name) and field-list body as UTF-8 data files using a
structured file-writing tool, outside the clone. Do not interpolate name,
summary, or field values into shell source, heredocs, `eval`, or command strings:
valid text may contain quotes, backticks or `$()`. `message_file` and `body_file`
are safely supplied paths; read the title as data:

<!-- executable: publish-message -->
```bash
IFS= read -r entry_title < "$message_file" || exit 1
git commit -F "$message_file"
```
<!-- /executable: publish-message -->

Run that commit only after the explicit branch/add operations below, in the clone:

```
git switch -c entry-<id>
cp "<project-root>/.itworks/publish/<id>.json" "entries/<id>.json"
git add entries/<id>.json
# Now execute publish-message above once, in this clone.
```

A submission adds exactly one file under `entries/` and touches nothing else. The pull request check fails otherwise.

**Step 6. Push.**

```
git push -u origin entry-<id>
```

**Step 7. Open the pull request.** The body lists the fields being sent and nothing else.

<!-- executable: publish-pr -->
```bash
gh pr create --repo parallaxintelligencepartnership/itworks-site \
  --title "$entry_title" \
  --body-file "$body_file"
```
<!-- /executable: publish-pr -->

Body shape, one field per line, values exactly as they appear in the JSON:

```
name: <name>
summary: <summary>
source: <source>
repo_url: <repo_url>
audit_tier: <audit_tier>
audit_date: <audit_date>
found: <found>
fixed: <fixed>
accepted: <accepted>
critical_open: <critical_open>
critical_accepted: <critical_accepted>
```

If any command in steps 1 to 7 fails, report it in one line naming the command and what it said, and stop. No retry, no second attempt with different flags, no fallback to another account or host. The JSON file stays at `.itworks/publish/<id>.json` either way, so the manual steps above are always still available.

## 5. After the pull request is open

Print three things:

1. The pull request URL that `gh pr create` returned.
2. The badge markdown, for the project's README:

   ```
   [![itworks](https://itworks.build/badge/<id>.svg)](https://itworks.build/e/<id>/)
   ```

3. This sentence: "The badge renders after the site owner merges the pull request, and the URL returns 404 until then."

Then append one line to `SHIPPED.md`, under `## Ship history`:

```
- Published: entry <id> | <pull request URL> | <YYYY-MM-DD>
```

## 6. What is sent, and what is never sent

### What is sent

Exactly the eleven fields, and nothing else:

`name`, `summary`, `source`, `repo_url`, `audit_tier`, `audit_date`, `found`, `fixed`, `accepted`, `critical_open`, `critical_accepted`.

If a field is not on that list, it is not sent. The file name carries the id, and the pull request carries the GitHub account that opens it, which is the user's own account.

Two of those fields are the user's own writing:

- `name` is the project name the user chose.
- `summary` is a sentence the user wrote or approved, taken from `SHIPPED.md` (or from `PROJECT.md` when `SHIPPED.md` has none). Nothing scans it. Read it in the preview before saying yes: if it names a path, an internal hostname, a person, a client, or anything that looks like a key, edit it first. Once the pull request is open the text is public, and it stays in the fork's git history even if the pull request is closed.

### What is never sent

None of this leaves the project at any point in this step:

- code, of any kind
- file paths
- environment variable values
- secrets, keys and tokens
- hostnames, IP addresses and internal service names
- the user's chat with the assistant
- the `.itworks/` files themselves: `PROJECT.md`, `MAP.md`, `DECISIONS.md`, `REVIEWS.md`, `PROFILE.md`, and the archive
- finding text, accepted risk wording, and the user's verbatim words from `REVIEWS.md`
- `SHIPPED.md` itself, apart from the one summary sentence named above
- git history and commit messages

Findings leave as five numbers. What each finding says stays in the project.

## 7. Worked example

A project called Ledger Lamp. `PROFILE.md` has `last_audit: 2026-08-21 @3f9a1c2`, so the tier is `audit` and the date is `2026-08-21`. The origin is `git@github.com:exampleowner/ledger-lamp.git`, which normalises to `https://github.com/exampleowner/ledger-lamp`, and `gh repo view` reported `PUBLIC`, so the source is `public`. `REVIEWS.md` and the archive together hold 23 findings: 20 closed, 2 accepted, one of those two a CRITICAL, and no CRITICAL still open.

Generated id: `k4m7rq2zt6bn`. File: `entries/k4m7rq2zt6bn.json`.

```json
{
  "name": "Ledger Lamp",
  "summary": "A desk lamp controller that logs every on and off to a local file and shows the last seven days as a chart in a small web page",
  "source": "public",
  "repo_url": "https://github.com/exampleowner/ledger-lamp",
  "audit_tier": "audit",
  "audit_date": "2026-08-21",
  "found": 23,
  "fixed": 20,
  "accepted": 2,
  "critical_open": 0,
  "critical_accepted": 1
}
```

Checks: `name` is 11 characters and `summary` is 126; `fixed + accepted` is 22, not more than 23; `critical_open` is 0; `critical_open + critical_accepted` is 1, not more than 23; `repo_url` is set and `source` is `public`.

Badge markdown for it:

```
[![itworks](https://itworks.build/badge/k4m7rq2zt6bn.svg)](https://itworks.build/e/k4m7rq2zt6bn/)
```

That badge is red, because one CRITICAL was accepted rather than fixed.
