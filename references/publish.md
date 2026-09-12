# What the publish step sends

Reference for `project-closeout` Step 5b. This is the complete list. If a field is not named here, it is not sent.

## Sent

Ten fields, built from files already in the project:

| Field | Value | How it is built |
|---|---|---|
| name | project name | `grep -m1 '^# Project:' .itworks/PROJECT.md`, text after the colon, trimmed |
| summary | one line | first sentence of the "What it is" section body in `.itworks/PROJECT.md` |
| source | "public" or "closed" | "public" when the git origin host is `github.com`, `gitlab.com`, `codeberg.org`, or `sr.ht`; else "closed" |
| repo_url | the origin URL, or "" | `git remote get-url origin`; the https origin URL only when source is public, else "" |
| audit_tier | "audit" or "closeout" | "audit" when `last_audit` in `.itworks/PROFILE.md` is not "none"; else "closeout" |
| audit_date | YYYY-MM-DD | the `last_audit` date from `.itworks/PROFILE.md` when audit_tier is "audit"; else today's date |
| found | integer | count of finding lines in `.itworks/REVIEWS.md` |
| fixed | integer | count of closed finding lines |
| accepted | integer | count of accepted finding lines |
| critical_open | integer | count of open CRITICAL lines |

Exact commands for the four counts, run against `.itworks/REVIEWS.md`:

```
grep -cE '^- \[[ x]\] (CRITICAL|IMPORTANT|ADVISORY) \|' .itworks/REVIEWS.md   # found
grep -cE '^- \[x\] .*\| (Closed|Verified)' .itworks/REVIEWS.md               # fixed
grep -cE '^- \[x\] .*\| Accepted' .itworks/REVIEWS.md                        # accepted
grep -cE '^- \[ \] CRITICAL \|' .itworks/REVIEWS.md                          # critical_open
```

To get the origin host for `source`, use `git remote get-url origin` and check the host of that URL against the four allowed hosts.

### Example payload

The example from itworks `docs/SPEC.md`:

```json
{"name":"MSP Sentinel","summary":"...","source":"closed","repo_url":"","audit_tier":"audit","audit_date":"2026-09-07","found":56,"fixed":56,"accepted":0,"critical_open":0}
```

## Not sent

Never leaves the project, no matter what:

- code
- file paths
- secrets
- environment variables
- the `.itworks/` files themselves
- the user's own words
- git history
- IP addresses (the service does not store them)

## Limits

- request body capped at 8 KB
- five submissions per IP per hour
- entries are hidden until an admin approves them
- badge colors: green when the audit is under 30 days old and no critical is open; amber when the audit is 30 or more days old; red when a critical is open
- the badge can look bad on purpose. that is the point of an honest audit trail

## How to remove an entry

Open an issue on the plugin repo with the entry id, and it will be handled from there.
