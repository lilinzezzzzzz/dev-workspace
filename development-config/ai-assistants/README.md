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
│   ├── code-review/
│   ├── find-skills/
│   ├── gen-agents-md/
│   └── git-commit-helper/
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
- **git-commit-helper**: 生成符合个人规范的 Git 提交信息
- **code-review**: 代码审查规范
- **find-skills**: 发现并安装外部 skills
- **gen-agents-md**: 生成或更新项目级 `AGENTS.md`

### 扩展模块（预留）

- **agents/**: 个人 Agent 行为定制
- **events/**: 个人工作流事件处理
- **skills/**: 个人专业技能模块

---

## 🚀 快速开始

### 1. 应用个人配置

执行统一同步脚本后，按提示选择要同步的内容类型，再选择目标 assistant：

```bash
./development-config/ai-assistants/sync-agents.sh
```

**脚本功能说明**:

- **内容选择**: 支持 `AGENTS.md`、`agents/`、`skills/`
- **skills 流程**: 先选择具体 skill，再选择目标 assistant
- **目标选择**: 支持 `codex` 或 `qoder`
- **覆盖策略**: `AGENTS.md` 直接覆盖；`agents/` 和 `skills/` 仅覆盖同名项
- **完整性校验**: 文件使用 `sha256sum`，目录使用 `diff -qr`
- **依赖要求**: 需要系统安装 `sha256sum` 和 `diff`

### 2. 典型用法

- 选择 `AGENTS.md`：同步个人规则文件到目标 assistant 根目录
- 选择 `agents`：同步仓库中的 agent 配置目录到目标 assistant 的 `agents/`
- 选择 `skills`：选择一个 skill 并同步到目标 assistant 的 `skills/`

### 3. 个性化定制

根据个人喜好和技术栈，在预留目录中添加：

- 个人偏好的 Agent 行为规则
- 符合个人工作流的事件处理
- 专业领域的个人技能模块

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
