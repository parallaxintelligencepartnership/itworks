LT: 196c3d82-9a39-4de3-b659-769f4d048750, 46b37df2-f86a-470d-8ec1-d5b9302fda74, 79b32e0a-4dbe-4591-80b6-80815732ec4c, f513c12a-79b2-4654-bf16-9c7444ffb456, 001d7f74-9b45-4520-ab97-1c7aa44ce1e8, 049f96d9-f326-4974-ac9c-63a59d8e7d43, cf3ad951-c8cd-494a-b28b-b4c266d3d12e, 4c473c27-f4fc-4b01-92f2-a323eab3e359
Status: In progress
Approved by Matt: 2026-10-13, "implement and deploy the outstanding tasks in this project" (covers the 1.0.2 version bump, tag, Gitea push and refreshing his local install; GitHub push is handed to Matt as a one-line command)

# Audit: outside repos and lane-report hardening (itworks 1.0.2)

## Goal

Make `project-audit` work on a repo that is not the user's own project, and fix
the lane problems found in the first real third-party audit. Lessons from that
audit are in the eight Local Tasks items above.

## Steps

1. Trigger: the skill fires on "audit this repo" or "audit <path>", even when no
   `.itworks/` exists. audit-method.md says to start the skill, not follow it by hand.
2. Outside-repo mode: a new Step 0 decides own project or outside repo. Outside
   mode writes minimal state (what it is, threat model, empty decisions, layout
   map) into an evidence folder next to the target, skips the owner interview, and
   never writes into the target tree.
3. Untrusted code: in outside mode reviewers only read; verifiers run code only in
   a sandbox with no network; the report names the isolation used.
4. Safety-filter losses: reviewers append one finding at a time, reproductions are
   worded as tests that check for the problem, every report ends with a fixed
   completion line, and the orchestrator checks the file instead of the summary.
5. Lane approval: an approved plan that already holds the lane table counts as the yes.
6. Per-finding lens: the lane lens is a default; a finding may carry its own lens.
7. Agreeable verifiers: every reproduction carries a passing control case; a lane
   whose verifier refuted nothing gets a blind re-check of a small sample.
8. Release 1.0.2: version bump, CHANGELOG, tests, tag, Gitea push, Matt's local
   install refreshed, GitHub push handed to Matt.

## What done means

The skill and method text carry all seven changes, the offline suites pass, 1.0.2
is tagged on Gitea, Matt's install reports 1.0.2, and the eight LT items are closed.

## Open questions

None.

## Where it stands

2026-10-13: plan written; editing the skill and method next.
