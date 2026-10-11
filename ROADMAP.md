# Roadmap

Ideas agreed on but not yet built. One section per lane; move an item to the
changelog when it ships.

## Released-product hardening and optional development workflow

The [implementation backlog](docs/plans/2026-10-11-itworks-hardening/README.md)
contains 26 fully specified, pending tasks based on the October audit:

- P01–P09: compatibility patch, deterministic tests, corrected validation and
  evaluation, and protection of user work.
- U01–U07: historical-state compatibility, tested recovery, installed-plugin
  upgrade qualification, release identity and existing-user guidance.
- F01–F10: separately enabled planning/TDD, evidence runner, bounded orchestration,
  independent verification and qualified Claude/Codex/Antigravity adapters.

Execute the patch and upgrade gates first. No implementation or release is
complete merely because the tasks are planned. Existing UI-consistency ideas
below remain separate scope.

## UI consistency (staged, agreed 2026-08-08)

The problem: AI-assisted apps drift into mismatched styling - every page its
own colors, fonts, control sizes, selectors and text boxes out of alignment -
because nothing establishes a single source of styling truth at the start.

1. **Style contract at kickoff (small).** When a project has a UI, kickoff
   adds one decision: a tokens file (colors, font stack, spacing scale, corner
   radius, control sizes) is created before the first component, and the
   recorded rule is "all styling references tokens; no raw hex/px values in
   components." A file plus a DECISIONS.md line, same shape as everything
   itworks already does.
2. **Drift check at checkpoint (medium).** A review-lens step that greps new
   UI code for hardcoded colors, font-families, and magic pixel values outside
   the token file and flags them, the way the secrets scan works. Catches
   per-page divergence the moment it happens.
3. **Visual conformance (large, parked).** Detecting that rendered layouts are
   actually misaligned needs a headless browser, screenshot baselines, and
   flake handling - a testing product, not a lint rule. Revisit only if stages
   1-2 leave a real gap; most mismatched UI comes from ad-hoc values, which
   they prevent at the source.

## Pressure testing

- Replace the old six-case matrix with the corrected executable oracles and
  isolated harness in P04/P05, then qualify exact host/model configurations under
  U07 and F09/F10. The current tree has eight pressure cases; new positive controls
  and workflow cases are specified in the task plans. Keep historical results
  distinct from new qualified runs and retain every failed/incomplete attempt.
