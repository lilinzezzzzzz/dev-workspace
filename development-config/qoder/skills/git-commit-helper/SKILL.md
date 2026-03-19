---
name: git-commit-helper
description: 生成符合 Conventional Commits 规范的提交信息。当用户请求提交代码、写 commit message、或查看 staged changes 时使用此技能。
---

# Git Commit Helper

## 提交前检查

1. 确认当前分支命名符合规范
2. 检查 staged changes
3. 生成符合规范的提交信息

## 分支命名规范

| 类型 | 格式 | 示例 |
| --- | --- | --- |
| 新功能 | `feature/<name>` | `feature/user-auth` |
| Bug修复 | `bugfix/<name>` | `bugfix/login-error` |
| 紧急修复 | `hotfix/<name>` | `hotfix/security-patch` |
| 发布 | `release/<version>` | `release/v1.2.0` |

## 提交格式

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| `feat` | 新功能 | `feat(auth): 添加 JWT 认证` |
| `fix` | Bug 修复 | `fix(api): 修复参数验证错误` |
| `docs` | 文档更新 | `docs: 更新 README` |
| `style` | 代码格式（不影响逻辑） | `style: 格式化代码` |
| `refactor` | 重构（非新功能、非修复） | `refactor(utils): 优化工具函数` |
| `perf` | 性能优化 | `perf(db): 优化查询性能` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具/依赖 | `chore: 更新依赖版本` |
| `ci` | CI/CD 相关 | `ci: 添加 GitHub Actions` |
| `revert` | 回滚提交 | `revert: 回滚 xxx 提交` |

### Scope 范围（可选）

表示影响范围，如：`auth`、`api`、`ui`、`db`、`config`

### Subject 主题

- 祈使语气（如「添加」非「添加了」）
- 使用中文，技术名词使用英文
- 不以句号结尾

### Body 正文（可选）

- 简洁描述**改了什么**，不解释原因，不过度展开

### Footer 页脚（可选）

- Breaking changes: `BREAKING CHANGE: xxx`
- 关闭 Issue: `Closes #123`

## 示例

**简单提交：**

```text
feat(auth): 添加用户登录功能
```

**带正文：**

```text
fix(api): 修复请求超时处理

添加重试机制，最多重试 3 次
修复连接池泄漏问题
```

**Breaking Change：**

```text
feat(api): 重构 API 响应格式

BREAKING CHANGE: 响应格式从 {code, data} 改为 {status, result}
```

## 工作流程

1. 运行 `git status` 查看当前状态
2. 运行 `git diff --staged` 查看暂存的更改
3. 分析更改内容，确定 type 和 scope
4. 生成符合规范的提交信息，**等待用户 review 确认**
5. 用户确认后，执行 `git commit -m "..."`
6. **不要**自动 push，除非用户明确要求

## 重要原则

- **不要重写用户更改**：除非用户明确要求
- **避免无关清理**：不要在同一次提交中做无关的代码清理，除非是为了解决阻塞问题
- **一次提交一个关注点**：保持提交的原子性
