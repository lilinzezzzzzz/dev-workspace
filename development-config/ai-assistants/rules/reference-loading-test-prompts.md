# Reference Loading Test Prompts

> 用于在同步 rules 后，手动验证 `AGENTS.md` 是否能引导 AI 正确加载
> `references/*.md`。这些内容是测试提示词，不是运行时规则。

## 使用方式

1. 执行同步脚本，将 rules 同步到目标 assistant。
2. 开启一个全新的 AI 会话，避免旧上下文影响验证。
3. 复制下面的测试 prompt 到新会话。
4. 检查回答是否符合每个 prompt 下的预期结果。

同步到 Codex 后，默认优先 reference 路径应为：

```text
~/.codex/references/<file>.md
```

同步到 Qoder 项目后，默认优先 reference 路径应为：

```text
<project-root>/.qoder/rules/references/<file>.md
```

## 全量加载验证

用于验证一个复杂后端任务是否能触发所有高频 reference。

```text
这是规则加载验证任务，不要修改任何文件。
请根据 AGENTS.md 的 Task-Specific References 规则判断需要加载哪些
references，并用文件读取工具读取它们。

任务场景：我要修改一个 Python FastAPI 接口，涉及 SQLAlchemy 查询、
Alembic migration，并需要补 regression tests。

请回复：
1. 你实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
4. 如果有应该读取但没读取的文件，说明原因
```

预期至少读取：

```text
python.md
backend-reliability.md
codebase-discovery.md
database.md
execution-workflow.md
verification.md
```

预期一级标题：

```text
# Python Rules
# Backend Reliability And Security Rules
# Codebase Discovery Rules
# Database And Persistence Rules
# Execution Workflow Rules
# Verification Rules
```

## 执行流程与代码库发现验证

用于验证非平凡代码任务会触发执行流程和代码库上下文发现规则。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要在一个不熟悉的模块里做多文件行为变更，需要先梳理
调用链、相关测试、配置和影响面，并给出执行计划。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
codebase-discovery.md
execution-workflow.md
```

预期一级标题：

```text
# Codebase Discovery Rules
# Execution Workflow Rules
```

## Python 与测试验证

用于验证 Python 任务和测试任务的组合触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要重构一个 .py 文件，并补充 pytest regression tests。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
python.md
verification.md
```

## 数据库验证

用于验证数据库、ORM 和迁移规则触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要评审一个 SQLAlchemy 查询和 Alembic migration，
重点关注 N+1 查询、分页、锁表风险和回滚策略。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
database.md
```

如果 AI 同时读取 `python.md` 或 `verification.md`，只要理由与任务场景
匹配，也可以接受。

## 后端可靠性验证

用于验证 API、worker、重试、幂等和日志规则触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要修改一个 worker 的 retry、timeout、idempotency 和日志处理。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
backend-reliability.md
```

## 验证策略验证

用于验证测试、CI、lint、type-check 相关规则触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要分析 CI 失败，并选择最小的测试、lint 和 type-check 命令。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
verification.md
```

## Git 工作流验证

用于验证 Git 分支、提交和历史敏感操作规则触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要基于当前 staged changes 生成一次 commit，并确认分支命名、
revert/reset 安全边界和报告要求。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
git-workflow.md
```

预期一级标题：

```text
# Git Workflow Rules
```

## 项目级 AGENTS.md 维护验证

用于验证项目级或子目录 `AGENTS.md` 维护规则触发。

```text
不要修改文件。
请按当前 AGENTS.md 执行必要的上下文加载。

任务场景：我要把当前项目中发现的稳定测试命令和子目录约束写入
项目级 AGENTS.md，并判断应该放在仓库根目录还是子目录 AGENTS.md。

请回复：
1. 实际读取了哪些 references 文件
2. 每个文件的实际读取路径
3. 每个文件的一级标题
```

预期至少读取：

```text
project-agents-maintenance.md
```

预期一级标题：

```text
# Project AGENTS.md Maintenance Rules
```

允许额外读取：

```text
codebase-discovery.md
execution-workflow.md
verification.md
```

说明：

- `codebase-discovery.md`：需要理解现有 `AGENTS.md` 层级和项目约定时可触发。
- `execution-workflow.md`：涉及多层级放置决策或需要明确计划时可触发。
- `verification.md`：任务场景提到稳定测试命令时可触发，但不是该用例的硬性要求。

## 判断标准

- AI 应明确说明实际读取了哪些 reference 文件。
- AI 应能报告真实读取路径，而不是只复述相对路径。
- AI 应能报告每个文件的一级标题。
- AI 报告的读取路径应符合当前 active assistant 的 reference 搜索顺序：
  Codex 优先 `~/.codex/references/<file>.md`，Qoder 优先
  `<project-root>/.qoder/rules/references/<file>.md`。
- 如果 reference 缺失，AI 应说明缺失路径或 blocker，并继续任务。
- 不接受只回答“我会遵循规则”但没有读取路径和标题的结果。
