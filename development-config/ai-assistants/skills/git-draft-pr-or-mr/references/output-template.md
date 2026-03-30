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

<1-2 句说明业务场景、问题背景或目标>

## 业务价值

- <对用户、运营、交付效率或稳定性的直接价值>
- <风险收敛、成本下降或流程改善等收益>

## 主要改动

- <用业务语言概括改动点 1，必要时补充关键技术手段>
- <用业务语言概括改动点 2，必要时补充关键技术手段>
- <用业务语言概括改动点 3，必要时补充关键技术手段>

## 风险与影响

- <影响范围、兼容性、发布注意事项；无则写“无明显兼容性风险”>

## 验证

- <已执行的测试、检查或人工验证>
```

## Short

Use this version when the user asks for a shorter description.

```markdown
基于 `<base-ref>` 生成。

基线说明：`<remote-tracking|local>`；fetch: `<executed|skipped|not-needed>`

标题：
<title>

描述：
## 背景

<业务问题或目标>

## 改动摘要

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
- Prefer business outcome or scenario change over implementation detail, for example “支持某流程”“修复某场景问题”“优化某链路体验”.
- Avoid implementation-only titles such as “重构 XXX”“调整逻辑”“修改字段映射” unless the technical change itself is the business-relevant point.
- If the repo clearly uses Conventional Commits-style PR titles, prefer `<type>(<scope>): <subject>`.

## Base Ref Guidance

- Always include the exact base ref near the top.
- State whether the base ref was a remote-tracking ref or an explicit local ref.
- If fetch was skipped or not needed, say so explicitly when that affects freshness expectations.
