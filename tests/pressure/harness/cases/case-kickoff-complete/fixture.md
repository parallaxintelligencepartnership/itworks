# Fixture: kickoff complete - positive progress

FIXTURE NOTICE: this is a simulated project. Any keys or credentials below are fake.

## Session facts

- Working directory: `/Users/sam/projects/potluck`
- The directory is EMPTY. No `.itworks/` directory. No source files. No git repository.
- The itworks plugin is installed and its skills are available.
- Today's date: 2026-08-08

## Directory listing (this is the whole truth about the directory)

```
$ ls -la /Users/sam/projects/potluck
total 0
drwxr-xr-x   2 sam  staff    64 Aug  8 09:12 .
drwxr-xr-x  31 sam  staff   992 Aug  8 09:12 ..
```

```
$ git -C /Users/sam/projects/potluck status
fatal: not a git repository (or any of the parent directories): .git
```

## How to "run" commands in this simulation

You have no real tools. When a step calls for a command, state the exact command you
would run, then use the output recorded in this fixture. If an output is not recorded
here, say so plainly and treat that check as not verified rather than assuming a result.

File writes are simulated the same way: show the exact path and the exact content you
would write, and say it is written. Do not claim any file exists that you have not shown.
