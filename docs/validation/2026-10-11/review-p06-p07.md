# Independent P06/P07 implementation review

Reviewer evaluation did not author security/staging/copy/evidence implementation.
Inspected actual helper, prescribed security scan and staging shell blocks, all four
integration modules, workflow fixture JSON and pressure rubrics. Ran disposable
synthetic Git projects only; no real credentials or source repository mutations.

Found and independently reproduced:

1. Failed shasum pipeline masked exit42 and published a successful copy with empty
   SHA digest. Root and author independently reproduced; pipefail plus checked64hex
   digest now returns1/no successful path. Reviewer rechecked exact failure.
2. Valid `-odd/source.txt` failed dirname option parsing. Parameter expansion now
   creates the correct parent; reviewer rechecked successful bytes and64hex inventory.
3. Owned literal `task[1].py` expanded as Git pathspec and committed unrelated
   `task1.py`. Root independently reproduced and added literal-pathspec handling to
   all three prescribed staging/diff/commit commands. Exact regression now passes.
4. Mutation pressure rubric required executed GREEN/RED despite fixture's explicitly
   unavailable outputs. Reviewer corrected narrowly to permit truthful NOT_VERIFIED
   held proof; source preservation and missing-test finding remain mandatory. Root
   reviews this reviewer-authored rubric change separately.

Evidence: p07-review-probes.json, p07-review-rerun.json, p06-pathspec-review.json; root
retains independent RED/GREEN files too. No original evidence was deleted.

Independent targeted commands: test_candidate_copy.py9 PASS;
test_checkpoint_staging.py2 PASS; test_secret_context.py1 PASS;
test_evidence_closure.py1 PASS. test_patch_contract.py additionally5 PASS with a PATH
lacking Python and host clients, including current helper. Existing copy tests cover
ordinary concurrent source edits, copied corruption, symlink/traversal/manifest errors,
missing dependencies and interruption, retaining source identity. Review probes add
hash backend failure and valid unusual path coverage. No remaining reproduced
blocking mechanical defect in this bounded review.

APPROVED for offline scope after repairs. The originally disclosed sequencing deviation
remains: some historical sensitivity proofs were performed after implementation, so
this batch does not meet strict regression-first sequencing for every original change.
Later revert/mutation proof cannot retroactively erase that deviation. New review
findings were independently reproduced before fixes and retained separately.

NOT RUN: Linux CI, real installed-host skill adherence/behavioral scoring, atomic
filesystem snapshots or adversarial change-and-revert guarantees. The helper does
not execute tests, prove inventory completeness or provide an OS security sandbox.
Live401 does not close a missing-regression finding; setup errors never count as RED.

Follow-up withdrawal pending runtime repair: a local core.fsmonitor hook executes
during helper git status and can mutate original source despite failed copy. Reviewer
reproduced with synthetic hook (p07-fsmonitor-review.json), notified root for independent
reproduction. This is distinct from malicious ABA edits: the helper itself launches
the configured command. Disable fsmonitor for identity collection and rerun before
P07 approval. Shared default tests also inherited global Git hooks; see
test-git-config-review.json. No real user hook/config was changed.

Staging/environment final follow-up: exact literal-pathspec regression and existing
unrelated-staged preservation both independently pass (2/2). Stronger inherited Git
config canary passes after root's shared test-environment fix; no hook ran and no
caller index/config byte changed. P06 offline mechanics approved. P07 awaits local
filter/fsmonitor guard verification; preserved TDD sequencing disclosure unchanged.

Final runtime repair independent verification: repeated the original synthetic
same-length dirty-file + advanced-mtime clean/process probes against the actual
repaired helper. Both return1 before executing configured filter, emit no successful
path and preserve original bytes. The original fsmonitor mutation command is now
suppressed; copy returns0 with original bytes preserved. Exact results retained in
p07-filter-review-rerun.json. Re-read implementation: effective executable-filter
configuration names are checked before status and configuration values are not
printed; every identity Git call disables fsmonitor and optional index locks.
The two literal-path staging tests pass again. Offline P06/P07 mechanics APPROVED
after these repairs, with all prior limitations and sequencing disclosure retained.
