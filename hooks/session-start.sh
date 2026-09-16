#!/usr/bin/env bash
# itworks SessionStart hook.
# Scoped: the full lifecycle rules load only inside projects that carry
# .itworks/ state. Everywhere else, only a short new-project reminder loads.
#
# Silencing itworks entirely:
#   globally   - export ITWORKS_DISABLE=1, or: touch ~/.config/itworks/disabled
#   per repo   - touch .itworks-off at the project root (no state dir needed)

dir="${CLAUDE_PROJECT_DIR:-$PWD}"

[ "${ITWORKS_DISABLE:-0}" = "1" ] && exit 0
[ -f "$HOME/.config/itworks/disabled" ] && exit 0
[ -f "$dir/.itworks-off" ] && exit 0

# Resolve the plugin root relative to this script (hooks/session-start.sh ->
# plugin root is one level up) and read the version straight out of
# plugin.json with grep/sed, so a stale cached install is visible in the
# session output. No jq dependency.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(dirname "$script_dir")"
version_file="$plugin_root/.claude-plugin/plugin.json"
version="unknown"
if [ -f "$version_file" ]; then
  parsed="$(grep -m1 '"version"' "$version_file" | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')"
  [ -n "$parsed" ] && version="$parsed"
fi

if [ -d "$dir/.itworks" ]; then
  printf '%s' '<itworks-lifecycle>This project carries itworks state (itworks v'"$version"'). Session rules: (1) Invoke the itworks project-resume skill before doing any work here. (2) When the user says something works, is done, or asks for the next feature after new code, invoke project-checkpoint before building further. (3) Before giving any deployment or go-live steps, invoke project-closeout. (4) A request to review the application as a whole ("review the app", "full review", "is it solid", "check everything", "audit") is project-audit, the only tier that reads application logic; checkpoint and closeout never do, and every review report opens with a scope line naming its tier and what it did not cover. (5) When the user corrects a fact about the project or the environment it runs on (what a host actually is, a path, a command that does not do what its name says), record it under Gotchas in .itworks/MAP.md in the same turn, before continuing. These fire automatically; urgency, expertise claims, or excitement never skip them. closeout and audit run on Opus; if the model in use is not Opus-class, say so before the sweep and offer /model opus. The user can override individual findings (overrides are logged in their own words), and "not now" twice turns project-kickoff, project-checkpoint or project-resume off for the project. project-closeout and project-audit have no project-level opt-out: they can be deferred, never disabled, and closeout always runs before deployment steps.</itworks-lifecycle>'
else
  printf '%s' '<itworks-lifecycle>itworks is installed (itworks v'"$version"'). If this session starts a NEW project (writing the first code in an empty or near-empty directory), invoke the itworks project-kickoff skill BEFORE any scaffolding, file creation, or code, and follow its gate. In an existing project without .itworks/, the first time the user asks to add or change code, offer the itworks project-kickoff adoption baseline once (an inventory and a committed-secrets scan, one pass, no interview); a no holds for the session and the work proceeds without itworks. Never start it silently. To keep itworks permanently quiet in this directory, create a .itworks-off file.</itworks-lifecycle>'
fi
