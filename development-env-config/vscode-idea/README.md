# VS Code 多语言开发环境配置

> 面向多语言开发者的生产级 VS Code 工作区配置

一套开箱即用的 VS Code 配置方案，支持 Python 和 Go 语言开发，采用模块化配置结构，提供一致的团队开发体验和最佳实践。

---

## 📋 目录

- [特性](#-特性)
- [目录结构](#-目录结构)
- [配置文件说明](#-配置文件说明)
- [快速开始](#-快速开始)
- [Python 开发配置](#-python-开发配置)
- [Go 开发配置](#-go-开发配置)
- [通用配置](#-通用配置)
- [推荐扩展](#-推荐扩展)
- [常见问题](#-常见问题)

---

## ✨ 特性

### 🐍 多语言支持
- **Python 开发**: Ruff + Basedpyright 工具链，uv 依赖管理
- **Go 开发**: Go 语言专用配置和调试支持
- **通用配置**: 编辑器核心设置、主题、快捷键等跨语言共享

### 🎨 编辑器增强
- **模块化设计**: 按语言分离配置，便于维护和扩展
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
- **多格式支持**: YAML、TOML、Jinja2、JSON、Markdown

---

## 🗂️ 目录结构

```
vscode-idea/
├── common/               # 通用配置（跨语言共享）
│   ├── settings.json     # 编辑器核心设置、主题、Git等
│   ├── extensions.json   # 推荐扩展列表
│   └── keybindings.json  # 自定义快捷键映射
├── python/               # Python 专用配置
│   ├── settings.json     # Python 工具链配置（Ruff、Basedpyright等）
│   └── launch.json       # Python 调试配置
├── golang/               # Go 专用配置
│   └── settings.json     # Go 语言配置
└── README.md             # 本文档
```

## 📁 配置文件说明

### 使用方式

**方式一：工作区级配置（推荐）**
将对应语言的配置文件复制到项目根目录的 `.vscode/` 文件夹：

Python 项目：
```bash
project-root/
└── .vscode/
    ├── settings.json     # 来自 common/
    ├── extensions.json   # 来自 common/
    ├── keybindings.json  # 来自 common/
    └── launch.json       # 来自 python/
```

Go 项目：
```bash
project-root/
└── .vscode/
    ├── settings.json     # 来自 common/ 和 golang/ 合并
    ├── extensions.json   # 来自 common/
    └── keybindings.json  # 来自 common/
```

**方式二：用户级配置**
- `common/settings.json` → VS Code 用户设置
- `common/keybindings.json` → 用户快捷键设置

---

## 🚀 快速开始

### 1️⃣ 安装推荐扩展

打开项目后，VS Code 会提示安装推荐扩展，或手动执行：
```bash
# 查看推荐扩展
code --list-extensions

# 批量安装核心扩展
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension detachhead.basedpyright
code --install-extension eamodio.gitlens

code --install-extension golang.go  # Go 项目需要
```

### 2️⃣ 配置开发环境

**Python 项目配置**：
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建项目环境
uv venv

# 激活环境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 安装依赖
uv pip install -r requirements.txt
```

**Go 项目配置**：
```bash
# 确保 Go 已安装
go version

# 初始化 Go 模块
go mod init your-project-name

# 安装依赖
go mod tidy
```

### 3️⃣ 应用配置文件

```bash
# 复制通用配置
cp -r development-env-config/vscode-idea/common/* .vscode/

# Python 项目额外复制
cp development-env-config/vscode-idea/python/* .vscode/

# Go 项目额外复制
cp development-env-config/vscode-idea/golang/settings.json .vscode/
```

### 4️⃣ 验证配置

1. **重启 VS Code** 使配置生效
2. **检查语言支持**：
   - Python: 打开 `.py` 文件应有语法高亮和智能提示
   - Go: 打开 `.go` 文件应有语法高亮和智能提示
3. **测试调试功能**：按 `F5` 启动调试

---

## 🐍 Python 开发配置

### 工具链配置

| 工具 | 作用 | 配置位置 |
|------|------|----------|
| **Ruff** | Python Linter + Formatter | `python/settings.json` |
| **Basedpyright** | 类型检查器 | `python/settings.json` |
| **uv** | 依赖管理器 | `python/settings.json` |
| **调试配置** | FastAPI/Uvicorn 调试 | `python/launch.json` |

### 核心设置
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python3",
  "ruff.enable": true,
  "ruff.fixAll": true,
  "basedpyright.analysis.typeCheckingMode": "basic"
}
```

## 🐹 Go 开发配置

### 工具链配置

| 工具 | 作用 | 配置位置 |
|------|------|----------|
| **Go 扩展** | Go 语言支持 | `golang/settings.json` |
| **调试配置** | Delve 调试器 | 集成在 `golang/settings.json` |
| **格式化** | gofmt/golines | `golang/settings.json` |

### 核心设置
```json
{
  "go.useLanguageServer": true,
  "go.formatTool": "gofmt",
  "go.lintTool": "golangci-lint"
}
```

## ⚙️ 通用配置

### Git 优化配置
```json
{
  "git.autofetch": false,              // 禁用自动拉取
  "git.refreshInterval": 5000,         // 5 秒刷新间隔
  "git.inputValidation": "always",      // 强制验证 commit message
  "git.inputValidationLength": 5       // 最少 5 字符
}
```

### 编辑器体验
```json
{
  "files.autoSave": "onFocusChange",        // 失焦自动保存
  "workbench.editor.limit.value": 5,       // 标签页限制
  "editor.smoothScrolling": true,          // 平滑滚动
  "workbench.colorTheme": "One Dark Pro"   // 主题设置
}
```

---

## 📦 推荐扩展

### 核心工具（必装）

| 扩展 | 功能 | 适用语言 |
|------|------|----------|
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python 语言支持 | Python |
| [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) | 现代化 Linter + Formatter | Python |
| [Basedpyright](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright) | 严格类型检查 | Python |
| [Go](https://marketplace.visualstudio.com/items?itemName=golang.go) | Go 语言支持 | Go |
| [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) | Git 增强工具 | All |

### 通用语言支持

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

### Q1: 如何选择正确的配置文件？

**A**: 根据项目类型选择：
- **Python 项目**: 复制 `common/` + `python/` 目录下的所有文件
- **Go 项目**: 复制 `common/` + `golang/` 目录下的所有文件
- **混合项目**: 可以同时使用多个语言的配置

### Q2: Ruff 和 Basedpyright 冲突？

**A**: 两者职责不同：
- **Ruff**: 负责代码风格（格式化、导入排序、简单错误）
- **Basedpyright**: 负责类型检查（类型注解、函数签名）

配置中已禁用 Basedpyright 的格式化功能，避免冲突。

### Q3: Git 提交时显示 "Input validation failed"？

**A**: Commit message 少于 5 个字符。解决方法：
```bash
# 写一个有意义的 message
git commit -m "Fix: 修复用户登录bug"

# 如需临时跳过验证（不推荐）
git commit -m "wip" --no-verify
```

### Q4: 虚拟环境未自动激活？

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

### Q5: uv 命令未找到？

**A**: 安装 uv：
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# 或使用 pip
pip install uv
```

### Q6: VS Code Git 日志显示大量重复命令？

**A**: 已通过以下配置解决：
- 禁用 `git.autofetch`
- 增加 `git.refreshInterval` 到 5000ms

如仍有问题，可进一步增加刷新间隔：
```json
{"git.refreshInterval": 10000}  // 10 秒
```

---

## 📚 参考资源

### Python 相关
- [Ruff 官方文档](https://docs.astral.sh/ruff/)
- [Basedpyright GitHub](https://github.com/DetachHead/basedpyright)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [VS Code Python 教程](https://code.visualstudio.com/docs/python/python-tutorial)
- [FastAPI 调试指南](https://fastapi.tiangolo.com/tutorial/debugging/)

### Go 相关
- [Go 扩展文档](https://github.com/golang/vscode-go/blob/master/docs/settings.md)
- [Delve 调试器](https://github.com/go-delve/delve)
- [golangci-lint](https://golangci-lint.run/)

### 通用资源
- [VS Code 官方文档](https://code.visualstudio.com/docs)
- [GitLens 文档](https://gitlens.amod.io/)

---

## 📄 许可证

本配置文件集为开源项目，采用 MIT 许可证，欢迎自由使用和修改。

## 🤝 贡献

如有改进建议，欢迎提交 Issue 或 Pull Request！

**维护者**: 多语言开发环境配置团队
**关注领域**: Python/Go 开发工具链优化、VS Code 配置最佳实践
