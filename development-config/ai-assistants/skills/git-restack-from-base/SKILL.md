---
name: git-restack-from-base
description: Recreate the current git branch from an explicitly provided base branch and cherry-pick the branch-only commits onto a new versioned branch. Use when a feature branch must be retargeted onto the newest integration branch or another base branch, especially for workflows like `A` 到 `A-v2`, `A-v2` 到 `A-v3`, or any request to cut a fresh branch from updated base history and migrate the current branch's commits with cherry-pick. Treat an unqualified base branch name such as `dev`, `main`, or `master` as the corresponding remote-tracking branch by default, not a local branch. In IDE workflows, first ask the user in natural language which base branch to use, then show the resolved base ref and current branch for confirmation before execution.
---

# Git Restack From Base

Use this skill to rebuild the current branch on top of an explicitly specified base branch while preserving the branch's own commits.

By default, treat an unqualified base branch name such as `dev`, `main`, `master`, or `release/1.0` as a remote branch. Resolve it to the corresponding remote-tracking ref, for example `dev` -> `origin/dev`. Only use a local base ref when the user explicitly asks for local branch state or provides a full local ref.

## Workflow

1. Ask the user in natural language: `基础分支是什么？` Do not infer it from context and do not start with a command.
2. Inspect the repository state before changing anything.
3. Run the helper script in plan mode with the provided base branch.
4. Return at least the `base_branch`, `source_branch`, and `new_branch` to the user and ask whether to continue.
5. Execute the restack only after explicit user confirmation.
6. Validate the resulting branch and report any unresolved conflicts or gaps.

Prefer using `scripts/restack_from_base.py` for branch naming, commit discovery, and command generation. Resolve that relative path against the directory containing this `SKILL.md`; do not assume the current working directory is the skill directory. The canonical helper path is `<skill-dir>/scripts/restack_from_base.py`. The script defaults to plan mode and prints `status: awaiting_confirmation`. Only run with `--apply --confirm` after the user has reviewed the printed branches and explicitly approved continuation.

## Base Ref Resolution

1. If the user provides a full remote-tracking ref such as `origin/main` or `upstream/release/1.0`, use it directly as the base ref.
2. If the user provides an unqualified branch name such as `dev`, `main`, `master`, or `release/1.0`, resolve it to the corresponding remote-tracking ref `<remote>/<branch>` by default.
3. Use `origin` as the default remote when it exists. If `origin` is absent and exactly one remote exists, use that remote. If multiple non-`origin` remotes exist, ask which remote to use.
4. Fetch the specific remote base before planning or applying, for example `git fetch origin dev`, then use `origin/dev`. Skip fetch only when the user explicitly asks to avoid it, the environment blocks it, or an explicit `--base-ref` was provided as already-fetched input.
5. Do not silently fall back to a local branch with the same name. Use a local base only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.
6. For a full remote-tracking ref such as `origin/release/1.0`, parse the first path component as the remote and fetch the remaining branch name. For an unqualified branch with slashes such as `release/1.0`, do not treat `release` as a remote unless it is a configured git remote.

## IDE Interaction Rule

In IDE usage, the first response must be a natural-language question asking for the base branch. Do not start by running the script, showing shell commands, or assuming `dev`.

The first response must contain only the base-branch question. Do not include explanations, command examples, workflow summaries, confirmation templates, or any extra text in that first turn.

Use this sequence:

1. Ask only `基础分支是什么？`
2. Wait for the user's answer.
3. Run the script in plan mode with that base branch.
4. Reply with the base branch, current branch, and new branch, then ask whether to continue.
5. Only after the user confirms, run the apply command.

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
- `--base-ref <ref>`: use an already-fetched ref instead of `<remote>/<base>`
- `--skip-fetch`: avoid `git fetch` when the environment is offline or the user wants to control fetch manually
- `--confirm`: required together with `--apply` after the user reviews the printed branches

## Execution Rules

- Require the base branch as an explicit input from the user before running the script.
- In IDE conversations, obtain that input by asking a natural-language question first, not by telling the user to execute a command.
- Resolve `scripts/restack_from_base.py` relative to this skill directory before executing it. Do not run `python3 scripts/restack_from_base.py` unless the shell is already in `<skill-dir>`.
- If the first attempt says the script is missing, check the sibling `scripts/` directory under this skill and rerun with the resolved path. Do not fall back to a manual restack until that canonical script path has been checked.
- Resolve an unqualified base branch name to `<remote>/<base>` by default. Use `origin` when present, otherwise the only configured remote; ask when multiple non-`origin` remotes exist.
- Do not silently fall back to a local branch with the same name as the requested remote base.
- Before any execution, show the user both the base branch they provided and the resolved base ref, then wait for approval.
- Abort if the working tree is dirty unless the user explicitly asks to proceed.
- Abort if there are no branch-only commits to cherry-pick.
- Use `git log --reverse <base_ref>..<source_branch>` semantics so cherry-pick order matches the original history.
- Prefer `git switch --no-track -c <new_branch> <base_ref>` to create the fresh branch without tracking the base branch.
- If a cherry-pick conflicts, stop immediately, report the conflicting commit, and tell the user to resolve and continue with `git cherry-pick --continue` or abort with `git cherry-pick --abort`.
- Do not delete the source branch automatically.

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
- whether the base ref was resolved as a remote-tracking ref, an explicit local ref, or another explicit ref
- the new branch name
- the commits selected for cherry-pick
- whether fetch was executed or skipped
- whether the run is awaiting confirmation, completed, or stopped on conflict

## References

- Read [references/base-ref-resolution.md](./references/base-ref-resolution.md) for the default base-ref resolution, freshness, and reporting rules.
