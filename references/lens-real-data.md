# Lens: real-data

Review runbook. Detects the "shell app" problem: screens that look finished but read nothing, save nothing, or show fake data the user believes is real. Lens id: `real-data`.

## Fires when

- The user built UI over data: lists, dashboards, tables, profiles.
- The user says "it's showing the data" or connected a form to storage.
- Closeout full sweep (always).

## Inspect

1. **Placeholder markers still wired in:**

   ```bash
   grep -rniE "lorem ipsum|placeholder|dummy|sample.?data|fake.?data|hardcoded|FIXME|mock" --include=*.js --include=*.jsx --include=*.ts --include=*.tsx --include=*.py --include=*.go --include=*.html --include=*.json src/ app/ 2>/dev/null | grep -v test | head -30
   ```

   Good: hits only in test files and seed scripts. Bad: hits in rendering or API code are IMPORTANT; CRITICAL if the user believes this data is real.

2. **Mock modules imported at runtime.** Grep the entry points for imports from `mocks/`, `fixtures/`, `__mocks__/` outside test files. Bad: IMPORTANT.

3. **The restart test** (persistence is real, not in-memory). Create a record through the app's own UI or API, stop the server process fully, start it again, read the record back:

   ```bash
   curl -s -X POST http://localhost:<port>/<create-endpoint> -d '<realistic payload>'
   # fully stop and restart the app process
   curl -s http://localhost:<port>/<read-endpoint>
   ```

   Good: the record survives the restart. Bad: it vanished; storage is a variable, not a database. CRITICAL.

4. **Round-trip fidelity.** What went in is what comes out: field-for-field compare of the created payload and the read-back record. Silently dropped fields are IMPORTANT.

5. **Displayed numbers trace to real sources.** Pick every stat, total, and count on screen and find the code that computes it. A number typed directly into the JSX or template is IMPORTANT.

Post-ship checks (only after the project has shipped, i.e. SHIPPED.md exists; from then on they run every time this lens does):

6. **Development does not point at production.** Read the local dev config, `.env`, and defaults: which database, which API base URL?

   Good: dev talks to a local or separate dev store. Bad: local development reads or writes the production database, or prod credentials sit in the dev config, is CRITICAL. New features get built against a copy, never against live users' data.

7. **Seed and reset scripts refuse production.** Find every script that drops, truncates, or seeds. Each must check its target and refuse to run against the production database (env guard, hostname check, explicit `--yes-i-mean-prod` flag).

   Good: guard present and demonstrated (run it pointed at a prod-shaped config, watch it refuse). Bad: a destructive script that would run anywhere is IMPORTANT; CRITICAL if the prod database is reachable from where the script runs.

8. **Schema changes go through migrations.** Compare the live schema to the code's expectations; look for ad-hoc ALTER/DROP applied by hand or by the assistant directly.

   Good: schema changes exist as migration files (or a documented, ordered change log), each with a way back down, applied to a backup-covered database. Bad: hand-applied schema changes on a database holding real data is IMPORTANT; a destructive change (DROP, column removal, type narrowing) with no backup taken first is CRITICAL.

## Severity rubric

- **CRITICAL:** the user believes fake data is real, or data does not survive a restart; dev pointed at the production database; destructive schema change on real data with no backup.
- **IMPORTANT:** mock imports at runtime, dropped fields, typed-in numbers, unguarded destructive scripts, hand-applied schema changes.
- **ADVISORY:** seed data still present but clearly labeled as sample content.

## Evidence to close

The restart-test transcript (create output, restart, read-back output showing the record), or the grep re-run showing markers gone from runtime code, or the code path from screen number to real computation.

## Guided cards

Terms this lens touches: persistence, database, seed data, placeholder (mock) data, CRUD, schema, backup and restore, migration, dev vs production data.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding.
