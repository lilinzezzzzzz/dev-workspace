# VS Code 多语言开发环境配置

> 通用设置与 Python / Go 开发配置模板

一套开箱即用的 VS Code 配置方案，支持 Python 和 Go 语言开发，采用模块化配置结构，提供一致的团队开发体验和最佳实践。

---

## 📋 目录

- [特性](#特性)
- [目录结构](#目录结构)
- [配置文件说明](#配置文件说明)
- [快速开始](#快速开始)
- [Python 开发配置](#python-开发配置)
- [Go 开发配置](#go-开发配置)
- [通用配置](#通用配置)
- [推荐扩展](#推荐扩展)
- [常见问题](#常见问题)

---

## 特性

### 🐍 多语言支持

- **Python 开发**: Ruff + Pylance 工具链，uv 依赖管理
- **Go 开发**: Go 语言专用配置和调试支持
- **通用配置**: 编辑器核心设置、主题、快捷键等跨语言共享

### 🎨 编辑器增强

- **模块化设计**: 按语言分离配置，便于维护和扩展
- **视觉优化**: Material Dark Theme 主题 + Material Icon，使用紧凑布局和活动栏
- **智能辅助**: 语言服务补全、括号高亮、TODO 聚合和内联诊断
- **性能优化**: 标签页限制、自动保存、平滑滚动

### 🔧 Git 工作流

- **提交验证**: 启用输入验证
- **状态监控**: 自动 Fetch 更新远程跟踪信息，不自动合并代码
- **内置 Git**: 当前行 Blame、提交图、文件时间线、三方合并编辑器和 Worktree 自动检测

### 🎯 其他亮点

- **快捷键优化**: `Cmd+Option+L` 格式化文档（PyCharm macOS 风格）
- **文件管理**: 自动排除缓存、智能搜索过滤
- **多格式支持**: YAML、TOML、Jinja2、JSON、Markdown

> ⚠️ **注意**: `keybindings.json` 只支持用户级别配置，不支持工作区级别。详见 [配置文件说明](#配置文件说明)。

---

## 目录结构

```text
vscode/
├── common/               # 通用配置（跨语言共享）
│   ├── settings.json     # 编辑器核心设置、主题、Git等
│   ├── extensions.json   # 推荐扩展列表
│   └── keybindings.json  # 自定义快捷键映射（⚠️ 仅支持用户级别）
├── python/               # Python 专用配置
│   ├── settings.json     # Python 工具链配置（Ruff、Pylance等）
│   └── launch.json       # Python 调试配置
├── golang/               # Go 专用配置
│   └── settings.json     # Go 语言配置
├── merge-settings.py     # 深度合并通用配置与语言配置
├── settings-python.jsonc # Python 合并产物（自动生成）
├── settings-golang.jsonc # Go 合并产物（自动生成）
└── README.md             # 本文档
```

## 配置文件说明

### 使用方式

#### 方式一：工作区级配置（推荐）
先运行合并脚本，再将对应语言的合并产物应用到项目根目录的 `.vscode/` 文件夹。已有配置先对比并合并，避免直接覆盖：

Python 项目：

```bash
project-root/
└── .vscode/
    ├── settings.json     # 来自 settings-python.jsonc
    ├── extensions.json   # 来自 common/
    └── launch.json       # 来自 python/
```

> ⚠️ **注意**: `keybindings.json` 不支持工作区级别，必须放在用户目录。

Go 项目：

```bash
project-root/
└── .vscode/
    ├── settings.json     # 来自 settings-golang.jsonc
    └── extensions.json   # 来自 common/
```

#### 方式二：用户级配置

- `common/settings.json` → VS Code 用户设置，应用前与现有设置对比并合并
- `common/keybindings.json` → 用户快捷键设置（⚠️ 必须使用用户级别）

> **配置文件级别支持对照表**:
>
> | 配置文件 | 用户级别 | 工作区级别 |
> | -------- | :-----: | :-------: |
> | `settings.json` | ✅ | ✅ |
> | `keybindings.json` | ✅ | ❌ |
> | `extensions.json` | ❌ | ✅ |
> | `launch.json` | 通过用户 `settings.json` 的 `launch` 对象 | ✅ |
> | `tasks.json` | ✅ | ✅ |

扩展推荐应写入项目 `.vscode/extensions.json`，多根工作区也可写入 `.code-workspace` 的 `extensions.recommendations`。全局调试配置应合并进用户 `settings.json` 的 `launch` 对象，不是把 `launch.json` 复制到用户目录；本仓库的调试模板依赖项目文件与环境，优先作为项目级配置使用。

---

## 快速开始

### 1️⃣ 安装推荐扩展

打开配置了推荐列表的项目后，VS Code 会提示安装推荐扩展，也可在命令面板执行“Extensions: Show Recommended Extensions”查看推荐列表。以下命令可查看已安装扩展，并手动安装部分核心扩展：

```bash
# 查看已安装扩展
code --list-extensions

# 批量安装核心扩展
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.vscode-pylance
code --install-extension davidanson.vscode-markdownlint
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-azuretools.vscode-containers
code --install-extension docker.docker
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
# 在仓库根目录生成 Python、Go 两份完整配置
python3 -B development-config/vscode/merge-settings.py

# 新项目先创建 .vscode 目录；以下以当前目录为目标项目
mkdir -p .vscode

# Python 项目选择这一份；-i 在文件已存在时询问是否覆盖
cp -i development-config/vscode/settings-python.jsonc .vscode/settings.json
cp -i development-config/vscode/python/launch.json .vscode/launch.json

# Go 项目改用这一份，不要在 Python 复制步骤后继续执行
cp -i development-config/vscode/settings-golang.jsonc .vscode/settings.json

# 推荐扩展列表独立应用；快捷键只能手工合并到用户级设置
cp -i development-config/vscode/common/extensions.json .vscode/extensions.json
```

以上源路径相对于本仓库根目录；应用到其他项目时，替换目标 `.vscode/` 为该项目目录。已有 `settings.json` 应先对比再手工合并；拒绝覆盖提示可保留原文件。不要依次复制 `common/settings.json` 与语言目录的 `settings.json`，后一次复制会丢失通用配置。

源模板保留分类标题和中文行尾注释；合并产物由脚本生成，仅保留文件头说明，不逐项复制源注释。不要手工修改合并产物。

### 4️⃣ 验证配置

1. **重启 VS Code** 使配置生效
2. **检查语言支持**：
   - Python: 打开 `.py` 文件应有语法高亮和智能提示
   - Go: 打开 `.go` 文件应有语法高亮和智能提示
3. **测试调试功能**：按 `F5` 启动调试

---

## Python 开发配置

### Python 工具链配置

| 工具 | 作用 | 配置位置 |
| ------ | ------ | ---------- |
| **Ruff** | Python Linter + Formatter | `python/settings.json` |
| **Pylance** | 类型检查器 | `python/settings.json` |
| **uv** | 虚拟环境与依赖管理 | README 的终端步骤；不在模板中指定 uv 命令或路径 |
| **调试配置** | FastAPI/Uvicorn 调试 | `python/launch.json` |

### Python 核心设置

以下为 `python/settings.json` 中的设置摘录：

```json
{
  "ruff.enable": true,
  "python.analysis.diagnosticMode": "openFilesOnly",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "never",
      "source.organizeImports.ruff": "never"
    }
  }
}
```

模板不固定 Python 解释器路径，调试器使用当前选中的工作区解释器；通过“Python: Select Interpreter”选择项目环境。模板也未显式设置 `python.analysis.typeCheckingMode`，该项沿用扩展默认值或其他适用设置，不保证启用 `basic`。Ruff 提供检查与手动格式化，保存时不自动格式化、修复或整理导入。

## Go 开发配置

### Go 工具链配置

| 工具 | 作用 | 配置位置 |
| ------ | ------ | ---------- |
| **Go 扩展** | Go 语言支持 | `golang/settings.json` |
| **调试配置** | Delve 调试器 | 集成在 `golang/settings.json` |
| **格式化** | goimports | `golang/settings.json` |

### Go 核心设置

编译错误诊断由 `gopls` 提供，不再配置已弃用且在启用语言服务器时不适用的 `go.buildOnSave`。

```json
{
  "go.useLanguageServer": true,
  "go.formatTool": "goimports",
  "go.lintTool": "golangci-lint"
}
```

## 通用配置

### 内置 Git 配置

```jsonc
{
  "git.autofetch": true,                       // 更新远程信息，不自动合并
  "git.blame.editorDecoration.enabled": true,   // 当前行作者和提交信息
  "git.mergeEditor": true,                     // 三方合并编辑器
  "git.detectWorktrees": true                  // 自动检测关联的 Worktree
}
```

在源代码管理中查看提交图，在资源管理器的时间线中查看当前文件历史。内置 Blame 显示最后修改当前行的提交作者，不等同于整份文件的逐行批注。

### 网络、安全与本机路径

- `http.proxySupport: "off"` 关闭扩展的代理支持；使用代理的机器应按实际网络环境调整。
- `security.workspace.trust.untrustedFiles: "open"` 直接在当前窗口打开受信任目录外的文件；需要逐次询问时改为 `"prompt"`。
- `chat.disableAIFeatures: true` 关闭 VS Code 内置聊天与 AI 功能。
- 通用模板不固定 `todo-tree.ripgrep.ripgrep` 的本机绝对路径；仅在目标机器需要时补充。
- `go.alternateTools` 仍由 `golang/settings.json` 管理，按目标机器的 Go / mise 安装方式调整，不复制到 common 或 Python 配置。
- 系统证书及高对比度主题沿用 VS Code 默认值，不额外添加覆盖。

### 编辑器体验

```jsonc
{
  "files.autoSave": "onFocusChange",              // 失焦自动保存
  "workbench.editor.limit.value": 6,               // 标签页限制
  "editor.smoothScrolling": true,                  // 平滑滚动
  "diffEditor.wordWrap": "off",                   // 源代码管理差异视图关闭自动换行
  "editor.fontSize": 12.5,                         // 编辑器字体大小
  "terminal.integrated.fontSize": 12.5,            // 终端字体大小
  "files.exclude": {
    "**/.venv": true,
    "**/venv": true,
    "**/.spec": true
  },
  "search.exclude": {
    "**/.spec": true
  },
  "workbench.colorTheme": "Material Dark Theme"   // 主题设置
}
```

---

## 推荐扩展

### 核心工具（必装）

| 扩展 | 功能 | 适用语言 |
| ------ | ------ | ---------- |
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python 语言支持 | Python |
| [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) | 现代化 Linter + Formatter | Python |
| [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) | 静态类型检查 | Python |

Python 扩展会配套推荐 Pylance、Python Debugger 和 Python Environments；它们分别负责语言分析、调试和环境管理，不属于重复功能。现有 Python 格式化、诊断和测试配置保持独立维护。

### 界面语言

- **简体中文语言包**: `ms-ceintl.vscode-language-pack-zh-hans`

### 开发容器

| 扩展 | 功能 |
| ------ | ------ |
| [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) | 连接远程主机开发，不要求使用容器 |
| [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) | 容器内开发 |
| [Container Tools](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-containers) | 容器、镜像管理与应用调试 |
| [Docker DX](https://marketplace.visualstudio.com/items?itemName=docker.docker) | Dockerfile / Compose / Bake 编辑增强 |

Docker DX、Container Tools 与 Dev Containers 职责不同。当前关闭 Docker DX 的 Compose 语言服务，减少与其他 Compose 编辑支持重叠；不需要因此移除 Dockerfile 编辑或容器管理扩展。

### 通用语言支持

- **YAML**: `redhat.vscode-yaml`
- **TOML**: `tamasfe.even-better-toml`
- **Protobuf**: `bufbuild.vscode-buf`
- **dotenv**: `mikestead.dotenv`

### 代码质量与标记

- **Error Lens**: `usernamehw.errorlens`（内联显示错误/警告）
- **TODO Tree**: `gruntfuggly.todo-tree`（TODO/FIXME 聚合）

### 辅助工具

- **Indent Rainbow**: `oderwat.indent-rainbow`（缩进着色）
- **EditorConfig**: `editorconfig.editorconfig`（统一代码风格）

### Markdown / 文档

- **Markdown All in One**: `yzhang.markdown-all-in-one`
- **markdownlint**: `davidanson.vscode-markdownlint`（检查与默认格式化工具）
- **vscode-pdf**: `tomoki1207.pdf`（PDF 预览）

### 系统状态

- **Stats Bar**: `njzy.stats-bar`（状态栏 CPU / 内存显示）

推荐列表不再包含 GitLens、Comment Translate、Better Comments 和 Path Intellisense，也不添加 npm Intellisense。使用内置 Git、语言服务补全和 Todo Tree 覆盖日常需求。扩展推荐不会自动卸载已经安装的扩展。

### 主题 / 图标

- **Material Dark Theme**: `romanrei.material-dark`
- **Material Icon Theme**: `pkief.material-icon-theme`
- **Material Product Icons**: `pkief.material-product-icons`

---

## ⚙️ 自定义配置

### 修改 Python 解释器路径

模板不固定解释器路径，优先通过“Python: Select Interpreter”选择环境。需要指定初始默认路径时，按系统选择以下示例之一，路径应替换为实际解释器位置。

Linux/macOS 示例：

```json
{
  "python.defaultInterpreterPath": "/usr/bin/python3"
}
```

Windows 示例：

```json
{
  "python.defaultInterpreterPath": "C:\\Python311\\python.exe"
}
```

已为工作区选过解释器时，修改 `python.defaultInterpreterPath` 不会自动切换当前解释器，应重新执行“Python: Select Interpreter”。

### 启用/禁用 Git 输入验证

```jsonc
{
  "git.inputValidation": true,   // 启用输入验证
  "git.confirmSync": false       // 同步时不弹确认对话框
}
```

### 更换主题

`workbench.colorCustomizations` 在 `common/settings.json` 中统一维护，供 Python 和 Go 配置共享。`Material Dark Theme` 下仅将编辑器背景设为 `#111111`，不覆盖侧边栏、活动栏、面板和状态栏背景。选区、标签页和资源管理器等颜色使用全局覆盖，切换主题后仍会生效。

修改通用配置后，运行 `python3 -B development-config/vscode/merge-settings.py`，同步生成 `settings-python.jsonc` 和 `settings-golang.jsonc`。

```jsonc
{
  "workbench.colorTheme": "Dark 2026",         // 替换为内置主题
  "workbench.iconTheme": "material-icon-theme" // 文件图标主题
}
```

### 调整 FastAPI 调试端口

编辑 `.vscode/launch.json` 中 FastAPI 调试项的 `args`。以下与 `python/launch.json` 的默认值一致，只调整 `--port` 后面的值即可：

```jsonc
{
  "args": [
    "main:app",
    "--host", "0.0.0.0",  // 监听所有 IPv4 网络接口
    "--port", "8000"      // 默认端口 8000
  ]
}
```

模板默认监听 `0.0.0.0`，便于通过容器端口映射或从其他设备访问；实际可访问范围还取决于端口发布和防火墙配置。直接在本机调试且只需本机访问时，可按需改为 `127.0.0.1`。

---

## 常见问题

### Q1: 如何选择正确的配置文件？

**A**: 根据项目类型选择：

- **Python 项目**: 使用 `settings-python.jsonc`，按需应用推荐扩展和 Python 调试配置
- **Go 项目**: 使用 `settings-golang.jsonc`（需单独安装 Go 扩展）
- **混合项目**: 手工深度合并两个语言模板；当前脚本只生成 Python、Go 两份独立配置

> **注意**: Go 扩展 `golang.go` 需要单独安装，不在默认推荐扩展列表中。

### Q2: Ruff 和 Pylance 冲突？

**A**: 两者职责不同：

- **Ruff**: 负责代码风格（格式化、导入排序、简单错误）
- **Pylance**: 负责类型检查（类型注解、函数签名）

模板通过 `[python].editor.defaultFormatter` 选择 Ruff 格式化，没有“禁用 Pylance 格式化”的设置。Pylance 的 `reportUnusedImport`、`reportUnusedVariable` 和 `reportMissingTypeStubs` 在模板中设为 `none`；其中前两项交由 Ruff 检查，缺少类型存根的提示不再显示。

### Q3: Git 提交验证如何配置？

**A**: 配置中已启用输入验证：

```jsonc
{
  "git.inputValidation": true  // 启用输入验证
}
```

如需跳过验证（不推荐）：

```bash
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

**A**: 先查看“输出 → Git”中的命令来源。当前模板启用自动 Fetch，周期性更新远程信息属于预期行为，不会自动合并代码。如不需要后台更新，可按需关闭 `git.autofetch`。当前行 Blame 按所查看的行读取作者信息；若仓库很大且影响操作，可临时关闭行尾 Blame 排查。模板已移除 GitLens 配置，不应再调整 `gitlens.*` 设置。

### Q7: 快捷键配置不生效？

**A**: `keybindings.json` 只支持用户级别配置，不支持工作区级别。请将配置复制到用户目录：

```bash
# Qoder (macOS)
cp keybindings.json ~/Library/Application\ Support/Qoder/User/keybindings.json

# VS Code (macOS)
cp keybindings.json ~/Library/Application\ Support/Code/User/keybindings.json

# VS Code (Windows)
copy keybindings.json %APPDATA%\Code\User\keybindings.json

# VS Code (Linux)
cp keybindings.json ~/.config/Code/User/keybindings.json
```

---

## 📚 参考资源

### Python 相关

- [Ruff 官方文档](https://docs.astral.sh/ruff/)
- [Pylance GitHub](https://github.com/microsoft/pylance-release)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [VS Code Python 教程](https://code.visualstudio.com/docs/python/python-tutorial)
- [FastAPI 调试指南](https://fastapi.tiangolo.com/tutorial/debugging/)

### Go 相关

- [Go 扩展文档](https://github.com/golang/vscode-go/blob/master/docs/settings.md)
- [Delve 调试器](https://github.com/go-delve/delve)
- [golangci-lint](https://golangci-lint.run/)

### 通用资源

- [VS Code 官方文档](https://code.visualstudio.com/docs)
- [VS Code Git 历史与 Blame](https://code.visualstudio.com/docs/sourcecontrol/history)

---

## 📄 许可证

本配置文件集为开源项目，采用 MIT 许可证，欢迎自由使用和修改。

## 🤝 贡献

如有改进建议，欢迎提交 Issue 或 Pull Request！

**维护者**: 多语言开发环境配置团队
**关注领域**: Python/Go 开发工具链优化、VS Code 配置最佳实践
