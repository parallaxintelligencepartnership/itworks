# State lint benchmark

Developer-only standard-library Python. Measures the actual lint shell script in three
separately pinned artifact copies on identical retained synthetic inputs, not a Python
reimplementation. Never checks out/resets/stashes the active worktree.

```sh
python3 tests/benchmarks/state_lint.py --baseline /tmp/released-copy \
  --baseline-audit /tmp/audited-copy --candidate /tmp/candidate-copy \
  --warmup 5 --runs 30 --output /tmp/new-benchmark-results
```

All artifact copies must include scripts/ and their actual references/publish.md.
The candidate copy includes its shared awk/helper. Output must not already exist or
sit within any input artifact. Python is a developer dependency only.

Workloads contain 0/10/100/800/5000 canonical findings. Live records alternate open
IMPORTANT and evidence-closed IMPORTANT, starting open. Active workloads put every
finding in live REVIEWS; archived workloads keep floor(n/5) live and place only closed,
archive-eligible findings in one archive. Fixtures never contain real credentials or user data. Historical
lint validates active records only, so archived timing measures that existing behavior;
candidate lint does likewise. Counts are checked outside timing.

Each workload first verifies exit/classification, archive warning threshold, actual
supported count commands and byte hashes. Released v1.0.0's publication reference has
four active-only counts; audited publication has five lifetime counts; the candidate
has the five-count shell protocol. The benchmark executes the historical documented
commands directly. Expected historical archive differences and the absent fifth count
are recorded, never concealed as equality or invented implementation. Comparable
active overlapping counts must match; audited/candidate lifetime counts must match.

Five warmups and thirty measured trials rotate artifact order each iteration. Raw
JSONL is flushed/fsynced after every trial; summaries update every iteration, retaining
median/p95 (nearest-rank), min/max, trial and failure counts. Environment, exact command, helper/template/runtime/input
hashes, nanosecond timer identity, workload identities and complete correctness output remain alongside raw trials.
A RUNNING artifact is incomplete, even if some summaries exist. Failures stop timing;
fix/review the cause, retain failed evidence, then start a new output directory.

Reuse for a final release candidate only when all measured runtime, workload and
relevant toolchain/environment identities are unchanged; record that association.
Never claim cross-platform performance from one host. Compare small-input distributions
and investigate material regressions before any improvement claim. Historical counting
contract differences are expected compatibility evidence, not speed improvements.

Child process CPU time is recorded alongside wall time using standard-library
`resource.getrusage(resource.RUSAGE_CHILDREN)` deltas around each waited child.
Every trial retains availability status and user/system/total CPU seconds; summaries
retain median/p95/min/max for each CPU measure and sample counts. This measures the
waited command and its waited descendants, not the Python benchmark's own CPU time.
The helper runs commands serially so unrelated benchmark children do not contaminate
the deltas. Unsupported platforms retain explicit UNAVAILABLE status/reason rather
than numeric zero; macOS/Linux qualification expects AVAILABLE for every sample.

The first full wall-only run omitted this required available metric. That is a known
instrumentation omission, not an unavailable platform capability; retain it as
wall-time-only evidence with the complete performance gate BLOCKED. A subsequent
full run with both metrics is required to close that gap. Material regression review
checks median **or p95** increases greater than both20% and50ms on identical workloads.
