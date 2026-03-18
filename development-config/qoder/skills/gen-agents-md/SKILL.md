---
name: gen-agents-md
description: 生成或更新项目根目录的 Qoder AGENTS.md 配置文件。当用户需要创建 AI 代理指令文档、配置编码规范、设置 Git 提交规范、定义响应偏好时使用此 skill。
metadata:
  allowed_tools: [Read, Write, Glob]
  tags: [agents, qoder, configuration, markdown, code-standards]
---

# Gen AGENTS.md

## When to use this skill
- 在新项目中创建 AGENTS.md 配置文件
- 更新现有 AGENTS.md 的编码标准
- 添加或修改 Git 提交规范
- 调整 AI 响应偏好设置

## Instructions

### Step 1: 检查现有文件

在项目根目录查找 AGENTS.md：
- 若存在：读取并分析现有内容，准备增量更新
- 若不存在：准备创建新文件

### Step 2: 收集必要信息

向用户确认以下内容（已有则跳过）：

**角色与上下文**
- 用户角色定位（如：后端工程师、全栈开发者）
- 技术栈（语言、框架、工具）

**编码标准**
- 代码风格要求
- 类型安全策略
- 异步编程偏好
- 日志规范
- API 设计规范
- 运行时环境（如 Python 用 uv，Go 用 Modules）

**Git 规范**
- 分支命名规则
- 提交消息格式
- 合并策略

**响应偏好**
- 语言偏好（中文/英文）
- 响应简洁程度
- 解决方案优先级

### Step 3: 生成/更新文件

**AGENTS.md 标准结构**：

```markdown
# Agent Instructions

## Role & Context
* **User Role:** [用户角色]
* **Tech Stack:** [技术栈列表]

## Coding Standards
### General
* **Quality:** [质量要求]
* **Architecture:** [架构要求]
* **Type Safety:** [类型安全要求]

### [Language Name] (如 Python/Golang)
* **Style:** [风格要求]
* **[其他类别]:** [具体要求]

## Git Commit Specification
* **Branch Naming:** [分支命名规则]
* **Commit Message Specification:** [提交消息格式]
* **Merge Strategy:** [合并策略]
* **Language Preference:** [语言偏好]

## Response Preferences
* **Conciseness:** [简洁性要求]
* **Solution-Oriented:** [解决方案导向]
* **Format:** [格式要求]

## Analysis & Verification Protocol
* **Challenge Assumptions:** [假设验证要求]
* **Identify Risks:** [风险识别要求]
* **Constructive Feedback Loop:** [反馈循环要求]

## Timeliness & Web Search
* **Web Search:** [网络搜索设置]
* **Information Freshness:** [信息时效性要求]
```

### Step 4: 写入文件

将生成的内容写入项目根目录的 AGENTS.md 文件。

## 验证清单
- [ ] 文件位于项目根目录
- [ ] Markdown 语法正确
- [ ] 所有必需部分已填写
- [ ] 编码标准具体明确
- [ ] Git 规范清晰可执行

## 示例

**输入**：用户是 Python 后端工程师，使用 FastAPI 和 SQLAlchemy

**输出**：

```markdown
# Agent Instructions

## Role & Context

* **User Role:** Senior Python Backend Development Engineer.
* **Tech Stack:**
  * Backend: FastAPI, SQLAlchemy, Pydantic
  * Database: PostgreSQL, Redis
  * Tools: uv, ruff, pylance

## Coding Standards

### Python

* **Style:**
  * Pythonic, Pydantic v2, PEP 8 compliant.
  * Ensure compatibility with ruff and pylance.
* **Database:**
  * Prefer SQLAlchemy ORM over raw SQL.
  * Use SQLAlchemy 2.0 style with type annotations.
* **API Design:**
  * Use FastAPI for REST APIs.
  * Prefer Pydantic V2 models for request/response schemas.
* **Runtime:**
  * Use uv for dependency management.

## Git Commit Specification

* **Format:** `<type>(<scope>): <subject>`
* **Types:** feat, fix, chore, docs, style, refactor, test, perf, ci

## Response Preferences

* **Conciseness:** Be direct and respond in Chinese.
* **Solution-Oriented:** Prioritize robustness over quick scripts.
```
