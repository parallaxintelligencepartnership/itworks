# Planning review and implementation handoff

2026-10-11. Planning is complete; implementation and release qualification remain pending.

## Authors and independent review

- Runtime reviewer authored P01–P09 after reading the scripts, state format, audit findings and current task constraints.
- Testing reviewer authored U01–U07 after inspecting the actual release tag/current branch and current official Claude installation documentation.
- Workflow reviewer authored F01–F10 against the inspected lifecycle and test implementation.
- Runtime and testing reviewers cross-reviewed the upgrade and optional-runner plans. The primary agent reviewed all three plans, selected shared compatibility boundaries and reconciled the integrated backlog.

This is a review of a plan, not a report that the future implementation meets its acceptance criteria.

## Material corrections made before handoff

| Review concern | Resolution in the final plan |
|---|---|
| A new Python prerequisite would break the shell-only released interface | Patch retains shell/awk runtime; Python execution runner is separately enabled later |
| Exact legacy acceptance joins could trigger destructive rebuilds | Empty records are invalid; nonempty ambiguous legacy linkage is read-only warning with strict gate blocking, preserving original words |
| Two benchmark implementations and mismatched trial counts | P09 owns one helper; U07 consumes 5-warmup/30-trial evidence, tied to artifact/runtime/workload identity |
| Release notes depended on qualification while qualification depended on packaged notes | U04 prepares identity; U06 commits conservative notes; P09/U05 qualify that candidate; U07 records final external evidence |
| Test-only recovery algorithm could falsely claim product protection | U03 executes the documented marked shell operations directly on synthetic fixtures, or factors a shared shell helper first |
| Copying a changing source could test inconsistent code | P07/F02 require source-before/source-after/copied-manifest agreement and preserved HEAD/index, with explicit quiescence limitations |
| Updating PLAN status invalidated every receipt | Execution status belongs only to run events; PLAN is immutable input during a run |
| Vague plan and check schemas left implementation choices open | F04/F05 specify check predicates, trusted unittest bridge and one explicit JSON block grammar for PLAN |
| A writer lock does not stop the user's editor | F08 declares the limitation, checks per-file preimages and preserves newer external edits during conflict/recovery |
| Exhausted runs could permanently own integration | F03/F07 define explicit abandon/supersede, quiescent child checks, retained evidence and linked fresh budget |
| Later task changes invalidate earlier successes | Final-candidate GREEN/regression revalidation is required; historical RED survives as provenance, repair counters do not reset |
| Parent death could leave children mutating the candidate | Launch handshake/process identity and descendant quiescence checks precede reuse; unsupported escaped processes block recovery |
| Verify-only mode had no complete task-state path | Omitted from the first optional runner; existing read-only audit remains available |
| Disabled-mode operations contradicted idempotent disable | Disable is an explicit safe exception; missing/already-disabled config is a no-op |
| UTF-8 filenames contradicted an ASCII-only protocol description | Patch's tab-separated protocol explicitly carries UTF-8 text with delimiter/control escaping |

## Checks performed during planning

1. Resolved `v1.0.0` to `0b972ac8232825d82f16023f54d3ccbeda443813`; audited HEAD remains `7df722830da8fe3a3872459e06308d2d53f4153b`. There are 41 changed tracked files between those revisions, included in planned release review.
2. Reran `python3 docs/audit/2026-10-11/reproduce.py`: 9 checks, 6 failures, 3 passing controls, exit 1. These are still-open defects, not unexpected planning failures or completed fixes.
3. Checked the 26 task definitions against the backlog: unique IDs, pending status, file scope, concrete test cases, validation commands and completion criteria.
4. Parsed the three JSON examples in the optional workflow plan with Python's standard JSON parser.
5. Validated the task dependency graph with `graphlib.TopologicalSorter`; it is acyclic and no patch/upgrade task depends on an F-series feature task.
6. Checked relative documentation links, audit-to-task mapping and the changed-file scope. New source/test paths inside tasks are proposed deliverables, not falsely claimed existing files.

## Remaining implementation-time qualifications

- Actual host CLI versions, native permissions, model identity visibility and source-type-specific install behavior must be probed during P05/U05/F09. The plan supplies acceptance cases and stop conditions; it does not guess unverified flags.
- Paid behavioral evaluations require available host/account capability and an authorized bounded budget. Missing live results remain NOT RUN/BLOCKED, not silently promoted from mocks.
- Release candidate version must be confirmed unused; release artifact identities and measured results do not exist yet. The proposed patch number is not a new tag.
- “Agy” is assumed to mean Antigravity. Resolve the exact product/surface before publishing support. No unambiguous “checkitself” project was supplied; no comparison claims about it are made.
- Performance thresholds and budgets are chosen operating defaults to validate, not measured improvements. No production reliability or latency gain is claimed from writing these plans.

Start implementation with P01 and follow the [dependency table](README.md). Preserve the audit evidence, implement regression-first, and leave optional-runner work out of the compatibility patch.
