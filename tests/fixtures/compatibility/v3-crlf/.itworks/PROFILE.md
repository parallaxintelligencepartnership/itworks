# Profile

format_version: 3
profile: guided        # guided | brief | expert
                       # guided: plain words, each new term gets its glossary card, short explanations
                       # brief: one context line per item, terms named with a half-line gloss
                       # expert: terse tables and one-liners, no cards, no explanations
                       # The profile changes wording ONLY. Checks and gates never vary by profile.
opted_out: []          # skill names the user told to stop auto-firing for this project
last_checkpoint: 2026-10-11 @7df7228
                       # the sha is what the cadence guard diffs against; date alone cannot measure a diff
last_audit: none
                       # set only by project-audit after its REVIEWS.md section is written; resume and
                       # closeout read it to say whether a whole-application audit is due
lens_debt:             # checkpoints run since each lens last ran; checkpoint hard-fires a lens at 3
  security-auth: 0
  llm-security: 0      # stays 0 forever in projects with no LLM/AI feature; the lens self-gates
  real-data: 0
  testing: 0
  production-readiness: 0
