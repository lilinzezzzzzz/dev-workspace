# PR/MR Output Template

Use this template as the default output shape when drafting a PR or MR.

## Default

```markdown
基于 `<base-ref>` 生成。

基线说明：`<remote-tracking|local>`；fetch: `<executed|skipped|not-needed>`

标题：
<title>

描述：
## 背景

<1-2 句说明问题背景或业务动机>

## 主要改动

- <改动点 1>
- <改动点 2>
- <改动点 3>

## 验证

- <已执行的测试、检查或人工验证>
```

## Short Business-Facing

Use this version when the user asks for a shorter description or a more business-facing summary.

```markdown
基于 `<base-ref>` 生成。

基线说明：`<remote-tracking|local>`；fetch: `<executed|skipped|not-needed>`

标题：
<title>

描述：
## 背景

<业务问题或目标>

## 业务改动

- <改动点 1>
- <改动点 2>
- <改动点 3>

## 结果

- <最终收益、风险收敛或行为变化>
```

## Title Guidance

- Prefer one line.
- Use Chinese by default.
- Keep technical identifiers such as `AgentBuild`, `NodeConfig`, `origin/main`, `<remote>/<branch>`, or `tenant RPC` when they carry meaning.
- If the repo clearly uses Conventional Commits-style PR titles, prefer `<type>(<scope>): <subject>`.

## Base Ref Guidance

- Always include the exact base ref near the top.
- State whether the base ref was a remote-tracking ref or an explicit local ref.
- If fetch was skipped or not needed, say so explicitly when that affects freshness expectations.
