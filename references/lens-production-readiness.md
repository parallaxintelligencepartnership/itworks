# Lens: production-readiness

Review runbook. Whether real people can rely on this app, and what happens to them when something breaks. Lens id: `production-readiness`.

## Fires when

- "Can people use it yet", deploy or hosting questions.
- Real user data is arriving or about to.
- Closeout full sweep (always).

## Inspect

1. **Forced-failure UX.** Break a dependency on purpose (stop the database, point the API at a dead port, submit garbage input) and look at what a user sees.

   Good: a plain-language error and the app stays usable. Bad: a raw stack trace on screen is IMPORTANT (it leaks internals); a hang or blank page is IMPORTANT.

2. **Errors are recorded somewhere findable.** Trigger the same failure and check server output or the log file.

   Good: a timestamped error with enough context to debug. Bad: silence is IMPORTANT.

3. **Backup and restore for real data** (only if PROJECT.md says data is real). Does a backup exist, is it automatic, and has a restore been performed at least once?

   Good: restore actually tested. Bad: no backup for real user data is CRITICAL at closeout, IMPORTANT before.

4. **Dependencies are pinned and locked.**

   ```bash
   git ls-files | grep -E "package-lock|pnpm-lock|yarn.lock|go.sum|poetry.lock|uv.lock|Gemfile.lock"
   grep -E '"[\^~]' package.json 2>/dev/null
   ```

   Good: lockfile committed; no floating ranges for direct dependencies. Bad: no committed lockfile is IMPORTANT.

5. **Exposure review.** What ports listen, what is meant to be public, and is HTTPS in front of anything on the internet?

   Good: matches PROJECT.md "Where it will live". Bad: internet-exposed HTTP with logins is CRITICAL.

6. **Deploy story written down.** The exact steps (or a script) to update the running app exist in the repo.

   Good: a README section or script. Bad: "I redo it by hand from memory" is ADVISORY before closeout, IMPORTANT at closeout.

7. **Spend caps and rate limits** (only if the app calls paid services per PROJECT.md, or exposes any public write endpoint). Three checks:

   - A spend cap or hard budget alarm exists at each paid provider (OpenAI, Anthropic, Stripe, Twilio, cloud). Usually not verifiable from the CLI: ask, and record an unverified "yes" as "not verified live:" with the provider console page as the evidence to close.
   - Every route that triggers a paid call has a per-user or per-IP rate limit. Find the routes (grep for the API client calls, trace to their handlers), then prove the limit: hammer one route and show the 429.
   - Public write endpoints (signup, contact forms, anything that inserts) have some abuse brake: rate limit, captcha, or auth.

   Good: caps set, hammer test returns 429. Bad: a public endpoint that triggers paid calls with no rate limit is CRITICAL (this is the surprise-bill disaster: one scripted stranger can spend real money all night); paid services with no provider-side cap is IMPORTANT; unlimited public writes with no paid call behind them is IMPORTANT.

## Severity rubric

- **CRITICAL:** real user data with no backup at ship; logins over plain HTTP on the internet; public endpoint triggering paid API calls with no rate limit.
- **IMPORTANT:** stack traces shown to users, silent errors, no lockfile, undocumented deploy at ship, paid services with no provider spend cap, unlimited public writes.
- **ADVISORY:** everything else in this lens before closeout escalation applies.

## Evidence to close

The forced-failure transcript showing the friendly error plus the matching log line; the restore-test output; `git ls-files` output showing the lockfile.

## Guided cards

Terms this lens touches: deploy, build, staging vs production, port, domain and DNS, monitoring, logging, backup and restore, lockfile, version pinning, HTTPS, rate limiting, spend cap.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding.
