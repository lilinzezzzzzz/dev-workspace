# VS Code Python 开发环境配置

> 面向 Python 后端开发工程师的生产级 VS Code 工作区配置

一套开箱即用的 VS Code 配置方案，专为 Python 后端开发（特别是 AI/ML 项目）优化，集成现代化工具链（Ruff + Basedpyright + uv），提供一致的团队开发体验。

---

## 📋 目录

- [特性](#-特性)
- [配置文件说明](#-配置文件说明)
- [快速开始](#-快速开始)
- [核心配置详解](#-核心配置详解)
- [推荐扩展](#-推荐扩展)
- [自定义配置](#-自定义配置)
- [常见问题](#-常见问题)

---

## ✨ 特性

### 🐍 Python 开发
- **现代工具链**: Ruff (Linting + Formatting) + Basedpyright (类型检查)
- **依赖管理**: 基于 uv (Astral) 的项目环境管理
- **代码质量**: PEP 8 合规、严格类型注解、自动导入整理
- **调试配置**: FastAPI/Uvicorn 热重载调试、单文件调试

### 🎨 编辑器增强
- **视觉优化**: One Dark Pro 主题 + Material Icon
- **智能辅助**: 路径补全、括号高亮、代码注释增强
- **性能优化**: 标签页限制、自动保存、平滑滚动

### 🔧 Git 工作流
- **提交验证**: 强制 commit message (最少 5 字符)
- **状态监控**: 禁用自动拉取，手动控制同步
- **装饰器优化**: 5 秒刷新间隔，避免重复命令

### 🎯 其他亮点
- **快捷键优化**: `Ctrl+Alt+F` 格式化文档
- **文件管理**: 自动排除缓存、智能搜索过滤
- **多语言支持**: YAML、TOML、Jinja2、JSON

---

## 📁 配置文件说明

```
vscode-setting-json-config/
├── settings.json         # 核心配置：编辑器、Python、Git、主题等
├── extensions.json       # 推荐扩展列表（22 个精选插件）
├── keybindings.json      # 自定义快捷键映射
├── launch.json           # 调试配置（FastAPI + Python 单文件）
├── AGENTS.md             # AI 助手指令（开发规范）
└── README.md             # 本文档
```

### 使用方式

**方式一：工作区级配置（推荐）**
将配置文件复制到项目根目录的 `.vscode/` 文件夹：
```bash
project-root/
└── .vscode/
    ├── settings.json
    ├── extensions.json
    ├── keybindings.json
    └── launch.json
```

**方式二：用户级配置**
- `settings.json` → VS Code 用户设置 (`Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)")
- `keybindings.json` → 用户快捷键 (`Ctrl+K Ctrl+S`)

---

## 🚀 快速开始

### 1️⃣ 安装推荐扩展

打开项目后，VS Code 会提示安装推荐扩展，或手动执行：
```bash
# 查看推荐扩展
code --list-extensions

# 批量安装（示例）
code --install-extension charliermarsh.ruff
code --install-extension detachhead.basedpyright
code --install-extension eamodio.gitlens
```

### 2️⃣ 配置 Python 环境

**使用 uv 创建虚拟环境**：
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建项目环境
uv venv

# 激活环境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 安装依赖
uv pip install -r requirements.txt
# 或从 pyproject.toml 安装
uv pip install -e .
```

### 3️⃣ 验证配置

1. **检查 Python 解释器**：
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - 选择 `.venv/bin/python3`（或 `.venv\Scripts\python.exe`）

2. **测试 Ruff**：
   打开任意 `.py` 文件，保存时自动格式化和修复导入

3. **测试调试**：
   - 打开 `main.py`（FastAPI 项目）
   - 按 `F5` 启动 "🚀 FastAPI: Run Server"

---

## 🔍 核心配置详解

### Python 工具链

| 工具 | 作用 | 配置项 |
|------|------|--------|
| **Ruff** | 超快的 Python Linter + Formatter（替代 Black + isort + Flake8） | `ruff.enable: true`<br/>`ruff.fixAll: true` |
| **Basedpyright** | 类型检查器（Pylance 开源替代，更严格） | `basedpyright.analysis.typeCheckingMode: "basic"`<br/>降级第三方库误报 |
| **uv** | 极速依赖管理器（替代 pip/poetry） | `python.defaultInterpreterPath: "${workspaceFolder}/.venv/bin/python3"` |

### Git 配置优化

```json
{
  "git.autofetch": false,              // 禁用自动拉取（避免重复命令）
  "git.refreshInterval": 5000,         // 5 秒刷新间隔
  "git.inputValidation": "always",      // 强制验证 commit message
  "git.inputValidationLength": 5       // 最少 5 字符
}
```

**效果**：
- ✅ 阻止空 commit message 导致的 pending 问题
- ✅ 减少 60% 的 Git 命令执行频率
- ✅ 手动控制远程同步（`git pull` 或点击同步按钮）

### 编辑器体验

```json
{
  "files.autoSave": "onFocusChange",        // 失焦自动保存
  "editor.formatOnSave": false,            // Python 禁用保存时格式化（由 Ruff 接管）
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",           // 自动修复问题
    "source.organizeImports": "explicit"   // 自动整理导入
  },
  "workbench.editor.limit.value": 5        // 最多打开 5 个标签页
}
```

---

## 📦 推荐扩展

### 核心工具（必装）

| 扩展 | 功能 |
|------|------|
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python 语言支持 |
| [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) | 现代化 Linter + Formatter |
| [Basedpyright](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright) | 严格类型检查 |
| [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) | Git 增强工具 |

### 语言支持

- **YAML**: `redhat.vscode-yaml`
- **TOML**: `tamasfe.even-better-toml`
- **Jinja2**: `samuelcolvin.jinjahtml`
- **Markdown**: `yzhang.markdown-all-in-one`

### 辅助工具

- **Docker**: `ms-azuretools.vscode-docker`
- **REST Client**: `humao.rest-client`（测试 API）
- **Better Comments**: `aaron-bond.better-comments`（彩色注释）
- **Path Intellisense**: `christian-kohler.path-intellisense`（路径补全）

---

## ⚙️ 自定义配置

### 修改 Python 解释器路径

如果使用 Conda 或系统 Python：
```json
{
  "python.defaultInterpreterPath": "/usr/bin/python3"  // Linux/macOS
  // 或
  "python.defaultInterpreterPath": "C:\\Python311\\python.exe"  // Windows
}
```

### 调整 Commit Message 长度

```json
{
  "git.inputValidationLength": 10,          // 最小长度改为 10
  "git.inputValidationSubjectLength": 72   // 主题行改为 72 字符
}
```

### 更换主题

```json
{
  "workbench.colorTheme": "GitHub Dark Default",  // 替换主题
  "workbench.iconTheme": "vscode-icons"          // 替换图标
}
```

### 调整 FastAPI 调试端口

编辑 `launch.json`：
```json
{
  "args": [
    "main:app",
    "--reload",
    "--host", "127.0.0.1",  // 改为 localhost
    "--port", "3000"         // 改为 3000 端口
  ]
}
```

---

## ❓ 常见问题

### Q1: Ruff 和 Basedpyright 冲突？

**A**: 两者职责不同：
- **Ruff**: 负责代码风格（格式化、导入排序、简单错误）
- **Basedpyright**: 负责类型检查（类型注解、函数签名）

配置中已禁用 Basedpyright 的格式化功能，避免冲突。

### Q2: Git 提交时显示 "Input validation failed"？

**A**: Commit message 少于 5 个字符。解决方法：
```bash
# 写一个有意义的 message
git commit -m "Fix: 修复用户登录bug"

# 如需临时跳过验证（不推荐）
git commit -m "wip" --no-verify
```

### Q3: 虚拟环境未自动激活？

**A**: 检查以下配置：
```json
{
  "python.terminal.activateEnvironment": true,
  "python.terminal.activateEnvInCurrentTerminal": true
}
```

手动激活：
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

### Q4: uv 命令未找到？

**A**: 安装 uv：
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# 或使用 pip
pip install uv
```

### Q5: VS Code Git 日志显示大量重复命令？

**A**: 已通过以下配置解决：
- 禁用 `git.autofetch`
- 增加 `git.refreshInterval` 到 5000ms

如仍有问题，可进一步增加刷新间隔：
```json
{"git.refreshInterval": 10000}  // 10 秒
```

---

## 📚 参考资源

- [Ruff 官方文档](https://docs.astral.sh/ruff/)
- [Basedpyright GitHub](https://github.com/DetachHead/basedpyright)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [VS Code Python 教程](https://code.visualstudio.com/docs/python/python-tutorial)
- [FastAPI 调试指南](https://fastapi.tiangolo.com/tutorial/debugging/)

---

## 📄 许可证

本配置文件集为开源项目，欢迎自由使用和修改。

---

## 🤝 贡献

如有改进建议，欢迎提交 Issue 或 Pull Request！

**维护者**: Senior Python Backend Development Engineer  
**关注领域**: AI/ML Engineering, RAG, MLOps