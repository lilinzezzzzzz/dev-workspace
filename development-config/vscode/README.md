# VS Code 用户设置与项目覆盖

本目录采用“统一用户默认设置 + 项目少量覆盖”的方式维护 Python、Go 开发配置。共享的编辑偏好只维护一份；环境文件、导入路径、测试目录和构建条件由项目决定。

生成脚本只更新本目录的生成文件，不读取或覆盖本机用户设置，也不修改任何项目的 `.vscode/`。应用配置需要另行对比、合并。

## 目录与职责

```text
vscode/
├── common/
│   ├── settings.json          # 用户通用默认：界面、Git、终端等
│   ├── project-settings.json  # 项目共享覆盖：原有 YAML 自定义标签
│   ├── extensions.json        # 团队推荐扩展
│   └── keybindings.json       # 用户快捷键
├── python/
│   ├── settings.json          # 用户 Python 默认：Ruff、Pylance、编辑体验
│   ├── project-settings.json  # Python 项目：环境、分析路径、测试、文件关联
│   └── launch.json            # Python / FastAPI 项目调试模板
├── golang/
│   ├── settings.json          # 用户 Go 默认：工具、编辑体验、gopls、Delve
│   └── project-settings.json  # Go 项目：构建、测试、文件关联、终端环境
├── merge-settings.py
├── settings-user.jsonc           # 统一用户默认设置（自动生成）
├── settings-project-python.jsonc # Python 项目覆盖（自动生成）
├── settings-project-golang.jsonc # Go 项目覆盖（自动生成）
├── settings-python.jsonc         # 原有 Python 完整配置（兼容产物）
└── settings-golang.jsonc         # 原有 Go 完整配置（兼容产物）
```

源模板保留分类标题和中文注释。生成文件只保留标题、来源说明和格式化后的正文，不复制逐项注释；五份产物均被 `.gitignore` 忽略，不应手工编辑或强制加入版本控制。

## 拆分原则

| 位置 | 内容 | 更新方式 |
| --- | --- | --- |
| 用户通用默认 | 字体、主题、Git、SCM、终端显示、搜索习惯、通用目录排除、Docker 提示、Stats Bar、缩进颜色、数据文件编辑偏好 | 修改 `common/settings.json` |
| 用户 Python 默认 | 环境自动激活、`[python]` 编辑行为、Ruff 统一规则、Pylance 补全与提示、Notebook 偏好 | 修改 `python/settings.json` |
| 用户 Go 默认 | `[go]` 等语言块、工具选择、gopls 分析与补全、Inlay Hints、Delve 显示和覆盖率偏好 | 修改 `golang/settings.json` |
| 共享项目覆盖 | `yaml.customTags` 中的 `!reference sequence` | 修改 `common/project-settings.json`；项目不用相应标签时可不保留 |
| Python 项目覆盖 | `.env`、分析路径与排除、pytest / unittest 选择、测试目录与参数、文件关联 | 按项目调整 `python/project-settings.json` |
| Go 项目覆盖 | 构建标记、gopls 环境、Lint / 测试参数、文件关联、目录排除、`GOFLAGS` | 按项目调整 `golang/project-settings.json` |

### 保证范围与跨项目生效

这次拆分保证“原有显式配置值不变”：两份兼容完整配置保持拆分前的设置值；统一用户默认与对应项目覆盖组合后，旧配置中明确设置过的每一项仍保持原值。不升级工具、不修改现有规则内容。原来通用模板中的文件排除与监听排除仍作为个人默认保留，项目可另行覆盖。

统一用户默认会扩大部分设置的适用范围。原先只存在于某种语言模板中的设置，应用到用户级后也会被其他项目继承；因此，这项保证不等于所有项目迁移后的完整有效配置或运行行为与以前完全相同。

| 设置 | 统一用户默认中的值 | 应用后的范围 |
| --- | --- | --- |
| `notebook.formatOnSave.enabled` | `false` | 所有项目中的 Notebook，不限于 Python 项目 |
| `notebook.codeActionsOnSave` | 保留原有显式保存时的修复、整理导入动作 | 所有项目中的 Notebook；实际动作取决于相应语言与扩展是否提供支持 |
| `[makefile]` | Tab 缩进、宽度 4 | 所有项目中被识别为 Makefile 的文件 |
| `[dockerfile]` | 空格缩进、宽度 4 | 所有项目中被识别为 Dockerfile 的文件 |
| `[python]`、`[go]` 及对应语言工具设置 | 保留原有语言默认值 | 任意项目中相应语言的文件，不根据项目被称为 Python 或 Go 项目来隔离 |

例如，原先只使用 Go 完整配置的项目会新增继承 Notebook 和 Python 默认设置；原先只使用 Python 完整配置的项目会新增继承 Go、Makefile 和 Dockerfile 默认设置。项目需要例外时，应在对应层级覆盖相关选项，迁移时也要验证这些新增生效范围。

### 用户级与项目级的优先级

同一项、同一语言层级下，项目设置优先于用户设置。对象设置会合并，数组会整体替换。

语言专用设置优先于普通编辑器设置。例如用户默认中的 `[python].editor.formatOnSave`，应通过项目的 `[python]` 块覆盖，不能只在项目顶层写 `editor.formatOnSave`。

因此，已有项目内的完整旧配置不会因为生成了用户配置就自动失效。迁移时要逐项移除重复设置，保留真实的项目差异，不能直接删除整个 `.vscode`。

### 本机工具路径与远程环境

- 不把个人绝对路径、凭证和机器私有配置写进模板。
- `go.alternateTools.go` 保留原模板的 `~/.local/share/mise/shims/go` 默认值，以保持工具选择；这不是对目标机器的自动探测。机器未使用 mise 时应在实际用户设置中按需调整。
- 模板不固定 `todo-tree.ripgrep.ripgrep`；本机已有的 Homebrew ripgrep 路径应在合并用户设置时保留。
- SSH 主机或开发容器可以有独立的远程设置，工具路径应匹配实际运行环境，不应照搬本机绝对路径。
- `http.proxySupport: "off"`、外部文件直接打开和关闭内置 AI 功能仍是原有个人默认值；本次拆分不重新选择这些策略。

## 生成配置

在仓库根目录执行：

```bash
# 生成统一用户设置、两份项目覆盖和两份兼容完整配置
python3 -B development-config/vscode/merge-settings.py
```

也可选择目标，多个选项可以组合：

```bash
# 只更新共享用户配置
python3 -B development-config/vscode/merge-settings.py --user

# 只更新 Python 或 Go 项目覆盖
python3 -B development-config/vscode/merge-settings.py --project-python --project-golang

# 保留旧 CLI 用法：只生成对应语言的完整配置
python3 -B development-config/vscode/merge-settings.py --python
python3 -B development-config/vscode/merge-settings.py --golang
```

| 产物 | 合并顺序（后面的覆盖前面的） | 用途 |
| --- | --- | --- |
| `settings-user.jsonc` | common 用户默认 → Python 用户默认 → Go 用户默认 | 对比并合并到 VS Code 用户设置 |
| `settings-project-python.jsonc` | common 项目覆盖 → Python 项目覆盖 | Python 项目 `.vscode/settings.json` 的起点 |
| `settings-project-golang.jsonc` | common 项目覆盖 → Go 项目覆盖 | Go 项目 `.vscode/settings.json` 的起点 |
| `settings-python.jsonc` | common 用户默认 → Python 用户默认 → common 项目覆盖 → Python 项目覆盖 | 兼容原来的完整 Python 配置 |
| `settings-golang.jsonc` | common 用户默认 → Go 用户默认 → common 项目覆盖 → Go 项目覆盖 | 兼容原来的完整 Go 配置 |

统一用户文件同时包含 Python、Go 默认设置，以及跨项目生效的 Notebook、Makefile、Dockerfile 等偏好，具体范围见“保证范围与跨项目生效”。它不是两份旧完整配置的直接合并，不包含项目环境、测试目录和构建条件。旧完整产物保留原语言配置的设置值，用于迁移过渡，不应继续作为新项目的首选方式。

## 应用与迁移

以下是后续迁移步骤；运行生成脚本本身不会执行这些操作。

1. 用命令面板的 `Preferences: Open User Settings (JSON)` 打开实际用户设置，将 `settings-user.jsonc` 与其对比合并。保留本机工具路径、已有私有配置和有意选择的个人覆盖，不要整份直接替换。
2. 检查项目现有 `.vscode/settings.json`。先保留项目专有设置，再清理已由用户默认提供的重复项。
3. 对照相应 `settings-project-*.jsonc`，只保留项目实际需要的覆盖。`tests/`、`${workspaceFolder}` 和 `.env` 是现有模板的默认约定，不保证适合所有项目。
4. 按需将 `python/launch.json` 合并到项目调试配置，将推荐扩展列表合并到 `.vscode/extensions.json`。项目已有的调试项和扩展推荐应保留。
5. 先在一个项目验证补全、Ruff、测试发现和调试，再逐步迁移其他项目。

同一项目如同时使用 Python、Go，应合并两份项目覆盖并审查冲突，特别是文件关联、排除目录、构建条件和测试参数；脚本不自动决定项目采用哪套规则。没有特殊配置的项目可以不创建 `settings.json`。

`settings-user.jsonc` 不是含个人配置的最终用户文件：每次更新都需要对比合并一次。完成迁移后，共享设置的后续调整不再需要复制到每个项目。更换 Profile 或远程环境时，也应检查对应设置层级是否有覆盖。

### 配置文件的应用位置

| 内容 | 位置 |
| --- | --- |
| 用户设置 | 用户 `settings.json` |
| 项目设置 | `.vscode/settings.json`，或多根工作区对应的设置层级 |
| 快捷键 | 用户级 `keybindings.json`，不支持项目级 |
| 扩展推荐 | `.vscode/extensions.json`，或 `.code-workspace` 的 `extensions.recommendations` |
| 项目调试 | `.vscode/launch.json` |
| 通用调试项 | 可手工合并到用户 `settings.json` 的 `launch` 对象；不直接复制用户级 `launch.json` |

本仓库的快捷键包括前进、后退及文档格式化；macOS 使用 `Cmd+Option+L` 格式化，Windows/Linux 使用 `Ctrl+Alt+L`。应用前与已有用户快捷键对比合并。

## Python 行为与项目差异

用户默认中的 Python 编辑行为摘录：

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "never",
      "source.organizeImports.ruff": "never"
    }
  },
  "ruff.configurationPreference": "editorOnly",
  "python.analysis.diagnosticMode": "openFilesOnly"
}
```

- 保留现有 Ruff 规则：行长 88、现有 `select` / `ignore`、FastAPI immutable calls 和 `editorOnly`。该策略以编辑器规则为准，不会因拆分就改成读取项目 TOML；若项目要求以自己的 `pyproject.toml` 或 `ruff.toml` 为准，需要单独决定并在项目中覆盖规则来源。
- Pylance 继续提供补全和类型分析，保留现有提示及诊断抑制设置，不额外指定 `typeCheckingMode`。
- 普通 Python 文件保存时仍不自动格式化、修复或整理导入；Notebook 的保存行为仍由原有 `notebook.*` 设置单独控制。
- Python 项目覆盖保留 pytest 开启、unittest 关闭、`tests/**/*.py` 发现范围及原有 pytest 参数；环境文件仍为 `${workspaceFolder}/.env`。
- 模板不固定 Python 解释器。通过 `Python: Select Interpreter` 选择项目环境；uv 的建环境和依赖安装通过终端执行，不由模板自动完成。
- 修改 `ruff.enable` 后，扩展可能提示重启 VS Code。拆分没有切换该值，统一默认中仍为 `true`。

### FastAPI 调试

`python/launch.json` 保留 FastAPI、当前 Python 文件及当前测试文件三项调试配置。FastAPI 参数为：

```jsonc
{
  "args": [
    "main:app",
    "--host", "0.0.0.0", // 监听所有 IPv4 网络接口
    "--port", "8000"     // 默认端口
  ]
}
```

调试器使用工作区当前解释器，默认读取项目 `.env`，不启用 Uvicorn 热重载。应用入口、端口和环境按项目调整。`0.0.0.0` 便于容器端口映射和其他设备访问，实际访问范围取决于端口发布与防火墙；只需本机访问时可改为 `127.0.0.1`。

## Go 行为与项目差异

- 用户默认保留 Go 工具选择、`goimports` 格式化、gopls 分析与补全、参数提示、覆盖率显示及 Delve 偏好。
- `[go]` 保存时格式化、显式保存时整理导入，保留原有 Tab 缩进和行宽标记；`[go.mod]`、`[go.sum]`、Makefile 和 Dockerfile 编辑偏好也保留。
- `go.lintFlags`、`go.testFlags`（`-v`、`-race`）、30 秒超时、测试环境及构建标记移入 Go 项目覆盖，值不变。
- `gopls.buildFlags` 和 `gopls.env` 移入项目覆盖，其他 gopls 偏好保留在用户默认中。
- `terminal.integrated.env.*` 中的 `GOFLAGS: "-mod=mod"` 仅在 Go 项目覆盖中；合并时继续保留 common 中的 Python IO 和字节码环境设置。
- Go 工程文件关联、vendor / bin / dist 等排除及搜索排除按原值保留在项目覆盖中。

## 推荐扩展

`common/extensions.json` 只表达团队推荐，不会自动安装、卸载扩展，也不影响设置继承。当前推荐列表保持不变：

| 类别 | 扩展 ID |
| --- | --- |
| 界面语言 | `ms-ceintl.vscode-language-pack-zh-hans` |
| 远程与容器 | `ms-vscode-remote.remote-containers`、`ms-vscode-remote.remote-ssh`、`ms-azuretools.vscode-containers`、`docker.docker` |
| Python | `ms-python.python`、`charliermarsh.ruff`、`ms-python.vscode-pylance` |
| 配置文件与接口 | `redhat.vscode-yaml`、`tamasfe.even-better-toml`、`bufbuild.vscode-buf`、`mikestead.dotenv` |
| 诊断与标记 | `usernamehw.errorlens`、`gruntfuggly.todo-tree` |
| 编辑辅助 | `oderwat.indent-rainbow`、`editorconfig.editorconfig` |
| 文档 | `yzhang.markdown-all-in-one`、`davidanson.vscode-markdownlint`、`tomoki1207.pdf` |
| 系统状态 | `njzy.stats-bar` |
| 主题与图标 | `romanrei.material-dark`、`pkief.material-icon-theme`、`pkief.material-product-icons` |

Go 项目仍需单独安装 `golang.go`。Python 扩展配套的 Debugger 和 Environments 分别负责调试与环境管理；它们不是 Ruff、Pylance 的替代品。内置 Git 继续提供当前行 Blame、提交图、文件时间线、三方合并编辑器和 Worktree 检测，不重新引入已清理的 GitLens 等扩展。

可用 `code --list-extensions` 查看已安装扩展，在命令面板运行 `Extensions: Show Recommended Extensions` 查看推荐。Docker DX、Container Tools 和 Dev Containers 的职责不同，保留原有组合及 Docker DX Compose 服务关闭的设置。

## 验证

在仓库根目录运行：

```bash
python3 -B -m unittest tests/test_merge_vscode_settings.py
python3 -B development-config/vscode/merge-settings.py
```

测试分别验证“原有显式配置值不变”和新增用户默认的跨项目继承，不把旧键的值相同当作完整有效配置相同。测试覆盖 Notebook、Makefile、Dockerfile 及另一种语言默认设置的新增继承，也验证项目可以覆盖这些偏好而保留同一对象中的其他默认项。

此外，测试覆盖生成目标、用户与项目边界、嵌套对象和数组覆盖、选择性生成及保护用户/项目文件。这些是配置组合与生成流程的验证；已有项目的实际迁移仍应在目标 VS Code 窗口验证，生成成功不代表项目已应用。

## 参考资料

- [VS Code 设置优先级](https://code.visualstudio.com/docs/configure/settings#_settings-precedence)
- [全局调试配置](https://code.visualstudio.com/docs/debugtest/debugging-configuration#_global-launch-configuration)
- [Ruff 编辑器设置](https://docs.astral.sh/ruff/editors/settings/)
- [Go 扩展设置](https://github.com/golang/vscode-go/blob/master/docs/settings.md)
