---
name: draft-pr-mr
description: 基于明确指定的基础分支或基础 ref 生成 PR/MR 标题和描述。用于用户要求“写 PR 标题”“生成 MR 描述”“基于 dev、main、master、origin/main 或其他 base branch 总结当前分支改动”“整理可直接粘贴到 GitHub/GitLab 的合并说明”等场景。默认将未限定的基础分支名解析为对应的 remote-tracking ref，而不是本地分支。只有在基础分支已指定或可被用户明确确认时使用；若未指定基础分支，先询问，不要自行猜测。
---

# Draft PR MR

Use this skill to draft a PR or MR title and description from the actual git diff between an explicit base ref and `HEAD`.

## Core Rules

1. Require an explicit base branch or base ref. If the user does not specify one, ask first instead of inferring.
2. Distinguish local refs from remote-tracking refs. `main` and `origin/main` are not equivalent.
3. Resolve an unqualified base branch name such as `dev`, `main`, or `master` to the corresponding remote-tracking ref such as `<remote>/<branch>` by default. Do not silently fall back to the local branch.
4. If the user explicitly asks for local branch state, or provides a full local ref such as `refs/heads/main`, use that exact local ref.
5. If the skill is using the default remote-tracking base and latest remote state matters, sync that ref first, for example `git fetch origin main`, then draft against `origin/main`.
6. Base the title and description on the real change set. Use commit messages only as secondary evidence.
7. State the exact base ref used whenever it matters, especially when the user names a branch such as `dev`, `main`, or `master` without clarifying whether they mean local or remote-tracking.
8. Produce one strong recommendation, not multiple equally vague options, unless the user explicitly asks for alternatives.

## Workflow

1. Resolve the base ref.
   - If the user gives a full ref such as `origin/main`, use it directly.
   - If the user gives an unqualified branch name such as `dev`, `main`, or `master`, resolve it to the corresponding remote-tracking ref `<remote>/<branch>` by default.
   - If the user explicitly asks for local branch state, or provides a full local ref such as `refs/heads/main`, use that exact local ref.
   - If the request says "latest" or "最新", or the skill is using the default remote-tracking behavior, fetch the remote-tracking ref first unless the environment is offline or the user asks not to fetch.
   - If the base is missing, stop and ask for it.

2. Inspect the real change set.
   - Prefer `git log --oneline <base>..HEAD` for commit context.
   - Prefer `git diff --stat <base>...HEAD` for size and hotspot context.
   - Prefer `git diff <base>...HEAD` for behavioral changes.
   - Read changed files only as needed to understand the dominant theme, business impact, and verification.

3. Identify the dominant story.
   - Summarize the primary user-facing or operator-facing outcome.
   - Call out important guardrails, compatibility constraints, or contract changes.
   - Separate core behavior changes from supporting tests or cleanup.

4. Draft the title.
   - Keep it short, concrete, and Chinese by default; keep technical terms in English when clearer.
   - Mirror repository conventions when obvious. If the repo clearly uses Conventional Commits-style PR titles, prefer that style.
   - Avoid vague titles such as “优化一些逻辑” or “修复问题”.

5. Draft the description.
   - Read [references/output-template.md](./references/output-template.md).
   - Use the default template unless the user asks for a shorter or more business-facing version.
   - Focus on why the change matters, what changed, and how it was verified.
   - Keep the description faithful to the diff. Do not promise behavior that is not evidenced.

## Output Rules

- Include the exact base ref used near the top when returning the draft.
- State whether the base ref was a remote-tracking ref or an explicit local ref, and whether fetch was executed or skipped when that affects freshness.
- If verification is visible in the repo or command output, include it; otherwise say it was not verified.
- If the branch includes unrelated commits or mixed concerns, say so and draft the description around the actual combined scope rather than pretending the change is narrower.
- If the user asks for “PR” or “MR”, treat the artifact shape as the same unless the target platform requires a specific term.

## References

- Read [references/output-template.md](./references/output-template.md) before drafting the final output.
