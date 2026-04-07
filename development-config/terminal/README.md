# Terminal Configuration

Ghostty + Zsh + Starship 终端环境配置，支持 Ubuntu 和 macOS 快速部署。

## 目录结构

```text
terminal/
├── configs/                    # 配置文件
│   ├── environment.d/
│   │   └── input-method.conf   # Linux GUI 会话输入法环境变量
│   ├── ghostty.config          # Ghostty 终端配置
│   ├── starship.toml           # Starship 提示符配置
│   └── zshrc                   # Zsh + Oh My Zsh 配置
├── apply-config.sh             # 仓库 → 系统
└── scripts/                    # 其他脚本
    ├── install-ubuntu.sh       # Ubuntu 一键安装
    ├── install-macos.sh        # macOS 一键安装
    └── sync-config.sh          # 系统 → 仓库
```

## 快速开始

### 新机器安装

**Ubuntu:**

```bash
./scripts/install-ubuntu.sh
```

**macOS:**

```bash
./scripts/install-macos.sh
```

### 配置同步

**从仓库应用到系统：**

```bash
./apply-config.sh
```

**从系统同步到仓库：**

```bash
./scripts/sync-config.sh
```

## 组件说明

| 组件 | 说明 |
|------|------|
| [Ghostty](https://ghostty.org/) | GPU 加速终端模拟器 |
| [Zsh](https://www.zsh.org/) + [Oh My Zsh](https://ohmyz.sh/) | Shell 及插件框架 |
| [Starship](https://starship.rs/) | 跨 Shell 提示符（支持 Python/Node.js/Go/Rust/Docker） |
| [zoxide](https://github.com/ajeetdsouza/zoxide) | 智能目录跳转 |
| [fzf](https://github.com/junegunn/fzf) | 模糊搜索 |
| [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) | 命令自动补全 |
| [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) | 语法高亮 |

## 自定义

- **主题**: 修改 `configs/ghostty.config` 中的 `theme`，可用主题列表: `ghostty +list-themes`
- **字体**: 修改 `configs/ghostty.config` 中的 `font-family` 和 `font-size`
- **提示符**: 修改 `configs/starship.toml`，支持 Python/Node.js/Go/Rust/Docker 等语言版本显示
- **插件**: 修改 `configs/zshrc` 中的 `plugins=(...)`
- **编辑器**: `configs/zshrc` 默认使用 Neovim/Vim 作为编辑器
- **PATH**: `configs/zshrc` 自动添加 Homebrew/Go/Cargo 等常用路径
- **GUI 输入法环境**: 修改 `configs/environment.d/input-method.conf`，并在 Linux 上重新登录使其生效
