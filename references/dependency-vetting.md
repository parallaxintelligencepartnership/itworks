# Dependency vetting

Small fixed runbook, not a lens. Runs whenever the diff adds or changes dependencies (checkpoint and kickoff invoke it; it never counts against the two-lens cap). Findings use the five-field grammar with the lens id of the nearest concern, usually `security-auth` for malicious/nonexistent packages and `production-readiness` for pinning problems.

Why this exists: AI assistants sometimes suggest package names that do not exist (attackers register those names and wait), names one letter off from the real package (typosquats), or packages that were legitimate once and have since been handed to a hostile maintainer. A beginner cannot tell a real package from a trap by looking at the install command. Supply chain attacks through package registries are a routine occurrence, not a theoretical one.

## Inspect (per new or changed package)

1. **It exists and it is the one you meant.** Look the exact name up on the official registry (`npm view <pkg>`, `pip index versions <pkg>` or the PyPI page, `go list -m <mod>@latest`, crates.io, etc.).

   Good: the package exists, and its description, repository link, and README match what it is being used for. Bad: name not found (the AI may have invented it; NEVER "fix" this by fuzzy-matching to a similar name) is CRITICAL; a near-miss name where a much more popular package differs by a character or word order (`react-dom` vs `reactdom`) is CRITICAL until the intended one is confirmed.

2. **Someone real maintains it.** Check last publish date, repository activity, and adoption (weekly downloads, dependents).

   Good: active repository, meaningful adoption, or a known org behind it. Bad: abandoned for years, near-zero adoption, or brand-new with a generic name, used for anything security- or data-touching, is IMPORTANT; fine for a toy usage is ADVISORY.

3. **Pinned exact, lockfile committed.**

   ```bash
   grep -E '"[\^~]' package.json 2>/dev/null   # floating ranges (npm)
   git ls-files | grep -E "package-lock|pnpm-lock|yarn.lock|go.sum|poetry.lock|uv.lock|Gemfile.lock|Cargo.lock|composer.lock"
   git status --porcelain | grep -iE "lock"    # lockfile changed but not staged?
   ```

   Good: exact versions for direct dependencies, lockfile tracked and committed with the change that altered it. Bad: floating ranges or an uncommitted/absent lockfile is IMPORTANT.

4. **Install scripts and weight** (quick look, not a deep audit). Does the package run install-time scripts, and is a whole framework being pulled in for one function?

   Good: no surprises. Bad: install-time script in an obscure package touching secrets or network is IMPORTANT; a large dependency where ten lines of code would do is ADVISORY (name the ten-line alternative).

## Severity rubric

- **CRITICAL:** package does not exist on the registry, or the name is a probable typosquat of a popular package.
- **IMPORTANT:** unmaintained or near-zero-adoption package in a security- or data-touching role; floating version ranges; lockfile missing or uncommitted; suspicious install scripts.
- **ADVISORY:** heavyweight dependency for a trivial job; abandoned package in a cosmetic role.

## Evidence to close

The registry lookup output showing the exact intended package; the grep showing no floating ranges; `git ls-files` showing the lockfile tracked.

## Guided cards

Terms this runbook touches: dependency (package), package registry, typosquatting, lockfile, version pinning, supply chain attack.

In guided profile, show each term's two-line card from `glossary.md` the first time it appears in a finding.
