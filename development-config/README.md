# Development Config

> 个人开发环境配置集合，用于在不同机器和项目之间复用编辑器、终端和 AI assistant 配置。

本目录保存开发工具链相关配置，不承载具体业务代码。各子目录按工具或场景拆分，并在目录内维护更详细的使用说明。

## 目录结构

```text
development-config/
├── ai-assistants/   # Codex、Qoder 等 AI assistant 的 rules、skills 和配置
├── terminal/        # Ghostty、Zsh、Starship 等终端环境配置
├── vscode/          # VS Code 通用、Python、Go 工作区配置
└── README.md
```

## 模块说明

| 目录 | 用途 | 详细文档 |
| ---- | ---- | -------- |
| `ai-assistants/` | 同步 AI assistant 规则、skills 和 Codex 配置 | [`ai-assistants/README.md`](ai-assistants/README.md) |
| `terminal/` | 安装和同步终端、Shell、提示符配置 | [`terminal/README.md`](terminal/README.md) |
| `vscode/` | 维护 VS Code 通用配置和语言专用配置 | [`vscode/README.md`](vscode/README.md) |

## 常用入口

### AI Assistant 配置

```bash
./development-config/ai-assistants/apply_agengts.sh
```

可交互选择同步 `rules`、`skills` 或 `codex-config`。选择 Qoder rules 时，需要输入已存在且以 `.qoder` 结尾的项目目录。

### Terminal 配置

```bash
./development-config/terminal/apply-config.sh
```

将仓库中的终端配置应用到当前系统。新机器安装和反向同步脚本见 `terminal/scripts/`。

### VS Code 配置

```bash
cp -r development-config/vscode/common/* .vscode/
cp development-config/vscode/python/* .vscode/
```

按项目语言选择复制 `python/` 或 `golang/` 下的配置。需要合并配置时，优先参考 `vscode/README.md` 中的说明。

## 维护原则

- 子目录内的 README 是具体使用说明的唯一权威来源。
- 新增工具配置时，优先新建独立子目录，并补充对应 README。
- 修改配置同步脚本时，应同时更新相关文档和最小可行验证命令。
- 不在本目录存放机器私有密钥、token、cookie 或其他敏感信息。
