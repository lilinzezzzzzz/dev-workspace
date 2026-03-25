# Commit Message Template

Use this as the default output shape. Keep it compact unless the change genuinely needs more structure.

## Draft Only

Use when the user asked for a message but not for an actual commit.

```text
建议的 commit message:

<type>(<scope>): <subject>
```

If `scope` is unnecessary, omit it:

```text
建议的 commit message:

<type>: <subject>
```

## Draft With Body

Use when the staged diff contains a small set of tightly related subchanges.
Format the body as a bulleted list using `- ` prefixes.

```text
建议的 commit message:

<type>(<scope>): <subject>

- <body bullet 1>
- <body bullet 2>
```

## Draft With Breaking Change

```text
建议的 commit message:

<type>(<scope>): <subject>

BREAKING CHANGE: <what changed for callers>
```

## Commit Executed

Use when the user explicitly asked to commit and the staged scope is coherent.

```text
已执行提交，commit message:

<type>(<scope>): <subject>
```

If you had to make an assumption, add one short line after the message:

```text
假设：本次 staged changes 以 <module/behavior> 为单一关注点。
```

## Blocked Cases

### Nothing staged

```text
当前没有 staged changes，无法基于已暂存内容生成可靠的 commit message。
```

### Mixed concerns

```text
当前 staged changes 包含多个无关关注点，不建议强行生成单一 commit message。
建议先拆分或重新 stage，再提交。
```

## Example Messages

```text
feat(auth): 添加 JWT 刷新令牌接口
fix(api): 修复分页参数为空时的 500 错误
refactor(vector): 拆分 embedding client 初始化逻辑
perf(db): 减少知识库列表接口的 N+1 查询
test(chunk): 补充分块任务失败重试场景覆盖
chore: 更新开发环境 pre-commit 配置
```
