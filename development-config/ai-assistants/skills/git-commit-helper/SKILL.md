---
name: git-commit-helper
description: 基于 staged changes、指定 diff 或明确的提交范围，生成符合 Conventional Commits 规范的 commit message，并在用户明确要求提交代码时执行安全的提交流程。当用户要求写 commit message、总结 staged changes、帮忙提交代码、判断 type 或 scope、拆分提交边界时使用此 skill。
---

# Git Commit Helper

Use this skill to derive a commit message from the actual change set. Prefer one atomic commit, one clear subject, and no hidden assumptions.

## Core Rules

1. Inspect the real change set before proposing or creating a commit.
2. Base the message on staged content first. Do not infer from unstaged changes unless the user explicitly asks.
3. Keep one commit to one concern. If the staged diff mixes unrelated changes, call it out before committing.
4. Prefer a short, imperative subject.
5. Do not auto-push.
6. If the user asked for a message only, draft the message only. If the user asked to commit, commit only after the staged scope is clear enough to justify a single message.
7. When the user provides a base branch or base ref for context, load and follow [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md). Default to the latest remote base for non-local branch names.

## Language Policy (IMPORTANT)

**Commit message 的 subject 和 body 默认使用中文。** 仅在以下情况保留英文：

- Conventional Commits 的 `type` 和 `scope` 必须使用英文（如 `feat`, `fix`, `auth`, `api`）
- 专有技术术语保持英文形式更清晰时（如 `JWT`, `API`, `WebSocket`, `CI/CD`, `Milvus`）
- 代码标识符、函数名、变量名等直接引用代码的内容

**示例：**

- `feat(auth): 添加 JWT 刷新令牌接口` ✓
- `fix(api): 修复分页参数为空时的 500 错误` ✓
- `feat(auth): add JWT refresh token endpoint` ✗ 应使用中文

## Workflow

1. Determine the user's intent.
   - `写 commit message` or `生成提交信息`: inspect the change set and draft the message only.
   - `看 staged changes`: summarize the staged diff and propose one strong message.
   - `提交代码`: inspect staged changes, generate the message, and commit if the staged scope is coherent.

2. Gather evidence from git.
   - Prefer `git status --short`, `git diff --staged --stat`, and `git diff --staged`.
   - If nothing is staged, say so clearly.
   - If the user asks for a commit but only unstaged changes exist, stop and explain the gap.
   - If the user provides a base branch or base ref for context, resolve freshness and reporting through the shared remote-base rule before using it.

3. Classify the change.
   - Load [references/commit-type-selection.md](./references/commit-type-selection.md).
   - Determine `type`, optional `scope`, `subject`, optional `body`, and optional `footer`.
   - Use the smallest accurate scope. Omit `scope` when it adds noise rather than clarity.

4. Check commit quality.
   - Ensure the staged diff represents one concern.
   - Check whether the change is breaking, revert-like, dependency-only, test-only, docs-only, or mixed.
   - If the change is ambiguous, present one recommended message and explain the assumption briefly.

5. Produce the result in a stable shape.
   - Use [references/commit-message-template.md](./references/commit-message-template.md) as the default output shape.
   - When committing, show the exact message used.
   - When a base ref was used for context, state the exact base ref, whether it was remote-tracking or local, whether fetch was executed, and the fetched base commit SHA when fetch succeeded.
   - If you did not commit, say whether the result is a draft, a recommendation, or blocked by staging ambiguity.

## Safety Guidance

- Do not commit unrelated staged changes just because they are present.
- Do not rewrite history unless the user explicitly asks.
- If a breaking change is visible in the diff, surface it explicitly with a `BREAKING CHANGE:` footer.
- If the repository has local commit policy such as branch naming or language preference, follow it when known, but do not invent rules that are not present.

## References

- Read [references/commit-type-selection.md](./references/commit-type-selection.md) for `type`, `scope`, and edge-case selection rules.
- Read [references/commit-message-template.md](./references/commit-message-template.md) for the default output format and examples.
