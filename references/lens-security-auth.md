# Lens: security-auth

Review runbook. Run the inspect steps in order with the real commands; capture output as evidence. Findings use the five-field grammar from `state-format.md` with lens id `security-auth`.

## Fires when

- The user touched login, signup, users, roles, permissions, API keys, or payment code.
- Any route or page was added that should not be public.
- Closeout full sweep (always).

## Inspect

Steps 1 and 2 share ONE canonical pattern set: `references/secret-patterns.grep`, which sits next to this lens file (`PAT` below is its path). Never retype patterns inline; the file is maintained so Stripe (`sk_live_`), OpenAI project keys (`sk-proj-`), GitHub fine-grained tokens, JWTs, database connection strings with credentials in them, and AWS, Discord and Telegram tokens are covered. It holds extended regular expressions, so always read it with `grep -E -f`: plain `grep -f` treats them as basic expressions and silently matches only the PEM line. If `gitleaks` is installed (`command -v gitleaks`), prefer it: `gitleaks detect --source . --no-banner --redact` covers current files AND full git history in one run; the greps below are the no-dependency fallback.

1. **Inspect candidate secret matches without retaining values.** `PAT` is the absolute canonical pattern-file path. Scan explicit client/served directories and built bundles, then the remaining working tree, excluding dependency and git storage. A match is a candidate requiring context, not automatically a leak. Use file/line-only output; never paste matching lines or token values into REVIEWS, chat or artifacts. Do not enable shell tracing. `gitleaks`, when used, must have redaction enabled.

   ```bash
   # secret-candidate-scan
   grep -rEn -f "$PAT" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build | cut -d: -f1,2
   ```

   Scan excluded built output separately if served; exclusions never establish it clean. Inspect matching content privately and classify using actual served roots, tracked paths (`git ls-files --error-unmatch -- "$path"`), ignore rules (`git check-ignore -- "$path"`), deployment configuration and history. File names alone do not establish exposure.

   | Context | Classification and action |
   |---|---|
   | Ignored, untracked server `.env`, proven unserved and not in history | Intentional private configuration; no automatic CRITICAL. Keep excluded from commits and evidence. |
   | Matching credential in client bundle, tracked source/template or committed history | Exposure; record location and consequence, normally CRITICAL; revoke/rotate affected live credentials. |
   | `.env.example` containing placeholders only | Inspect content; placeholder template is not a credential finding. |
   | `.env.example` containing credential-shaped material | Exposure candidate even though its filename says example; inspect, never stage known material. |
   | Served/tracked/history context unknown | Unverified; name the missing evidence. Do not claim clean or invent exposure. |

2. **Scan complete git history, including removed values.** Never cap commits or infer historical cleanliness from the current tree. Retain patch line numbers only; inspect matching history privately to identify affected paths/commits, without retaining raw values.

   ```bash
   # secret-history-scan
   git log --all -p | grep -En -f "$PAT" | cut -d: -f1
   ```

   Empty output is meaningful only if git and grep executed successfully (grep exit1 means no match; exit2 is error). Run each command with failure checking; a pipeline alone cannot prove all stages succeeded. For history leaks, deletion alone is not remediation: retain rotation/revocation evidence and scope history cleanup separately.

3. **Inspect tracked configuration contents.** `git ls-files` identifies tracked `.env`, key and credential files for private content review. A filename match is not automatically CRITICAL: a placeholder `.env.example` may be intentional. Real matching values in tracked configuration require exposure assessment. An ignored server `.env` must also be proven unserved; `.gitignore` alone is insufficient.

4. **Doors actually locked.** List every route or page that should require login (from PROJECT.md "Who uses it"), then hit each WITHOUT a token or session:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<port>/<protected-route>
   ```

   Good: 401, 403, or a redirect to login. Bad: 200 with data is CRITICAL.

5. **Role boundaries** (only if PROJECT.md says roles exist). Log in as the lowest role, request an admin-only route the same way. Good: denied. Bad: CRITICAL. A hidden admin button is not access control; the endpoint behind it is.

6. **Injection.** Find queries built by gluing user text into strings. The patterns live in `references/injection-patterns.grep` beside this file (`INJ` below is its path), the same single-source rule as `PAT` above; never retype them inline:

   ```bash
   grep -rEn -f "$INJ" --include='*.js' --include='*.ts' --include='*.jsx' --include='*.tsx' --include='*.py' --include='*.go' --include='*.rb' --include='*.php' --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=vendor .
   ```

   Read every hit; a hit inside a test fixture or a comment is not a finding, a hit that glues a request value into a query is. Good: no matches (parameterized queries only). Bad: IMPORTANT at checkpoint and closeout; the audit tier raises it to CRITICAL when it traces the value to a form field or URL parameter. Checkpoint and closeout do not read application logic, so they do not make that call.

7. **Stored XSS.** `grep -rn "innerHTML\|dangerouslySetInnerHTML" <client dirs>`. Any hit that is fed by user-written data without sanitization is IMPORTANT.

8. **Password storage** (only if the app has its own login). `grep -rn "bcrypt\|argon2\|scrypt" <server dirs>`. Good: one of these libraries hashes passwords. Bad: passwords stored plain or reversibly is CRITICAL.

## Severity rubric

- **CRITICAL:** a stranger can read secrets, act as another user, or run commands (findings from steps 1-5 and 8).
- **IMPORTANT:** exploitable with effort or only by authenticated users (steps 6-7, typically).
- **ADVISORY:** hygiene: missing rate limiting, verbose error pages leaking stack traces, no CSRF token on cookie-session forms that only change low-stakes data.

## Evidence to close

Re-run the exact inspect command and retain redacted file/line-only evidence with command exit statuses. For route findings, the curl output showing 401/403. For history leaks, confirmation the key was rotated at the provider plus the clean re-grep. Never close on "changed the code, should be fine."

## Guided cards

Terms this lens touches: API key, authentication (auth), authorization, RBAC (roles), session, token, secrets, environment variables (.env), input validation, SQL injection, XSS, password hashing, HTTPS.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding. Never re-explain a term already carded this session.
