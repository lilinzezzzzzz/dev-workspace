#!/bin/bash
# Ghostty + Zsh + Starship 快速安装脚本
# 适用于 macOS
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"
echo "======================================"
echo "  Ghostty + Zsh + Starship 安装脚本"
echo "           (macOS 版本)"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 检查是否为 macOS
if [[ "$(uname)" != "Darwin" ]]; then
    print_error "此脚本仅适用于 macOS"
    echo "如果你使用的是 Ubuntu，请运行 install.sh"
    exit 1
fi

# ==================== 1. 安装 Homebrew ====================
echo ""
echo ">>> 检查 Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # 添加 Homebrew 到 PATH (Apple Silicon)
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    print_status "Homebrew 安装完成"
else
    print_status "Homebrew 已安装"
fi

# ==================== 2. 安装基础依赖 ====================
echo ""
echo ">>> 安装基础依赖..."
brew install git curl fzf

# ==================== 3. 安装 Oh My Zsh ====================
echo ""
echo ">>> 安装 Oh My Zsh..."
# macOS 自带 Zsh，无需额外安装
if [ -d "$HOME/.oh-my-zsh" ]; then
    print_status "Oh My Zsh 已安装，跳过"
else
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    print_status "Oh My Zsh 安装完成"
fi

# ==================== 4. 安装 Zsh 插件 ====================
echo ""
echo ">>> 安装 Zsh 插件..."

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

# zsh-autosuggestions
if [ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    print_status "zsh-autosuggestions 已安装"
else
    git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
    print_status "zsh-autosuggestions 安装完成"
fi

# zsh-syntax-highlighting
if [ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    print_status "zsh-syntax-highlighting 已安装"
else
    git clone https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
    print_status "zsh-syntax-highlighting 安装完成"
fi

# ==================== 5. 安装 Starship ====================
echo ""
echo ">>> 安装 Starship..."
if command -v starship &> /dev/null; then
    print_status "Starship 已安装: $(starship --version | head -1)"
else
    brew install starship
    print_status "Starship 安装完成"
fi

# ==================== 6. 安装 zoxide ====================
echo ""
echo ">>> 安装 zoxide..."
if command -v zoxide &> /dev/null; then
    print_status "zoxide 已安装"
else
    brew install zoxide
    print_status "zoxide 安装完成"
fi

# ==================== 7. 安装 Ghostty ====================
echo ""
echo ">>> 安装 Ghostty..."
if [ -d "/Applications/Ghostty.app" ] || command -v ghostty &> /dev/null; then
    print_status "Ghostty 已安装"
else
    # Ghostty 可通过 Homebrew Cask 安装
    brew install --cask ghostty
    print_status "Ghostty 安装完成"
fi

# ==================== 8. 安装字体 ====================
echo ""
echo ">>> 安装 Nerd 字体..."
# 通过 Homebrew 安装字体
if brew list --cask font-meslo-lg-nerd-font &> /dev/null 2>&1; then
    print_status "MesloLGS NF 字体已安装"
else
    brew tap homebrew/cask-fonts 2>/dev/null || true
    brew install --cask font-meslo-lg-nerd-font
    print_status "MesloLGS NF 字体安装完成"
fi

# ==================== 9. 复制配置文件 ====================
echo ""
echo ">>> 复制配置文件..."

# 备份原有配置
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%Y%m%d%H%M%S)"
    print_status "已备份原 .zshrc"
fi

# 复制配置
cp "$CONFIG_DIR/zshrc" "$HOME/.zshrc"
print_status "已复制 .zshrc"

mkdir -p "$HOME/.config/ghostty"
cp "$CONFIG_DIR/ghostty.config" "$HOME/.config/ghostty/config"
print_status "已复制 Ghostty 配置"

mkdir -p "$HOME/.config"
cp "$CONFIG_DIR/starship.toml" "$HOME/.config/starship.toml"
print_status "已复制 Starship 配置"

# ==================== 10. 设置默认 Shell ====================
echo ""
echo ">>> 检查默认 Shell..."
# macOS 自带 Zsh 且默认就是 Zsh (从 Catalina 开始)
if [ "$SHELL" != "/bin/zsh" ]; then
    chsh -s /bin/zsh
    print_status "默认 Shell 已设置为 Zsh"
else
    print_status "默认 Shell 已经是 Zsh"
fi

# ==================== 完成 ====================
echo ""
echo "======================================"
echo -e "${GREEN}  安装完成！${NC}"
echo "======================================"
echo ""
echo "后续步骤："
echo "  1. 重新打开终端或运行 'source ~/.zshrc'"
echo "  2. 打开 Ghostty 应用 (在 Applications 中)"
echo "  3. 在 Ghostty 设置中优先选择 'MesloLGS NF' 字体，必要时回退到 'JetBrains Mono'"
echo ""
echo "已安装组件："
echo "  - Ghostty 深色终端配置"
echo "  - Zsh + Oh My Zsh + zsh-autosuggestions + zsh-syntax-highlighting"
echo "  - Starship 低噪声双行提示符"
echo "  - zoxide (按需启用)"
echo "  - fzf (模糊搜索)"
echo ""
echo "提示：如果 Homebrew 命令找不到，请运行："
echo '  eval "$(/opt/homebrew/bin/brew shellenv)"  # Apple Silicon'
echo '  eval "$(/usr/local/bin/brew shellenv)"     # Intel Mac'
echo ""
echo "配置同步命令："
echo "  从仓库复制到系统: $SCRIPT_DIR/apply-config.sh"
echo "  从系统同步到仓库: $SCRIPT_DIR/sync-config.sh"
echo ""
echo "配置文件目录: $CONFIG_DIR"
echo ""
