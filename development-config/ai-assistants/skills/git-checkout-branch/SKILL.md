---
name: git-checkout-branch
description: 基于用户明确提供的远程基础分支和当前分支的真实修改内容，推断一个符合仓库分支约定或常见团队前缀的新分支名，并在确认后从该远程基础分支切出新分支。适用于“先确认远程基础分支，再根据当前未提交改动新建分支”“把当前修改带到新分支”“按 diff 自动生成 `feature/`、`bugfix/`、`hotfix/`、`release/`、`chore/`、`docs/`、`refactor/`、`test/`、`ci/` 风格分支名”等场景。先问清基础分支并优先按远程跟踪分支解析，再检查真实 diff 并给 1 个强推荐分支名；如果工作区为空、改动主题混杂或基础分支不明确，要先说明。
---

# Git Checkout Branch

Use this skill to create a new branch from an explicit remote base branch while keeping the current working tree changes intact.

## Core Rules

1. Ask for the base branch first if the user has not explicitly provided one.
   - Ask exactly: `基础分支是什么？`
   - Do not run repo inspection or branch creation until the base branch is known.
2. Inspect the real repository state first. Never invent a branch topic.
3. Resolve the provided base branch before continuing.
   - Treat an unqualified base branch name such as `dev`, `main`, `master`, or `release/1.0` as a remote branch by default. Resolve it to the corresponding remote-tracking ref, for example `dev` -> `origin/dev`.
   - Use `origin` as the default remote when it exists. If `origin` is absent and exactly one remote exists, use that remote. If multiple non-`origin` remotes exist, ask which remote to use.
   - If the user provides a full remote-tracking ref such as `origin/dev` or `upstream/main`, use that exact remote-tracking ref.
   - Fetch the specific remote base before proposing or creating the branch, for example `git fetch origin dev`, then use `origin/dev`. Skip fetch only when the user explicitly asks to avoid it or the environment blocks it; report the skip or blocker.
   - Never silently fall back to a local branch with the same name. Use a local base only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/dev`.
   - If the remote base branch still cannot be resolved unambiguously, stop and ask for clarification.
4. Prefer repository-local naming conventions when visible from existing local or remote refs.
5. If no local convention is visible, default to Git Flow-compatible or common team prefixes:
   - `feature/` for new work, net-new capability, or no stronger signal
   - `bugfix/` for ordinary defect fixes
   - `hotfix/` only for urgent production fixes explicitly indicated by the user
   - `release/` for versioning, release preparation, or stabilization
   - `chore/` for tooling, dependency, maintenance, or housekeeping changes
   - `docs/` for documentation-only changes
   - `refactor/` for behavior-preserving code restructuring
   - `test/` for test-only changes or test coverage work
   - `ci/` for CI pipeline, build workflow, or release automation changes
6. Give one strong recommendation. If the diff mixes unrelated topics, stop and ask the user to split the work or state the intended focus.
7. Unless the user already supplied an exact branch name and explicitly asked to execute immediately, propose the branch name first and wait for confirmation before switching.
8. Treat `docs/`, `test/`, `ci/`, and `refactor/` as narrow prefixes. Use them only when that concern is the dominant change, not just one part of a broader feature or bugfix.

## Workflow

1. If the base branch is not yet known, ask for it and stop. Do not continue to analysis or execution until the user answers.

2. Inspect the current branch, resolved base ref, current diff, and visible naming conventions.

```bash
git remote
git branch -r --list
git fetch <remote> <base-branch>
git rev-parse --verify <remote>/<base-branch>
git rev-parse --abbrev-ref HEAD
git branch --list
git branch --show-current
git status --short
git diff --staged --stat
git diff --stat
git branch --all --format='%(refname:short)'
```

For a full remote-tracking ref such as `origin/release/1.0`, parse the first path component as the remote and fetch the remaining branch name. For an unqualified branch with slashes such as `release/1.0`, do not treat `release` as a remote unless it is a configured git remote.

If the summary is not enough to infer the topic, inspect `git diff --staged` and `git diff`.

3. Infer the primary topic from evidence, in this order:
   - changed paths and filenames
   - added or removed symbols, config keys, API names, or error paths
   - repeated nouns or module names in the diff
   - the user's stated intent in the current request

Do not derive the topic from an imagined future commit message.

4. Choose the prefix using this decision order.
   - `hotfix/`: explicit production incident, online urgent fix, or release-blocking repair. This outranks every other prefix.
   - `release/`: version bump, packaging, release note preparation, cutover, or release hardening. Use it when the branch is primarily about shipping or stabilizing a release.
   - `docs/`: only when the diff is documentation-only. If docs accompany code changes, do not use `docs/`.
   - `ci/`: only when the diff is primarily CI pipeline, workflow YAML, build jobs, release automation, or check orchestration. If CI changes are only supporting a feature or fix, do not use `ci/`.
   - `test/`: only when the diff is primarily tests, fixtures, snapshots, test harnesses, or coverage work. If tests are added alongside product code, do not use `test/`.
   - `refactor/`: only when the diff preserves behavior and mainly restructures code, names, or module layout. If the refactor also introduces user-visible behavior changes or bug fixes, do not use `refactor/`.
   - `bugfix/`: ordinary defect fix with no production urgency.
   - `chore/`: tooling, dependency, maintenance, repository housekeeping, or low-risk support work that does not fit `docs/`, `ci/`, or `test/`.
   - `feature/`: net-new capability, API or schema extension, product behavior change, or the fallback when no narrower prefix is clearly dominant.

5. Apply the narrow-prefix purity rules.
   - Pick `docs/` only if changed files are docs, markdown, inline help text, or similar user/developer documentation and there is no product-code behavior change.
   - Pick `test/` only if changed files are tests or test-only support assets and production code is untouched or changed only to unblock test execution mechanically.
   - Pick `ci/` only if changes are limited to CI config, build scripts, release scripts, container/build pipeline wiring, or automation metadata.
   - Pick `refactor/` only if the intent is code shape cleanup with stable external behavior. Typical signals: extracted helpers, renamed internals, file moves, dead-code removal, or simplified control flow without contract changes.
   - If the diff includes both a narrow-prefix signal and meaningful feature or fix code, prefer `feature/`, `bugfix/`, or `hotfix/` based on user-visible intent.

6. Generate the slug.
   - Use 2-5 lowercase English words in kebab-case
   - Prefer `<domain>-<action>` or `<module>-<problem>`
   - Remove vague words such as `update`, `change`, `misc`, `stuff`
   - Keep only ASCII letters, digits, and `-`
   - Keep it under 40 characters when practical

7. Validate the proposal.
   - The branch name must describe the dominant topic, not every touched file
   - The base branch must be resolved before proposing a branch name
   - The base branch must resolve to a remote-tracking ref unless the user explicitly asked for a local ref
   - Unqualified base names must not resolve to local refs; `dev` means the resolved remote-tracking ref such as `origin/dev`
   - If the working tree is clean, say there is no diff-based topic to infer unless the user provides one
   - If the diff spans unrelated modules or concerns, say the change set is too mixed for reliable auto-naming
   - If the proposed branch already exists, add a short disambiguator only after checking refs
   - If the repo's existing branch prefixes conflict with the default proposal, follow the repo convention and say so explicitly
   - If `docs/`, `test/`, `ci/`, or `refactor/` was selected, explain briefly why the diff is pure enough to justify that narrow prefix

8. Execute after confirmation.

Prefer:

```bash
git switch --no-track -c <branch-name> <base-ref>
```

Fallback for older Git:

```bash
git checkout --no-track -b <branch-name> <base-ref>
```

Then, if `origin/<branch-name>` already exists, set upstream explicitly:

```bash
git branch --set-upstream-to=origin/<branch-name> <branch-name>
```

If the same-name remote branch does not exist yet, do not set upstream during checkout.

9. Verify and report.

```bash
git branch --show-current
git status --short
```

If `origin/<branch-name>` did not exist at checkout time, tell the user the first publish should be `git push -u origin <branch-name>`. This creates the remote branch and sets upstream in one step. Do not inherit the base branch as upstream.

Report the original branch, the resolved base ref, the new branch, the prefix rationale, and the evidence used to infer the slug.

## Output Shape

Before execution, reply in this shape:

```text
基础分支：<provided-base-branch>
解析后的基础分支：<resolved-base-ref>
基线说明：remote-tracking；fetch: <executed|skipped|blocked>
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

- base branch is missing or unresolved
- working tree is clean
- diff topic is mixed
- existing repo naming convention conflicts with the default proposal
- branch already exists and needs a different name

## Safety Notes

- Do not auto-commit, auto-stash, or auto-reset changes.
- Do not change the base branch implicitly.
- Do not set upstream to the base branch. Only set upstream to `origin/<branch-name>` when that exact remote branch already exists.
- Do not treat an out-of-date local branch as the authoritative base when a remote-tracking ref is available.
- Do not use a same-name local branch as fallback for an unresolved remote base branch.
- Do not claim the result follows "Git Flow" if the repository clearly uses another naming scheme.
- Do not choose `docs/`, `test/`, `ci/`, or `refactor/` just because those files appear in the diff; they must be the dominant intent of the branch.
- If only part of the current changes should move to the new branch, say that a plain branch switch is insufficient and the user likely needs selective staging, `git stash --keep-index`, or a separate commit workflow.

## Examples

- auth token refresh endpoint -> `feature/auth-refresh-token`
- nil pagination guard -> `bugfix/pagination-nil-guard`
- urgent payment callback repair -> `hotfix/payment-callback-timeout`
- cut `1.8.0` release prep -> `release/1-8-0`
- docs cleanup for skill text -> `docs/skill-branch-rules`
- code reshaping without behavior change -> `refactor/branch-rule-cleanup`
- add branch naming tests -> `test/branch-name-selection`
- update CI workflow for release validation -> `ci/release-validation-workflow`
- feature plus docs update -> `feature/<topic>`, not `docs/<topic>`
- bug fix plus regression test -> `bugfix/<topic>`, not `test/<topic>`
- refactor plus behavior fix -> `bugfix/<topic>` or `feature/<topic>`, not `refactor/<topic>`
