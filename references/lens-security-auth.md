# Lens: security-auth

Review runbook. Run the inspect steps in order with the real commands; capture output as evidence. Findings use the five-field grammar from `state-format.md` with lens id `security-auth`.

## Fires when

- The user touched login, signup, users, roles, permissions, API keys, or payment code.
- Any route or page was added that should not be public.
- Closeout full sweep (always).

## Inspect

Steps 1 and 2 share ONE canonical pattern set: `references/secret-patterns.grep`, which sits next to this lens file (`PAT` below is its path). Never retype patterns inline; the file is maintained so Stripe (`sk_live_`), OpenAI project keys (`sk-proj-`), GitHub fine-grained tokens, and JWTs are covered. If `gitleaks` is installed (`command -v gitleaks`), prefer it: `gitleaks detect --source . --no-banner` covers current files AND full git history in one run; the greps below are the no-dependency fallback.

1. **Secrets in client-reachable code.** Run against every directory served to browsers AND the built bundle (`dist/`, `build/`, `public/`):

   ```bash
   grep -rEn -f "$PAT" <client dirs>
   ```

   Good: no matches. Bad: any match is CRITICAL.

2. **Secrets committed to git history, not just current files.** Stream the whole history; never cap the commit count or build a `git grep $(git rev-list ...)` argument list (it silently truncates and can overflow argv):

   ```bash
   git log --all -p | grep -En -f "$PAT" | head -20
   ```

   Good: nothing. Bad: CRITICAL even if the current file is clean. History is public once pushed; a leaked key must be rotated at the provider, not just deleted from the file.

3. **`.env` or key files tracked by git:**

   ```bash
   git ls-files | grep -E "(^|/)\.env|\.pem$|credentials"
   ```

   Good: nothing, and `.gitignore` contains `.env`. Bad: CRITICAL.

4. **Doors actually locked.** List every route or page that should require login (from PROJECT.md "Who uses it"), then hit each WITHOUT a token or session:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<port>/<protected-route>
   ```

   Good: 401, 403, or a redirect to login. Bad: 200 with data is CRITICAL.

5. **Role boundaries** (only if PROJECT.md says roles exist). Log in as the lowest role, request an admin-only route the same way. Good: denied. Bad: CRITICAL. A hidden admin button is not access control; the endpoint behind it is.

6. **Injection.** Find queries built by gluing user text into strings:

   ```bash
   grep -rnE "(query|execute|exec)[[:space:]]*\([[:space:]]*[\"'\`][^\"'\`]*(\+|\$\{)" --include=*.js --include=*.ts --include=*.py --include=*.go --include=*.rb --include=*.php .
   ```

   Good: no matches (parameterized queries only). Bad: IMPORTANT; CRITICAL if the glued-in value comes straight from a form or URL.

7. **Stored XSS.** `grep -rn "innerHTML\|dangerouslySetInnerHTML" <client dirs>`. Any hit that is fed by user-written data without sanitization is IMPORTANT.

8. **Password storage** (only if the app has its own login). `grep -rn "bcrypt\|argon2\|scrypt" <server dirs>`. Good: one of these libraries hashes passwords. Bad: passwords stored plain or reversibly is CRITICAL.

## Severity rubric

- **CRITICAL:** a stranger can read secrets, act as another user, or run commands (findings from steps 1-5 and 8).
- **IMPORTANT:** exploitable with effort or only by authenticated users (steps 6-7, typically).
- **ADVISORY:** hygiene: missing rate limiting, verbose error pages leaking stack traces, no CSRF token on cookie-session forms that only change low-stakes data.

## Evidence to close

Re-run the exact inspect command and paste output showing it clean. For route findings, the curl output showing 401/403. For history leaks, confirmation the key was rotated at the provider plus the clean re-grep. Never close on "changed the code, should be fine."

## Guided cards

Terms this lens touches: API key, authentication (auth), authorization, RBAC (roles), session, token, secrets, environment variables (.env), input validation, SQL injection, XSS, password hashing, HTTPS.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding. Never re-explain a term already carded this session.
