# Independent review of U01

Reviewer: evaluation agent (did not implement U01). Reviewed generator, manifest,
source snapshots, fixture shapes and test assertions on 2026-10-11.

PASS: `python3 -m unittest discover -s tests/unit -p test_compatibility_fixtures.py -v`
ran 4 tests successfully, including every fixture/mode preservation assertion.
Independently fetched both pinned source blobs with `git show <commit>:references/state-format.md`:
2/2 byte-identical to retained snapshots. Independently loaded the generator with ROOT
redirected into a TemporaryDirectory and regenerated 97 files; all matched checked-in
bytes, including the manifest. No source fixture or repository state was overwritten.

No blocking finding in this bounded review. v1/v2 are honestly labeled derived legacy
state shapes, not historical binaries; actual historical-script execution remains U02.
Tests exercise real candidate shell operations and explicit diagnostic/status/count
expectations, not a second Python parser. Hash corruption test asserts SHA-256 failure.

Limits: this confirms fixture provenance, reproducibility and candidate compatibility
on this macOS host. It does not qualify Linux, installed host behavior or user-data
migration. Future generation should run in a clean disposable destination: generator
writes expected files but intentionally does not remove unrelated stale files.
