# Qoder 用户级配置

> 面向 Qoder 用户的个人开发环境配置和指令集

一套专为 Qoder AI 助手用户定制的个人级配置，包含编码规范、Git 工作流、Agent 指令等，旨在提升个人 AI 辅助开发的效率和代码质量。

---

## 📋 目录结构

```text
development-config/qoder/
├── AGENTS.md           # 核心 Agent 指令和开发规范
├── commands/           # 可执行命令配置
│   └── git-commit.md   # Git 提交信息生成命令
├── agents/             # Agent 配置文件（预留）
├── events/             # 事件处理配置（预留）
├── skills/             # 技能模块配置（预留）
└── README.md           # 本文档
```

---

## 🎯 核心组件

### AGENTS.md

用户的个人 Agent 指令和开发规范：

- **角色定位**: 个人开发者的技术偏好和习惯
- **技术栈**: 根据个人项目需求定制
- **编码标准**: 符合个人编码风格的最佳实践
- **Git 规范**: 个性化的提交信息规范

### Commands 命令集

个人定制的可执行命令，目前包含：

- **git-commit**: 生成符合个人规范的 Git 提交信息

### 扩展模块（预留）

- **agents/**: 个人 Agent 行为定制
- **events/**: 个人工作流事件处理
- **skills/**: 个人专业技能模块

---

## 🚀 快速开始

### 1. 应用个人配置

将 `AGENTS.md` 内容配置到 Qoder 的用户设置中，让 AI 助手适应您的个人开发习惯。

### 2. 配置个人命令

```bash
# 在 Qoder 中激活 git-commit 命令
# 使用方式：/git-commit
```

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
2. 在预留目录中建立项目模板
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
- [Qoder 官方文档](https://docs.qodo.ai/)

---

## 📄 许可证

本配置集采用 MIT 许可证，可根据需要自由修改和分发。

---

## 🤝 个人维护

建议 Fork 此配置作为个人开发环境的基础，根据自己的需求进行定制化改进！

**适用对象**: 独立开发者、技术爱好者
**核心价值**: 个人编码效率提升、AI 辅助开发体验优化
