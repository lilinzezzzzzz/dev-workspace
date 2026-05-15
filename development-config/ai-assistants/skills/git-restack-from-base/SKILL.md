---
name: git-restack-from-base
description: Recreate the current git branch on top of an explicitly provided base branch by rebasing the branch-only commits onto a new versioned branch. The new versioned branch acts as a safety net so the original source branch stays untouched. Use when a feature branch must be retargeted onto the newest integration branch or another base branch, especially for workflows like `A` 到 `A-v2`, `A-v2` 到 `A-v3`, or any request to cut a fresh branch from updated base history and migrate the current branch's commits onto it. Treat an unqualified base branch name such as `dev`, `main`, or `master` as the corresponding remote-tracking branch by default, not a local branch. If the user has not explicitly provided a base branch or base ref, ask for it and stop. After the user provides it, visibly show that specified base before any task execution, then show the resolved base ref and current branch for confirmation before applying.
---

# Git Restack From Base

Rebuild the current branch on top of an explicitly specified base branch while preserving the branch's own commits. A new versioned branch (`A` → `A-v2`, `A-v2` → `A-v3`) is created so the original source branch stays intact and recoverable.

For base ref resolution, freshness, and downgrade reporting, load and follow [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md).

## Workflow

1. **Require base branch** — If not provided, ask only `基础分支是什么？` then stop. Do not infer, assume, or start any command. The first response must contain only this question — no explanations, examples, or extra text.
2. **Show base** — Visibly show the specified base branch/ref (e.g. `基础分支：dev`) before any other action.
3. **Plan** — Resolve `<skill-dir>/scripts/restack_from_base.py` and run it in plan mode. Fetch the base first (use `--skip-fetch` only if user explicitly allows). Resolve unqualified base to `<remote>/<base>` (prefer `origin`; ask if multiple non-`origin` remotes). Never silently fall back to a local branch.
4. **Report & confirm** — Return `base_branch`, `base_ref`, `source_branch`, `new_branch`, `commits_to_rebase` count, and every plan `warning:` line. Ask whether to continue. Do not proceed without explicit confirmation.
5. **Apply** — Run `--apply --confirm` only after confirmation. The script creates the new branch with `git switch --no-track -c <new_branch> <source_branch>` and rebases with `git rebase --empty=drop --onto <base_ref> <base_ref>`. Never cherry-pick.
6. **Verify** — Check HEAD on new branch, new branch starts from refreshed base, all commits present in order, source branch untouched.
7. **Delete source branch** — Ask separately after successful restack + verification. Show exact refs to delete. Only delete after explicit confirmation.

## Pre-conditions

- Abort if working tree is dirty (unless user explicitly asks to proceed).
- Abort if no branch-only commits to rebase (`<base_ref>..<source_branch>` is empty).
- Use `git log --reverse <base_ref>..<source_branch>` semantics for commit discovery.
- Planning and applying must use the same resolved base ref and report the same freshness status.

## Naming Rule

- No `-v<integer>` suffix → append `-v2` (e.g. `feature/foo` → `feature/foo-v2`).
- Has `-v<integer>` suffix → increment (e.g. `feature/foo-v2` → `feature/foo-v3`).
- Do not guess a different scheme unless the repo uses one and the user asks.

## Commands

```bash
python3 <skill-dir>/scripts/restack_from_base.py --base dev          # plan mode (default)
python3 <skill-dir>/scripts/restack_from_base.py --base dev --apply --confirm  # apply after confirmation
```

Key flags: `--remote <name>`, `--source-branch <name>`, `--new-branch <name>`, `--base-ref <ref>`, `--skip-fetch`, `--confirm` (required with `--apply`).

If the script is missing, check `<skill-dir>/scripts/` and retry with the resolved path. Manual fallback (last resort): `git switch --no-track -c <new_branch> <source_branch>` then `git rebase --empty=drop --onto <base_ref> <base_ref>`.

## Rebase Warnings

Surface every plan warning before apply:

- **Merge commits** → flattened by default. Ask: proceed, or abort and rerun with `--rebase-merges --empty=drop --onto <base_ref> <base_ref>`.
- **GPG-signed commits** → signatures dropped. Ask: proceed, rerun with `-S`, or abort. Never silently re-sign.
- **Other local branches in range** → left on pre-rebase commits. List affected refs. Ask: proceed, rerun with `--update-refs` (git 2.38+), or abort. Never pass `--update-refs` automatically.
- **Rebase conflict** → stop immediately. Tell user to `git rebase --continue` or `git rebase --abort`. Remind source branch is untouched.
- `--empty=drop` is always used. New branch first push needs no `--force`. SHAs are rewritten.

## Source Branch Deletion

After successful restack + verification, ask whether to delete. Show exact refs:

- Local: `refs/heads/<source_branch>`
- Remote: upstream from `git for-each-ref --format=%(upstream:short) refs/heads/<source_branch>`, or `<remote>/<source_branch>` when unambiguous

Delete only after explicit confirmation:

```bash
git branch -D <source_branch>
git push <remote> --delete <remote_branch>
```

Rules: never delete if restack failed/conflict/unverified; HEAD must be on new branch; no remote ref → delete only local after confirming; multiple candidates → ask which.

## Verification

```bash
git status --short
git log --oneline --decorate --graph -n 15
git log --reverse <new_branch> --not <base_ref> --oneline
```

Check: HEAD on new branch, new branch starts from refreshed base, all commits present in order, source branch untouched.

## Reporting

Report: base branch provided, source branch, base ref, fetched base SHA, base freshness (`fetched`/`local-cached`), ref resolution type, new branch name, commits to rebase (count + list), merge/GPG/branch-range warnings, fetch status, run status (awaiting confirmation / completed / conflict), rewritten commits list, source branch deletion status.

## References

- [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md) — shared base-ref resolution, freshness, and reporting rules.
- [references/base-ref-resolution.md](./references/base-ref-resolution.md) — restack-specific confirmation and reporting rules.
