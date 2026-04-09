---
name: git-checkout-branch
description: 基于当前分支的真实修改内容和当前 `HEAD`，推断一个符合仓库分支约定或 Git Flow 风格的新分支名，并在确认后直接从当前分支切出。适用于“根据当前未提交改动新建分支”“把当前修改带到新分支”“按 diff 自动生成 `feature/`、`hotfix/`、`release/` 风格分支名”等场景。先检查真实 diff，再给 1 个强推荐分支名；如果工作区为空、改动主题混杂或仓库已有不同命名规范，要先说明。
---

# Git Checkout Branch

Use this skill to create a new branch from the current `HEAD` while keeping the current working tree changes intact.

## Core Rules

1. Inspect the real repository state first. Never invent a branch topic.
2. Always cut the new branch from the current `HEAD`. Do not silently switch base branches, stash changes, or rewrite history.
3. Prefer repository-local naming conventions when visible from existing local or remote refs.
4. If no local convention is visible, default to Git Flow-compatible core prefixes:
   - `feature/` for new work, refactor tied to active development, or ordinary non-urgent changes
   - `hotfix/` only for urgent production fixes explicitly indicated by the user
   - `release/` for versioning, release preparation, or stabilization
   - `bugfix/` and `chore/` are team extensions, not the default; use them only if the repository already uses them or the user explicitly asks
5. Give one strong recommendation. If the diff mixes unrelated topics, stop and ask the user to split the work or state the intended focus.
6. Unless the user already supplied an exact branch name and explicitly asked to execute immediately, propose the branch name first and wait for confirmation before switching.

## Workflow

1. Inspect the current branch, current diff, and visible naming conventions.

```bash
git branch --show-current
git status --short
git diff --staged --stat
git diff --stat
git branch --all --format='%(refname:short)'
```

If the summary is not enough to infer the topic, inspect `git diff --staged` and `git diff`.

2. Infer the primary topic from evidence, in this order:
   - changed paths and filenames
   - added or removed symbols, config keys, API names, or error paths
   - repeated nouns or module names in the diff
   - the user's stated intent in the current request

Do not derive the topic from an imagined future commit message.

3. Choose the prefix.
   - `feature/`: net-new capability, API or schema extension, refactor tied to ongoing development, or no stronger signal
   - `hotfix/`: explicit production incident, online urgent fix, or release-blocking repair
   - `release/`: version bump, packaging, release note preparation, cutover, or release hardening
   - `bugfix/`: ordinary defect fix only when the repo already uses `bugfix/` or the user explicitly wants it
   - `chore/`: tooling, CI, dependency, or repository maintenance only when the repo already uses `chore/` or the user explicitly wants it

4. Generate the slug.
   - Use 2-5 lowercase English words in kebab-case
   - Prefer `<domain>-<action>` or `<module>-<problem>`
   - Remove vague words such as `update`, `change`, `misc`, `stuff`
   - Keep only ASCII letters, digits, and `-`
   - Keep it under 40 characters when practical

5. Validate the proposal.
   - The branch name must describe the dominant topic, not every touched file
   - If the working tree is clean, say there is no diff-based topic to infer unless the user provides one
   - If the diff spans unrelated modules or concerns, say the change set is too mixed for reliable auto-naming
   - If the proposed branch already exists, add a short disambiguator only after checking refs
   - If the repo's existing branch prefixes conflict with the default proposal, follow the repo convention and say so explicitly

6. Execute after confirmation.

Prefer:

```bash
git switch -c <branch-name>
```

Fallback for older Git:

```bash
git checkout -b <branch-name>
```

7. Verify and report.

```bash
git branch --show-current
git status --short
```

Report the original branch, the new branch, the prefix rationale, and the evidence used to infer the slug.

## Output Shape

Before execution, reply in this shape:

```text
当前分支：<current-branch>

检测到的主要改动：
- <1 line summary>
- <optional 1 line supporting evidence>

建议分支名：<prefix/slug>
- 前缀依据：<why this is feature/hotfix/release/...>
- 命名依据：<how the slug came from files, symbols, or request intent>

是否切换到该新分支？
```

If blocked, say exactly why:
- working tree is clean
- diff topic is mixed
- existing repo naming convention conflicts with the default proposal
- branch already exists and needs a different name

## Safety Notes

- Do not auto-commit, auto-stash, or auto-reset changes.
- Do not change the base branch implicitly.
- Do not claim the result follows "Git Flow" if the repository clearly uses another naming scheme.
- If only part of the current changes should move to the new branch, say that a plain branch switch is insufficient and the user likely needs selective staging, `git stash --keep-index`, or a separate commit workflow.

## Examples

- auth token refresh endpoint -> `feature/auth-refresh-token`
- nil pagination guard -> `bugfix/pagination-nil-guard` only when `bugfix/` exists in the repo; otherwise `feature/pagination-nil-guard`
- urgent payment callback repair -> `hotfix/payment-callback-timeout`
- cut `1.8.0` release prep -> `release/1-8-0`
