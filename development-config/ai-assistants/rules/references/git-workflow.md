---
trigger: model_decision
description: Load for branch creation, commits, staged changes, reset, revert, rebase, merge, cherry-pick, stash, tag, push, pull, PR/MR preparation, or history-sensitive repository operations.
---
# Git Workflow Rules

Use these rules for branch, commit, rebase, merge, revert, reset, stash,
push, pull, PR/MR, or other history-sensitive repository work.

## Safety Baseline

- Preserve user work. Do not overwrite, revert, reformat, or delete existing
  changes unless explicitly requested.
- Inspect `git status` and the relevant diff before committing, rebasing,
  reverting, resetting, stashing, or switching branches.
- Do not run destructive commands, force push, broad removes, or history
  rewrites unless the user explicitly requested the operation or approved it.
- If unrelated changes exist, leave them alone. If they overlap with the
  requested work, adapt to them instead of reverting them.

## Branches And History

- Branch prefixes: `feature/*`, `bugfix/*`, `hotfix/*`, `release/*`,
  `chore/*`, `docs/*`, `refactor/*`, `test/*`, `ci/*`.
- When reverting committed changes, prefer `git revert` over `git reset` or
  force push to preserve history.
- Resolve unqualified base branches such as `dev`, `main`, or `master` as
  remote-tracking refs by default when drafting PR/MR text, reviewing diffs,
  or restacking branches.
- Use non-interactive Git commands where practical.

## Commits And Reports

- Commit only when the user explicitly asks for a commit.
- Base commit messages on staged changes or a clearly specified diff range.
- Do not claim a push, commit, merge, or rebase succeeded unless the command
  was run and its result was observed.
- Report changed refs, commits created, conflicts resolved, commands run,
  and any remaining risk for history-sensitive work.
