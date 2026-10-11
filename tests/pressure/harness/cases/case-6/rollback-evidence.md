# Optional disposable rollback fixture variant

Executed locally 2026-10-11 in a new TemporaryDirectory, synthetic text only.
No installed plugin, deployment, real project tag or user worktree was changed.
Select this evidence explicitly alongside fixture.md to exercise the rehearsal branch.
This proves restoration of one disposable file only, not application or data rollback.

```text
$ git init -q
exit 0
$ git add release.txt
exit 0
$ git -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm disposable release
exit 0
$ git tag ship-fixture
exit 0
$ git show ship-fixture:release.txt
version one
exit 0
$ # Only inside owned disposable fixture: write version two to release.txt
$ git restore --source=ship-fixture --worktree release.txt
exit 0
$ cat release.txt
version one
exit 0
```
