# Roadmap

Ideas agreed on but not yet built. One section per lane; move an item to the
changelog when it ships.

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

- Run the split-role harness (tests/pressure/harness/) as the standard matrix:
  all 6 cases x sonnet x 3 runs after any skill wording change, and before any
  version announce. Haiku is out of scope per the README model note.
