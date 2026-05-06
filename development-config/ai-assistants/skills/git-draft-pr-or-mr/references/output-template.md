# PR/MR Output Template

Use this template as the default output shape when drafting a PR or MR.

## Default

```markdown
基于 `<base-ref>` 生成。

基线说明：`<remote-tracking|local>`；fetch: `<executed|not-needed|degraded>`；base commit: `<sha|not-needed>`

标题：
<title>

描述：
## 主要改动

- <概括核心改动 1>
- <概括核心改动 2>
- <概括核心改动 3>

## 技术说明

- <仅保留 reviewer 需要知道的技术细节、兼容性约束或实现取舍；无则可省略该节>
```

## Short

Use this version when the user asks for a shorter description.

```markdown
基于 `<base-ref>` 生成。

基线说明：`<remote-tracking|local>`；fetch: `<executed|not-needed|degraded>`；base commit: `<sha|not-needed>`

标题：
<title>

描述：
- <改动点 1>
- <改动点 2>
- <改动点 3>
```

## Title Guidance

- Prefer one line.
- Use Chinese by default.
- Keep technical identifiers such as `AgentBuild`, `NodeConfig`, `origin/main`, `<remote>/<branch>`, or `tenant RPC` when they carry meaning.
- Prefer Conventional Commits-style PR titles by default, using `<type>(<scope>): <subject>` when scope adds real signal.
- Prefer business outcome or scenario change over implementation detail, for example “支持某流程”“修复某场景问题”“优化某链路体验”.
- Avoid implementation-only titles such as “重构 XXX”“调整逻辑”“修改字段映射” unless the technical change itself is the business-relevant point.
- If the target repo clearly uses a different PR title convention, follow that convention instead of forcing Conventional Commits.

## Base Ref Guidance

- Always include the exact base ref near the top.
- Use [../../_shared/git-remote-base-resolution.md](../../_shared/git-remote-base-resolution.md) for resolution, freshness, downgrade, and reporting rules.
