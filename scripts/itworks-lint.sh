#!/usr/bin/env bash
# itworks-lint: deterministic validator for the .itworks/ state directory.
# Usage: itworks-lint.sh [project-root]   (default: current directory)
# Exit 0 = valid (warnings allowed), exit 1 = contract violations found.
# Requires only bash + grep; no other dependencies.

root="${1:-.}"
vc="$root/.itworks"
errors=0
warnings=0

err()  { printf 'ERROR: %s\n' "$1"; errors=$((errors+1)); }
warn() { printf 'warn:  %s\n' "$1"; warnings=$((warnings+1)); }

[ -d "$vc" ] || { err "no .itworks directory at $root"; exit 1; }

for f in PROJECT.md DECISIONS.md REVIEWS.md PROFILE.md; do
  [ -f "$vc/$f" ] || err "missing $vc/$f"
done
[ "$errors" -gt 0 ] && { printf '%d error(s)\n' "$errors"; exit 1; }

SEV='(CRITICAL|IMPORTANT|ADVISORY)'
LENS='(security-auth|real-data|testing|production-readiness|llm-security)'
# Sanctioned REVIEWS.md section headings. Trailing text after the form is allowed.
HEAD='^## (Checkpoint ([0-9]+|[0-9]{4}-[0-9]{2}-[0-9]{2}[a-z]?)|Baseline checkpoint|Closeout sweep|Closeout|Reopen review|Audit|Archive)( |$)'

# --- PROFILE.md ---
profile=$(grep -E '^profile:' "$vc/PROFILE.md" | head -1 | sed -E 's/^profile:[[:space:]]*([a-z]+).*/\1/')
case "$profile" in
  guided|brief|expert) ;;
  *) err "PROFILE.md profile is '$profile', must be guided|brief|expert" ;;
esac
if ! grep -qE '^format_version:[[:space:]]*[0-9]+' "$vc/PROFILE.md"; then
  warn "PROFILE.md has no format_version (treating as v1; resume will add 'format_version: 3')"
fi

# --- MAP.md: the code map (format v3). Missing or thin is drift; resume and checkpoint write it. ---
if [ ! -f "$vc/MAP.md" ]; then
  warn "no MAP.md (v2 state; resume writes the code map from the tree and the README)"
else
  for h in "Run" "Test" "Layout" "Environment" "Gotchas"; do
    grep -q "^## $h" "$vc/MAP.md" || warn "MAP.md missing heading: ## $h"
  done
  map_lines=$(wc -l < "$vc/MAP.md" | tr -d ' ')
  if [ "$map_lines" -gt 80 ]; then
    warn "MAP.md is $map_lines lines; the cap is about 60 (a map, not a listing; remove rows that stopped being true)"
  fi
fi
while read -r key; do
  case "$key" in
    security-auth|real-data|testing|production-readiness|llm-security|"") ;;
    *) warn "PROFILE.md unknown lens_debt key: $key" ;;
  esac
done < <(grep -E '^  [a-z-]+:' "$vc/PROFILE.md" | sed -E 's/^  ([a-z-]+):.*/\1/')
if ! grep -qE '^last_audit:' "$vc/PROFILE.md"; then
  warn "PROFILE.md has no last_audit (resume will add 'last_audit: none'; a whole-application audit has never been recorded)"
fi

# --- Size drift: the state is read whole at every session start ---
reviews_lines=$(wc -l < "$vc/REVIEWS.md" | tr -d " ")
if [ "$reviews_lines" -gt 800 ]; then
  warn "REVIEWS.md is $reviews_lines lines; sections with every finding closed and no accepted risks may move to .itworks/archive/ (see state-format.md)"
fi
long_decisions=$(awk 'length($0) > 600' "$vc/DECISIONS.md" | wc -l | tr -d ' ')
if [ "$long_decisions" -gt 0 ]; then
  warn "DECISIONS.md has $long_decisions line(s) over 600 characters; a decision line is the ruling and its reason, detail belongs in docs with a path"
fi

# --- REVIEWS.md finding lines ---
# Contract: OPEN finding lines must parse (they drive the gates) -> error.
# Checked lines and severity-less checkboxes are drift, not gate risks -> warn.
in_accepted=0
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    "### Accepted risks"*) in_accepted=1 ;;
    "#"*) in_accepted=0 ;;
  esac
  # Accepted risks entries carry a Revisit when: condition (pre-field entries are drift).
  if [ "$in_accepted" -eq 1 ] && printf '%s' "$line" | grep -qE '^- [0-9]{4}-[0-9]{2}-[0-9]{2} \|'; then
    printf '%s' "$line" | grep -q 'Revisit when:' \
      || warn "REVIEWS.md Accepted risks entry has no 'Revisit when:' (pre-field entry): ${line:0:100}"
  fi
  case "$line" in
    "- [ ]"*)
      if printf '%s' "$line" | grep -qE "^- \[ \] $SEV \|"; then
        printf '%s' "$line" | grep -qE "^- \[ \] $SEV \| $LENS \| .+ \| Evidence to close: .+" \
          || err "REVIEWS.md open finding does not parse (five-field grammar): ${line:0:100}"
      else
        warn "REVIEWS.md open checkbox without severity (finding or stray checklist?): ${line:0:100}"
      fi
      ;;
    "- [x]"*)
      if printf '%s' "$line" | grep -qE "^- \[x\] $SEV \|"; then
        printf '%s' "$line" | grep -qE "^- \[x\] $SEV \| $LENS \| .*(Closed|Accepted|Verified):? ?[0-9]{4}-[0-9]{2}-[0-9]{2}" \
          || warn "REVIEWS.md checked finding lacks Closed/Accepted <date>: ${line:0:100}"
      fi
      ;;
  esac
done < "$vc/REVIEWS.md"

if grep -qE '\| Accepted:? ?[0-9]{4}' "$vc/REVIEWS.md" && ! grep -q '### Accepted risks' "$vc/REVIEWS.md"; then
  err "REVIEWS.md has Accepted findings but no '### Accepted risks' section"
fi

# Checkpoint headings (warn only; content sections are model-written prose)
while read -r h; do
  printf '%s' "$h" | grep -qE "$HEAD" \
    || warn "REVIEWS.md unsanctioned section heading: $h"
done < <(grep -E '^## ' "$vc/REVIEWS.md")

# --- Cross-file: REVIEWS.md <-> SHIPPED.md ---
# A ship record exists, so the review state and the ship record must agree.
if [ -f "$root/SHIPPED.md" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    err "SHIPPED.md exists but a CRITICAL finding is open (ship gate drift): ${line:0:100}"
  done < <(grep -E "^- \[ \] CRITICAL \|" "$vc/REVIEWS.md")

  open_all=$(grep -c '^- \[ \]' "$vc/REVIEWS.md")
  open_gate=$(grep -cE '^- \[ \] (CRITICAL|IMPORTANT) \|' "$vc/REVIEWS.md")
  accepted=$(grep -cE '^- \[x\] .*\| Accepted' "$vc/REVIEWS.md")

  if grep -q 'OUTSTANDING' "$root/SHIPPED.md" && [ "$open_all" -eq 0 ]; then
    warn "SHIPPED.md lists OUTSTANDING work but REVIEWS.md has no open findings (untracked risk)"
  fi
  if [ "$open_gate" -gt 0 ] && ! grep -q 'OUTSTANDING' "$root/SHIPPED.md"; then
    warn "REVIEWS.md has $open_gate open CRITICAL/IMPORTANT finding(s) but SHIPPED.md never says OUTSTANDING (open risk invisible to the ship record)"
  fi
  if [ "$accepted" -gt 0 ] && ! grep -qi 'accepted risks' "$root/SHIPPED.md"; then
    warn "REVIEWS.md has $accepted Accepted finding(s) but SHIPPED.md has no accepted risks section"
  fi
  # A shipped project with no recorded whole-application audit is running on runbook tiers alone.
  if grep -qE '^last_audit:[[:space:]]*none' "$vc/PROFILE.md" 2>/dev/null; then
    warn "SHIPPED.md exists but last_audit is none: no whole-application audit recorded (checkpoint and closeout never read application logic)"
  fi
fi

# --- PROJECT.md headings ---
for h in "What it is" "Who uses it" "Terminology map" "Stack" "Data" "Where it will live" "Definition of done" "Verification expectations"; do
  grep -q "^## $h" "$vc/PROJECT.md" || err "PROJECT.md missing heading: ## $h"
done

printf '%d error(s), %d warning(s)\n' "$errors" "$warnings"
[ "$errors" -eq 0 ]
