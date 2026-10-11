# Reviews

## Checkpoint 1 - 2026-10-11 - lenses: security-auth, testing
### Findings
- [x] CRITICAL | security-auth | API key in client code (src/app.js:12) | Closed 2026-10-11: synthetic check passes
- [x] IMPORTANT | testing | no failure-path test for login | Closed 2026-10-11: test_login_rejects_bad_password passes
- [x] CRITICAL | security-auth | API key in client code (public/app.js:1) | Accepted 2026-10-11: see Accepted risks
### Accepted risks
- 2026-10-11 | API key in client code (public/app.js:1) | User's words: "I accept this specific risk; don't rewrite my words." | Revisit when: next closeout
