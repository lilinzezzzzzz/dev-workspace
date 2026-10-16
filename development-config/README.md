# Development Config

> 个人开发环境配置集合，用于在不同机器和项目之间复用编辑器和终端配置。

本目录保存开发工具链相关配置，不承载具体业务代码。各子目录按工具或场景拆分，并在目录内维护更详细的使用说明。AI assistant 配置已迁移到独立项目 `agent-workbench`。

## 目录结构

```text
development-config/
├── terminal/        # Ghostty、Zsh、Starship 等终端环境配置
├── vscode/          # VS Code 通用、Python、Go 工作区配置
└── README.md
```

## 模块说明

| 目录 | 用途 | 详细文档 |
| ---- | ---- | -------- |
| `terminal/` | 安装和同步终端、Shell、提示符配置 | [`terminal/README.md`](terminal/README.md) |
| `vscode/` | 维护 VS Code 通用配置和语言专用配置 | [`vscode/README.md`](vscode/README.md) |

## 常用入口

### Terminal 配置

```bash
./development-config/terminal/apply-config.sh
```

将仓库中的终端配置应用到当前系统。新机器安装和反向同步脚本见 `terminal/scripts/`。

### VS Code 配置

在仓库根目录生成统一用户默认设置和项目覆盖：

```bash
uv sync --locked
./development-config/vscode/apply-config.sh
```

本地脚本开发环境使用 Python 3.14。统一入口无参数启动时先选择是否生成配置，再提供 Python（默认）、Go 或用户配置菜单；项目模式必须输入项目根目录，预览后确认写入。只生成时使用 `apply-config.sh --generate-only`。Python 实现集中在 `scripts/vscode/`，入口从任意工作目录调用都会使用本仓库的 uv 环境。三种配置都先统计并展示全部变更，再选择全部应用（默认）、逐项处理或取消，最后统一确认写入（回车默认写入，`n` 不写入）；本机额外设置保留。源模板统一使用 `.jsonc`；实际应用的用户和项目配置仍保留 `settings.json`、`launch.json`、`extensions.json`、`keybindings.json` 等约定文件名。具体合并方式和适用范围见 [`vscode/README.md`](vscode/README.md)。

## 维护原则

- 子目录内的 README 是具体使用说明的唯一权威来源。
- 新增工具配置时，优先新建独立子目录，并补充对应 README。
- 修改配置同步脚本时，应同时更新相关文档和最小可行验证命令。
- 不在本目录存放机器私有密钥、token、cookie 或其他敏感信息。
- AI assistant rules、skills 和 Codex/Qoder 同步入口由独立项目
  `agent-workbench` 维护，不在本仓库继续维护副本。
