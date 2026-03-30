# AI Assistant 用户级配置

> 面向 Codex、Qoder 及其他 IDE 内 AI assistant 的通用个人配置和指令集

一套可复用的个人级 AI assistant 配置，包含编码规范、Git 工作流、AGENTS 指令与 skills，同一份内容可以同时服务于 Codex、Qoder 以及其他支持类似机制的开发工具。

---

## 📋 目录结构

```text
development-config/ai-assistants/
├── AGENTS.md                 # 通用 AGENTS 指令和开发规范
├── sync-agents.sh            # 统一同步入口：AGENTS.md / agents / skills
├── agents/                   # Agent 配置文件（预留）
├── events/                   # 事件处理配置（预留）
├── skills/
│   ├── api-endpoint-analyzer/
│   ├── git-code-reviewer/
│   ├── git-commit-helper/
│   ├── git-draft-pr-or-mr/
│   └── git-restack-from-base/
└── README.md
```

---

## 🎯 核心组件

### AGENTS.md

用户的通用 AGENTS 指令和开发规范：

- **适用范围**: Codex、Qoder 和其他支持类似规则注入的工具
- **角色定位**: 个人开发者的技术偏好和习惯
- **技术栈**: 根据个人项目需求定制
- **编码标准**: 符合个人编码风格的最佳实践
- **Git 规范**: 个性化的提交信息规范

### Skills 与同步脚本

当前目录已经包含一组可复用能力：

- **sync-agents.sh**: 统一同步入口，可交互选择 `AGENTS.md`、`agents/` 或单个 `skill`
- **api-endpoint-analyzer**: 系统化分析 API endpoint 的请求、响应、业务流程与错误处理
- **git-code-reviewer**: 基于 diff 输出高信号代码审查结论，优先发现 bug、回归和风险
- **git-commit-helper**: 基于 staged diff 生成或执行规范的 Conventional Commit
- **git-draft-pr-or-mr**: 基于明确 base ref 和真实 git diff 生成精简的 PR/MR 标题与描述
- **git-restack-from-base**: 基于显式基础分支重新切出版本化分支，并按原顺序 cherry-pick 当前分支独有提交

### 扩展模块（预留）

- **agents/**: 个人 Agent 行为定制
- **events/**: 个人工作流事件处理
- **skills/**: 个人专业技能模块

### Skill 目录约定

当前 `skills/` 目录采用统一结构，便于同步、复用和持续演进：

```text
skills/<skill-name>/
├── SKILL.md                  # 触发描述、核心工作流、边界规则
├── agents/
│   └── openai.yaml           # UI 展示名、短描述、默认 prompt
├── references/               # 按需加载的模板、检查清单、选择规则
└── scripts/                  # 可选，本地辅助脚本或命令封装
```

设计原则：

- `SKILL.md` 保持精简，只放高价值流程和决策规则
- 细节模板、checklist、示例下沉到 `references/`
- `agents/openai.yaml` 负责展示层和默认触发入口
- `scripts/` 只放 skill 专属、值得复用的执行逻辑，避免把复杂 shell 直接塞进说明文档
- skill 命名与目录名保持一致，避免同步或调用时混淆
- `sync-agents.sh` 会自动发现包含 `SKILL.md` 的一级 skill 目录，无需手动维护 skill 列表

---

## 🚀 快速开始

### 1. 应用个人配置

执行统一同步脚本后，按提示选择要同步的内容类型，再选择目标 assistant：

```bash
./development-config/ai-assistants/sync-agents.sh
```

**脚本功能说明**:

- **内容选择**: 支持 `AGENTS.md`、`agents/`、`skills/`
- **skills 流程**: 先选择具体 skill 或全部 skills，再选择目标 assistant
- **目标选择**: 支持 `codex`、`qoder` 或 `both`
- **覆盖策略**: `AGENTS.md` 直接覆盖；`agents/` 和 `skills/` 仅覆盖同名项
- **完整性校验**: 文件使用 SHA-256 校验，目录使用 `diff -qr`
- **依赖要求**: 需要系统安装 `diff`，文件校验会优先使用 `sha256sum`，并兼容 `shasum` 或 `openssl`

### 2. 典型用法

- 选择 `AGENTS.md`：同步个人规则文件到目标 assistant 根目录
- 选择 `agents`：同步仓库中的 agent 配置目录到目标 assistant 的 `agents/`
- 选择 `skills`：选择一个 skill 或全部 skills，并同步到目标 assistant 的 `skills/`
- 选择 `both`：将选中的内容同步到当前配置的所有目标目录

当前已维护的 skill 更适合以下场景：

- `api-endpoint-analyzer`：解释接口契约、梳理调用链、核对实现与文档是否一致
- `git-code-reviewer`：审查 PR、MR、commit 或 diff，输出带 severity 的具体 findings
- `git-commit-helper`：根据 staged changes 生成 commit message，或在范围清晰时执行提交
- `git-draft-pr-or-mr`：基于显式 base branch 或 base ref，生成可直接粘贴到 GitHub/GitLab 的 PR/MR 文案
- `git-restack-from-base`：把当前功能分支基于新 base 重建为 `-v2`、`-v3` 等版本化分支，并在确认后执行 cherry-pick

### 3. 个性化定制

根据个人喜好和技术栈，在预留目录中添加：

- 个人偏好的 Agent 行为规则
- 符合个人工作流的事件处理
- 专业领域的个人技能模块
- 遵循 `SKILL.md + agents/openai.yaml + optional references/ + optional scripts/` 的 skill 结构

---

## 📋 开发规范摘要

### 编程语言规范

**Python 开发**:

- 遵循 PEP 8 和 Pydantic v2 规范
- 使用 uv 进行依赖管理
- 优先使用 SQLAlchemy ORM
- 异步编程使用 anyio + httpx

**Golang 开发**:

- 遵循 Effective Go 指南
- 使用标准库，最小化第三方依赖
- 显式错误处理和上下文传递
- 惯用的并发模式

### Git 工作流

**分支命名**:

- `feature/<description>`
- `bugfix/<description>`
- `hotfix/<description>`
- `release/<version>`

**提交信息格式**:

```
<type>(<scope>): <subject>

[optional body]
```

**提交类型**:

- `feat`: 新功能
- `fix`: 修复 bug
- `chore`: 构建过程或辅助工具变动
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构代码
- `test`: 测试相关
- `perf`: 性能优化
- `ci`: CI/CD 配置变更

---

## 🛠️ 使用建议

### 个人优化

1. 根据个人编码习惯调整规范细节
2. 定期回顾和优化个人工作流
3. 持续完善个人技能库

### 项目适配

1. 针对不同项目类型调整配置重点
2. 在 `skills/` 或预留目录中建立项目模板
3. 积累个人最佳实践案例

### 持续进化

1. 跟踪个人技术成长轨迹
2. 学习并整合新的开发方法
3. 定期重构个人配置体系

---

## 📚 相关资源

- [Conventional Commits 规范](https://www.conventionalcommits.org/)
- [Python 官方文档](https://docs.python.org/)
- [Go 编程语言规范](https://golang.org/doc/effective_go)
- 对应 assistant 或 IDE 的官方文档

---

## 📄 许可证

本配置集采用 MIT 许可证，可根据需要自由修改和分发。

---

## 🤝 个人维护

建议 Fork 此配置作为个人开发环境的基础，根据自己的需求进行定制化改进！

**适用对象**: 独立开发者、技术爱好者
**核心价值**: 个人编码效率提升、AI 辅助开发体验优化
