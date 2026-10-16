# VS Code 用户设置与项目覆盖

本目录采用“统一用户默认设置 + 项目少量覆盖”的方式维护 Python、Go 开发配置。共享的编辑偏好只维护一份；环境文件、导入路径、测试目录和构建条件由项目决定。

生成脚本只更新本目录的生成文件，不读取或覆盖本机用户设置，也不修改任何项目的 `.vscode/`。应用配置需要另行对比、合并。

## 目录与职责

```text
vscode/
├── common/
│   ├── settings.jsonc         # 用户通用默认：界面、Git、终端等
│   ├── project-settings.jsonc # 项目共享覆盖：原有 YAML 自定义标签
│   ├── extensions.jsonc       # 团队推荐扩展
│   └── keybindings.jsonc      # 用户快捷键
├── python/
│   ├── settings.jsonc         # 用户 Python 默认：Ruff、Pylance、编辑体验
│   ├── project-settings.jsonc # Python 项目：环境、分析路径、测试、文件关联
│   └── launch.jsonc           # Python / FastAPI 项目调试模板
├── golang/
│   ├── settings.jsonc         # 用户 Go 默认：工具、编辑体验、gopls、Delve
│   └── project-settings.jsonc # Go 项目：构建、测试、文件关联、终端环境
├── apply-config.sh               # 统一入口：可选生成，再进入应用流程
├── settings-user.jsonc           # 统一用户默认设置（自动生成）
├── settings-project-python.jsonc # Python 项目覆盖（自动生成）
└── settings-project-golang.jsonc # Go 项目覆盖（自动生成）
```

源模板统一使用 `.jsonc`，保留分类标题和中文注释，避免按严格 JSON 检查注释。生成文件只保留标题、来源说明和格式化后的正文，不复制逐项注释；三份产物均被 `.gitignore` 忽略，不应手工编辑或强制加入版本控制。

Python 实现位于仓库的 `scripts/vscode/`：`merge-settings.py` 负责生成，`apply-settings.py` 负责应用，`jsonc_settings.py` 负责保留未改动字段注释的 JSONC 编辑。实现始终定位到本配置目录，不依赖调用者的工作目录。

## 拆分原则

| 位置 | 内容 | 更新方式 |
| --- | --- | --- |
| 用户通用默认 | 字体、主题、Git、SCM、终端显示、搜索习惯、通用目录排除、Docker 提示、Stats Bar、缩进颜色、数据文件编辑偏好 | 修改 `common/settings.jsonc` |
| 用户 Python 默认 | 环境自动激活、`[python]` 编辑行为、Ruff 统一规则、Pylance 补全与提示、Notebook 偏好 | 修改 `python/settings.jsonc` |
| 用户 Go 默认 | `[go]` 等语言块、工具选择、gopls 分析与补全、Inlay Hints、Delve 显示和覆盖率偏好 | 修改 `golang/settings.jsonc` |
| 共享项目覆盖 | `yaml.customTags` 中的 `!reference sequence` | 修改 `common/project-settings.jsonc`；项目不用相应标签时可不保留 |
| Python 项目覆盖 | `.env`、分析路径与排除、pytest / unittest 选择、测试目录与参数、文件关联 | 按项目调整 `python/project-settings.jsonc` |
| Go 项目覆盖 | 构建标记、gopls 环境、Lint / 测试参数、文件关联、目录排除、`GOFLAGS` | 按项目调整 `golang/project-settings.jsonc` |

### 保证范围与跨项目生效

这次拆分保证“原有显式配置值不变”：统一用户默认与对应项目覆盖组合后，原模板中明确设置过的每一项仍保持原值。不升级工具、不修改现有规则内容。原来通用模板中的文件排除与监听排除仍作为个人默认保留，项目可另行覆盖。

上述保证针对配置拆分。测试保存后的自动发现模式现使用 `${workspaceFolder}/tests/**/*.py`，由 Python 扩展展开为绝对路径，以兼容父路径包含 `.codex` 等隐藏目录的工作区；测试工作目录、pytest 目标目录和运行参数保持不变。

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
# 生成统一用户设置及两份项目覆盖
./development-config/vscode/apply-config.sh --generate-only
```

也可选择目标，多个选项可以组合：

```bash
# 只更新共享用户配置
./development-config/vscode/apply-config.sh --generate-only --user

# 只更新 Python 或 Go 项目覆盖
./development-config/vscode/apply-config.sh --generate-only --project-python --project-golang

```

| 产物 | 合并顺序（后面的覆盖前面的） | 用途 |
| --- | --- | --- |
| `settings-user.jsonc` | common 用户默认 → Python 用户默认 → Go 用户默认 | 对比并合并到 VS Code 用户设置 |
| `settings-project-python.jsonc` | common 项目覆盖 → Python 项目覆盖 | Python 项目 `.vscode/settings.json` 的起点 |
| `settings-project-golang.jsonc` | common 项目覆盖 → Go 项目覆盖 | Go 项目 `.vscode/settings.json` 的起点 |

统一用户文件同时包含 Python、Go 默认设置，以及跨项目生效的 Notebook、Makefile、Dockerfile 等偏好，具体范围见“保证范围与跨项目生效”。它不包含项目环境、测试目录和构建条件；这些内容由对应项目覆盖提供。

## 应用与迁移

### 使用应用脚本

在仓库根目录准备开发环境，然后启动统一入口：

```bash
uv sync --locked
./development-config/vscode/apply-config.sh
```

本仓库的本地开发环境由 `.python-version` 固定为 Python 3.14；脚本最低要求 Python 3.11，以兼容现有容器。开发依赖和锁定版本由仓库根目录的 `pyproject.toml`、`uv.lock` 管理。

Shell 入口根据自身位置定位仓库，并通过 `uv run --project <仓库根目录> --locked` 使用仓库环境。从其他目录调用时不会切换当前工作目录，相对项目路径仍相对调用位置解析。首次运行可能按锁文件准备仓库环境；目标项目的环境和依赖另行管理。

无参数启动时先询问 `是否生成配置? [y/N]`：`y` 刷新三份配置，回车或 `n` 跳过生成并使用现有文件，随后进入应用菜单。跳过时不会自动补生成缺失文件；选择应用后若缺少对应配置，会提示先生成。带应用参数的命令行模式仍自动生成。选择生成后，即使随后取消或只预览，仓库内的生成文件仍已更新，用户和项目的 `settings.json` 不会因此写入。`--generate-only` 只生成，不进入应用流程；`--help` 和子命令帮助不生成文件。参数及退出状态原样转发，生成失败时停止。

应用流程隐藏生成日志，完成生成选择后显示菜单；带应用参数时直接显示应用预览；生成错误仍正常显示。需要查看生成结果时使用 `--generate-only`。

Python 交互输入在提供 `readline` / libedit 的环境中启用终端行编辑，支持中文退格和光标编辑，不记录输入历史；缺少该模块时回退为普通输入。

交互问题使用 `[?]` 标记，输入位于下一行的 `>` 后；配置摘要和详细差异使用独立标题，执行结果使用 `[完成]` / `[结果]`，提醒和错误使用 `[!]` / `[错误]`，不依赖终端颜色。

入口及相关 Python 脚本的提示、帮助、摘要和错误信息保留中文内容，标点统一使用 ASCII 半角符号，如 `: `、`, `、`; `、`?` 和 `()`；短提示省略句末句号，标题分隔线使用 `-`。路径、配置值和差异内容按原文显示，不转换其中的标点。

菜单顺序为 `1. Python 项目配置 (默认)`、`2. Go 项目配置`、`3. 用户配置`、`0. 取消`；回车选择 Python。项目根目录必填且输入后立即检查，路径无效时直接报错退出。Python 根目录留空使用项目根目录。

输入完成后先统计“新增设置”和“同名值不同”的数量，不重复计算冲突与修改。然后展示全部建议的“当前值 → 应用后值”，再选择处理方式：

- `1. 全部应用`（默认）：选中全部新增项及不同值，仍需最后确认才写入。
- `2. 逐项处理`：每项展示当前值和建议值；默认选项 1 保留当前值或跳过新增，选项 2 使用建议值或新增此项。
- `0. 取消`：直接退出，不写入。

嵌套对象按子项统计和选择，数组作为一项整体处理；相同值不询问。全部选择都在内存中进行，不会逐项写入。最后统一显示新增、修改、保留和跳过新增的数量，逐项模式还展示最终选中项的“当前值 → 应用后值”，全部应用模式不重复明细。随后询问是否写入 `[Y/n]`，回车或 `y` 写入，输入 `n` 不写入；全部保留或跳过时不创建或改写文件。中途取消或输入结束不会应用任何选择。预览可能包含本机配置值。

- 用户配置读取 `settings-user.jsonc`；Python 项目读取 `settings-project-python.jsonc` 并根据目录和显式参数产生建议；Go 项目读取 `settings-project-golang.jsonc`，不推断模块布局或运行 Go 命令。
- 三种模式不再使用“模板优先 / 已有值优先”的自动冲突策略，`--conflicts` 参数已移除。模板及项目识别结果作为建议，由批量确认或逐项选择决定是否应用；模板之外的额外键及嵌套子键保留。
- 用户设置默认定位到 VS Code 稳定版的默认 Profile。其他 Profile、Insiders、远程设置或自定义位置必须提供实际路径；脚本不推测当前活动 Profile。
- 应用脚本只写目标 `settings.json`。环境创建、依赖安装，以及快捷键、扩展推荐和调试入口的应用另行处理。

也可以使用命令行，默认统计全部建议且只预览，`--diff` 查看原始文本差异；增加 `--write` 表示明确应用全部建议，不再另行交互确认。需要逐项处理时使用无参数入口：

```bash
# 用户设置：预览；确认后使用同一命令加 --write
./development-config/vscode/apply-config.sh user

# 指定另一个 Profile 的实际用户设置文件
./development-config/vscode/apply-config.sh user \
  --target "/path/to/profile/settings.json" --write

# 项目根目录始终必填
./development-config/vscode/apply-config.sh project-python "/path/to/project"

# Go 项目：预览；确认全部建议后加 --write
./development-config/vscode/apply-config.sh project-golang "/path/to/go-project"

# 手动指定后端布局；模板之外的项目设置继续保留
./development-config/vscode/apply-config.sh project-python "/path/to/project" \
  --python-root backend --source-dir backend/src --test-dir backend/tests \
  --test-framework pytest --env-file backend/.env --write
```

Shell 入口适用于有 Bash 的环境。需要直接调用 Python 时，可从仓库根目录执行 `uv run python -B scripts/vscode/apply-settings.py` 或 `uv run python -B scripts/vscode/merge-settings.py`；直接调用应用实现不会先生成配置。

Python 项目的自动识别只检查目录和 TOML 元数据，不导入项目代码或运行应用：

| 内容 | 自动处理 | 手动指定 |
| --- | --- | --- |
| Python 根目录 | 通常是 `pyproject.toml` 所在目录，不是源码包目录，例如选择 `backend/` 而非 `backend/src/docflow/`；留空使用项目根目录，不自动切换到 `backend/` | `--python-root backend` |
| 源码路径 | 优先使用 Python 根目录下的 `src/`，否则使用 Python 根目录 | `--source-dir`，相对项目根目录，可重复 |
| 测试目录 | 优先保留可定位的已有 pytest 目标，其次读取 TOML 的 `testpaths`，再检查 `tests/`、`test/`、`dev/tests/`；候选不明确时停止 | `--test-dir`，相对项目根目录，可重复 |
| 测试体系 | 沿用已有启用状态；否则有测试目录时按模板使用 pytest，没有则关闭测试发现 | `--test-framework pytest`、`unittest` 或 `none` |
| 环境文件 | 检查 Python 根目录和项目根目录的 `.env`；多个文件时要求指定，不读取其内容 | `--env-file` 或 `--no-env` |
| 默认解释器 | 只检查 Python 根目录下的 `.venv/bin/python`，存在时写入相对工作区的 `.venv/bin/python` 可执行文件路径，避免 Ruff 将 `.venv` 目录当作程序执行；未找到时在预览、写入或无需写入的流程结束后提示 | 已选过解释器时仍需在 VS Code 中检查选择 |

未找到解释器时，不自动创建虚拟环境，也不新增解释器设置；已有解释器配置继续保留。不再检查 `.venv/Scripts/python.exe`。

目录和环境文件参数须位于项目根目录内且已存在。测试保存后的自动发现始终使用 `${workspaceFolder}` 前缀；多测试目录生成 brace 模式。目录存在不能证明测试依赖已安装，脚本也不据此推断所有测试框架，非 pytest 项目应显式选择框架。

已有文件按变更字段编辑，未改动字段的注释、额外键和换行风格保留；被整体替换的数组或值内部注释可能随值替换。重复键、无效 JSONC、目标文件符号链接、指向项目外的 `.vscode` 目录链接，或预览后目标内容及链接位置发生变化时拒绝写入。相同配置重复应用不改写文件。命令行 `--diff` 保留原始 unified diff 格式并显示文本值，按需使用；默认预览只列键名和路径。不自动创建备份，也不删除模板之外的旧设置；不再启用的测试参数可能保留但不会运行。

### 手动应用

也可按以下步骤手动迁移；运行生成脚本本身不会执行这些操作。

1. 用命令面板的 `Preferences: Open User Settings (JSON)` 打开实际用户设置，将 `settings-user.jsonc` 与其对比合并。保留本机工具路径、已有私有配置和有意选择的个人覆盖，不要整份直接替换。
2. 检查项目现有 `.vscode/settings.json`。先保留项目专有设置，再清理已由用户默认提供的重复项。
3. 对照相应 `settings-project-*.jsonc`，只保留项目实际需要的覆盖。`tests/`、`${workspaceFolder}` 和 `.env` 是现有模板的默认约定，不保证适合所有项目。
4. 按需将 `python/launch.jsonc` 合并到 `.vscode/launch.json`，将 `common/extensions.jsonc` 合并到 `.vscode/extensions.json`。项目已有的调试项和扩展推荐应保留。
5. 先在一个项目验证补全、Ruff、测试发现和调试，再逐步迁移其他项目。

`python/project-settings.jsonc` 的行尾注释标明了需要按项目检查的环境文件、源码路径、分析排除范围、测试体系、测试工作目录与参数，以及文件类型关联。测试保存后的自动发现规则匹配文件绝对路径，默认使用 `${workspaceFolder}/tests/**/*.py`；后端位于 `backend/` 时可改为 `${workspaceFolder}/backend/tests/**/*.py`。显式的工作区前缀在变量展开后包含完整路径，避免 `**/` 无法跨过隐藏父目录的问题。`pytestArgs` 中的相对路径仍以 `python.testing.cwd` 为基准。注释不会复制到生成文件，调整项目覆盖时应同时参考源模板。

同一项目如同时使用 Python、Go，应合并两份项目覆盖并审查冲突，特别是文件关联、排除目录、构建条件和测试参数；脚本不自动决定项目采用哪套规则。没有特殊配置的项目可以不创建 `settings.json`。

`settings-user.jsonc` 不是含个人配置的最终用户文件：每次更新都需要对比合并一次。完成迁移后，共享设置的后续调整不再需要复制到每个项目。更换 Profile 或远程环境时，也应检查对应设置层级是否有覆盖。

### 配置文件的应用位置

仓库源模板和生成文件使用 `.jsonc`；应用到 VS Code 时，目标文件仍使用下表中的约定名称，这些 `.json` 配置文件本身支持注释。按内容对比合并，并保留目标中已有的本机设置和项目差异。

| 内容 | 位置 |
| --- | --- |
| 用户设置：`settings-user.jsonc` | 用户 `settings.json` |
| 项目设置：`settings-project-*.jsonc` | `.vscode/settings.json`，或多根工作区对应的设置层级 |
| 快捷键：`common/keybindings.jsonc` | 用户级 `keybindings.json`，不支持项目级 |
| 扩展推荐：`common/extensions.jsonc` | `.vscode/extensions.json`，或 `.code-workspace` 的 `extensions.recommendations` |
| 项目调试：`python/launch.jsonc` | `.vscode/launch.json` |
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
- Python 项目覆盖默认开启 pytest、关闭 unittest，使用 `${workspaceFolder}/tests/**/*.py` 在保存测试目录中的 Python 文件后触发重新发现；初始或手动测试发现及运行仍由 `python.testing.cwd` 和 `pytestArgs` 决定，原有参数不变。环境文件仍为 `${workspaceFolder}/.env`。
- 模板不固定 Python 解释器。通过 `Python: Select Interpreter` 选择项目环境；uv 的建环境和依赖安装通过终端执行，不由模板自动完成。
- 修改 `ruff.enable` 后，扩展可能提示重启 VS Code。拆分没有切换该值，统一默认中仍为 `true`。

### FastAPI 调试

`python/launch.jsonc` 保留 FastAPI、当前 Python 文件及当前测试文件三项调试配置。FastAPI 参数为：

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

`common/extensions.jsonc` 只表达团队推荐，不会自动安装、卸载扩展，也不影响设置继承。当前推荐列表保持不变：

| 类别 | 扩展 ID |
| --- | --- |
| 界面语言 | `ms-ceintl.vscode-language-pack-zh-hans` |
| 远程与容器 | `ms-vscode-remote.remote-containers`、`ms-vscode-remote.remote-ssh`、`ms-azuretools.vscode-containers`、`docker.docker` |
| Python | `ms-python.python`、`charliermarsh.ruff`、`ms-python.vscode-pylance` |
| 配置文件与接口 | `redhat.vscode-yaml`、`tamasfe.even-better-toml`、`bufbuild.vscode-buf`、`mikestead.dotenv` |
| 诊断与标记 | `usernamehw.errorlens`、`gruntfuggly.todo-tree` |
| 编辑辅助 | `oderwat.indent-rainbow`、`editorconfig.editorconfig` |
| 文档 | `davidanson.vscode-markdownlint`、`tomoki1207.pdf` |
| 系统状态 | `njzy.stats-bar` |
| 主题与图标 | `romanrei.material-dark`、`pkief.material-icon-theme`、`pkief.material-product-icons` |

Go 项目仍需单独安装 `golang.go`。Python 扩展配套的 Debugger 和 Environments 分别负责调试与环境管理；它们不是 Ruff、Pylance 的替代品。内置 Git 继续提供当前行 Blame、提交图、文件时间线、三方合并编辑器和 Worktree 检测，不重新引入已清理的 GitLens 等扩展。

可用 `code --list-extensions` 查看已安装扩展，在命令面板运行 `Extensions: Show Recommended Extensions` 查看推荐。Docker DX、Container Tools 和 Dev Containers 的职责不同，保留原有组合及 Docker DX Compose 服务关闭的设置。

## 验证

在仓库根目录运行：

```bash
python3 -B -m unittest tests/test_merge_vscode_settings.py
./development-config/vscode/apply-config.sh --generate-only
```

应用脚本和 JSONC 编辑器使用独立临时目标验证，运行：

```bash
uv run python -B -m unittest tests/test_apply_vscode_settings.py tests/test_merge_vscode_settings.py tests/test_vscode_entrypoint.py
uv run ruff check scripts/vscode tests/test_apply_vscode_settings.py tests/test_merge_vscode_settings.py tests/test_vscode_entrypoint.py
bash -n development-config/vscode/apply-config.sh
```

测试覆盖用户配置批量应用、额外设置与注释保留、项目目录必填、菜单预览与取消、后端布局、无测试项目、显式参数、错误输入、符号链接、幂等和目标变更保护；不会应用到测试机的真实用户配置或现有项目。

Go 应用测试覆盖预览、逐项保留、嵌套额外设置保留、重复应用、菜单确认、空路径与不存在路径；测试仅使用临时项目。

统一入口还覆盖从其他工作目录启动、仓库及项目路径包含空格、参数转发、只生成模式、帮助、缺少 uv、生成失败中止和应用退出状态传递。测试夹具使用独立的实现目录与配置目录。

测试分别验证“源模板显式配置值在合并后不变”和新增用户默认的跨项目继承，不把旧键的值相同当作完整有效配置相同。测试覆盖 Notebook、Makefile、Dockerfile 及另一种语言默认设置的新增继承，也验证项目可以覆盖这些偏好而保留同一对象中的其他默认项。自动发现模式的回归测试展开 `${workspaceFolder}` 后，在普通、带空格及隐藏父目录的临时工作区中执行文件系统 glob，检查测试目录直属、多层嵌套文件的匹配，并验证非 Python 文件、源码文件及其他测试目录不会误匹配；同时覆盖根目录和 `backend/` 两种测试布局。

此外，测试覆盖生成目标、用户与项目边界、嵌套对象和数组覆盖、选择性生成及保护用户/项目文件。这些是配置组合与生成流程的验证；已有项目的实际迁移仍应在目标 VS Code 窗口验证，生成成功不代表项目已应用。

## 参考资料

- [VS Code 设置优先级](https://code.visualstudio.com/docs/configure/settings#_settings-precedence)
- [全局调试配置](https://code.visualstudio.com/docs/debugtest/debugging-configuration#_global-launch-configuration)
- [Ruff 编辑器设置](https://docs.astral.sh/ruff/editors/settings/)
- [Go 扩展设置](https://github.com/golang/vscode-go/blob/master/docs/settings.md)
