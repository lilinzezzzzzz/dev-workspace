---
name: git-restack-from-base
description: Recreate the current git branch from an explicitly provided base branch and cherry-pick the branch-only commits onto a new versioned branch. Use when a feature branch must be retargeted onto the newest integration branch or another base branch, especially for workflows like `A` 到 `A-v2`, `A-v2` 到 `A-v3`, or any request to cut a fresh branch from updated base history and migrate the current branch's commits with cherry-pick. Treat an unqualified base branch name such as `dev`, `main`, or `master` as the corresponding remote-tracking branch by default, not a local branch. If the user has not explicitly provided a base branch or base ref, ask for it and stop. After the user provides it, visibly show that specified base before any task execution, then show the resolved base ref and current branch for confirmation before applying.
---

# Git Restack From Base

Use this skill to rebuild the current branch on top of an explicitly specified base branch while preserving the branch's own commits.

For base ref resolution, freshness, and downgrade reporting, load and follow [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md).

## Workflow

1. Require an explicitly provided base branch or base ref before doing anything else.
2. If the request does not include one, ask the user in natural language: `基础分支是什么？` Then stop and wait. Do not infer it from context and do not start with a command.
3. If the request includes one, first visibly show the base branch or base ref exactly as the user specified it before running commands or continuing the task.
4. Inspect the repository state before changing anything.
5. Run the helper script in plan mode with the provided base branch.
6. Return at least the `base_branch`, `base_ref`, `source_branch`, and `new_branch` to the user and ask whether to continue.
7. Execute the restack only after explicit user confirmation.
8. Validate the resulting branch and report any unresolved conflicts or gaps.
9. After a successful restack and validation, ask the user whether to delete the source branch locally and remotely.
10. Delete the source branch only after the user explicitly confirms the deletion request.

Prefer using `scripts/restack_from_base.py` for branch naming, commit discovery, and command generation. Resolve that relative path against the directory containing this `SKILL.md`; do not assume the current working directory is the skill directory. The canonical helper path is `<skill-dir>/scripts/restack_from_base.py`. The script defaults to plan mode and prints `status: awaiting_confirmation`. Only run with `--apply --confirm` after the user has reviewed the printed branches and explicitly approved continuation.

## Base Ref Resolution

Follow the shared remote-base rule in [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md). The restack-specific requirement is that planning and applying both use the same resolved base ref and report the same freshness status.

## IDE Interaction Rule

In IDE usage, the first response must be a natural-language question asking for the base branch. Do not start by running the script, showing shell commands, or assuming `dev`.

The first response must contain only the base-branch question. Do not include explanations, command examples, workflow summaries, confirmation templates, or any extra text in that first turn.

If the user already provided the base branch or base ref in the current request, the first visible response must show it explicitly, for example `基础分支：dev`. Only then may you inspect repository state or run the plan command.

Use this sequence:

1. Ask only `基础分支是什么？`
2. Wait for the user's answer.
3. Reply first with the specified base branch or base ref.
4. Run the script in plan mode with that base branch.
5. Reply with the base branch, resolved base ref, current branch, and new branch, then ask whether to continue.
6. Only after the user confirms, run the apply command.

## Naming Rule

- If the current branch does not end with `-v<integer>`, append `-v2`.
- If the current branch ends with `-v<integer>`, increment the integer.
- Examples:
  - `feature/foo` -> `feature/foo-v2`
  - `feature/foo-v2` -> `feature/foo-v3`

Do not guess a different naming scheme unless the repository already uses one and the user asks to follow it.

## Commands

Use the helper script:

```bash
python3 <skill-dir>/scripts/restack_from_base.py --base dev
python3 <skill-dir>/scripts/restack_from_base.py --base origin/dev
python3 <skill-dir>/scripts/restack_from_base.py --base dev --remote upstream
python3 <skill-dir>/scripts/restack_from_base.py --base dev --apply --confirm
```

With the default resolution rules, `--base master --remote upstream` means the effective base ref is `upstream/master`, not the local `master` branch.

Useful flags:

- `--remote <name>`: remote for unqualified base branches. Omit it to use `origin` when present or the only configured remote.
- `--source-branch <name>`: restack a branch other than `HEAD`
- `--new-branch <name>`: override the generated versioned branch name
- `--base-ref <ref>`: use an explicit ref instead of resolving `<remote>/<base>`; this is not a remote-latest base unless the relevant fetch already succeeded in this session
- `--skip-fetch`: degrade to the local cached remote-tracking ref only after the user explicitly allows proceeding without verifying the latest remote base
- `--confirm`: required together with `--apply` after the user reviews the printed branches

## Execution Rules

- Require the base branch as an explicit input from the user before running the script.
- In IDE conversations, obtain that input by asking a natural-language question first, not by telling the user to execute a command.
- Do not continue the task, inspect repository state, or run commands until the user has provided a base branch or base ref and you have visibly shown that specified base to the user.
- Resolve `scripts/restack_from_base.py` relative to this skill directory before executing it. Do not run `python3 scripts/restack_from_base.py` unless the shell is already in `<skill-dir>`.
- If the first attempt says the script is missing, check the sibling `scripts/` directory under this skill and rerun with the resolved path. Do not fall back to a manual restack until that canonical script path has been checked.
- Resolve an unqualified base branch name to `<remote>/<base>` by default. Use `origin` when present, otherwise the only configured remote; ask when multiple non-`origin` remotes exist.
- Resolve and fetch the base using the shared remote-base rule before planning or applying.
- Do not silently fall back to a local branch with the same name as the requested remote base.
- Before any execution, show the user both the base branch they provided and the resolved base ref, then wait for approval.
- Abort if the working tree is dirty unless the user explicitly asks to proceed.
- Abort if there are no branch-only commits to cherry-pick.
- Use `git log --reverse <base_ref>..<source_branch>` semantics so cherry-pick order matches the original history.
- Prefer `git switch --no-track -c <new_branch> <base_ref>` to create the fresh branch without tracking the base branch.
- If a cherry-pick conflicts, stop immediately, report the conflicting commit, and tell the user to resolve and continue with `git cherry-pick --continue` or abort with `git cherry-pick --abort`.
- Do not delete the source branch as part of the restack apply command.

## Source Branch Deletion

After apply mode completes successfully and verification shows `HEAD` is on the new branch, ask whether to delete the source branch locally and remotely. This must be a separate confirmation after restack completion, not part of the pre-apply confirmation.

Before asking, resolve and show the exact refs that would be deleted:

- local source branch: `refs/heads/<source_branch>`
- remote source branch: use the source branch upstream from `git for-each-ref --format=%(upstream:short) refs/heads/<source_branch>` when present; otherwise use `<remote>/<source_branch>` only when that remote-tracking ref exists and the remote is unambiguous

Ask in natural language, for example:

`Restack 已完成。是否删除源分支？将删除本地 refs/heads/<source_branch> 和远程 <remote>/<source_branch>。`

Only run deletion commands after explicit user confirmation. Use:

```bash
git branch -D <source_branch>
git push <remote> --delete <remote_branch>
```

Deletion rules:

- Never delete the source branch if restack failed, stopped on conflict, or verification has not completed.
- Never delete the branch currently checked out; `HEAD` must be on `<new_branch>`.
- If no remote source branch is found, delete only the local source branch after confirming that no remote ref will be deleted.
- If multiple candidate remote branches exist, ask which one to delete instead of guessing.
- Report deletion results separately from the restack result.

## Verification

After apply mode completes, verify:

```bash
git status --short
git log --oneline --decorate --graph -n 15
git log --reverse <source_branch> --not <base_ref> --oneline
```

Check that:

- `HEAD` is on the new branch.
- The new branch starts from the refreshed base branch.
- Every branch-only commit from the source branch exists on the new branch in the same order.

## Reporting

Report:

- the base branch provided by the user
- the source branch
- the base ref used
- the fetched base commit SHA when fetch succeeded
- the base freshness, such as `fetched` or `local-cached`
- whether the base ref was resolved as a remote-tracking ref, an explicit local ref, or another explicit ref
- the new branch name
- the commits selected for cherry-pick
- whether fetch was executed, or whether the user explicitly allowed degrading to the local cached remote-tracking ref
- whether the run is awaiting confirmation, completed, or stopped on conflict
- whether source branch deletion was skipped, awaiting confirmation, completed, or partially completed

## References

- Read [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md) for shared base-ref resolution, freshness, and reporting rules.
- Read [references/base-ref-resolution.md](./references/base-ref-resolution.md) for restack-specific confirmation and reporting rules.
