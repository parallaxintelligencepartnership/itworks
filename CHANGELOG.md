# Changelog

## 1.0.0 - 2026-09-12

First public release.

- Five lifecycle skills: kickoff (alignment interview before any code), checkpoint (evidence-backed review of what was just built), resume (replay saved state in a few lines), audit (whole-application adversarial review with independent verification), closeout (full sweep, reckoning, ship checklist, SHIPPED.md).
- Five review lenses (security and auth, LLM security, real data, testing, production readiness) plus dependency vetting.
- Project state in `.itworks/`: PROJECT, DECISIONS, REVIEWS, PROFILE, and MAP. MAP.md is the code map and gotcha list: how to run and test the project, where the important code lives, what the hosts actually are, and the corrections the project has already paid for. Written at kickoff, patched at every checkpoint, read whole at resume.
- Deterministic state linter (`scripts/itworks-lint.sh`), format version 3.
- Opt-in publishing of closeout summaries to itworks.dev, with the exact sent-field list in `references/publish.md`.
- Adversarial pressure-test harness with six cases and fixed user scripts.
