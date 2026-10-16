#!/bin/bash
# Ghostty + Zsh + Starship 快速安装脚本
# 适用于 Ubuntu 24.04
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"
GUI_ENV_SOURCE="$CONFIG_DIR/environment.d/input-method.conf"
GUI_ENV_DIR="$HOME/.config/environment.d"
GUI_ENV_TARGET="$GUI_ENV_DIR/input-method.conf"
echo "======================================"
echo "  Ghostty + Zsh + Starship 安装脚本"
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

# 检查是否为 Ubuntu
if ! grep -qi "ubuntu" /etc/os-release 2>/dev/null; then
    print_warning "此脚本针对 Ubuntu 优化，其他发行版可能需要手动调整"
fi

# ==================== 1. 安装基础依赖 ====================
echo ""
echo ">>> 安装基础依赖..."
sudo apt update
sudo apt install -y zsh git curl fzf

# ==================== 2. 安装 Oh My Zsh ====================
echo ""
echo ">>> 安装 Oh My Zsh..."
if [ -d "$HOME/.oh-my-zsh" ]; then
    print_status "Oh My Zsh 已安装，跳过"
else
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    print_status "Oh My Zsh 安装完成"
fi

# ==================== 3. 安装 Zsh 插件 ====================
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

# ==================== 4. 安装 Starship ====================
echo ""
echo ">>> 安装 Starship..."
if command -v starship &> /dev/null; then
    print_status "Starship 已安装: $(starship --version | head -1)"
else
    curl -sS https://starship.rs/install.sh | sh -s -- -y
    print_status "Starship 安装完成"
fi

# ==================== 5. 安装 zoxide ====================
echo ""
echo ">>> 安装 zoxide..."
if command -v zoxide &> /dev/null; then
    print_status "zoxide 已安装"
else
    curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
    print_status "zoxide 安装完成"
fi

# ==================== 6. 安装 Ghostty ====================
echo ""
echo ">>> 安装 Ghostty..."
if command -v ghostty &> /dev/null; then
    print_status "Ghostty 已安装: $(ghostty --version | head -1)"
else
    echo "从 GitHub 下载 Ghostty deb 包..."
    DEB_URL="https://github.com/mkasberg/ghostty-ubuntu/releases/download/1.3.1-0-ppa2/ghostty_1.3.1-0.ppa2_amd64_24.04.deb"
    curl -L -o /tmp/ghostty.deb "$DEB_URL"
    sudo dpkg -i /tmp/ghostty.deb || sudo apt install -f -y
    rm -f /tmp/ghostty.deb
    print_status "Ghostty 安装完成"
fi

# ==================== 7. 安装字体 ====================
echo ""
echo ">>> 安装 Nerd 字体..."
FONT_DIR="$HOME/.local/share/fonts"
mkdir -p "$FONT_DIR"

if [ -f "$FONT_DIR/MesloLGS NF Regular.ttf" ]; then
    print_status "MesloLGS NF 字体已安装"
else
    curl -fLo "$FONT_DIR/MesloLGS NF Regular.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf
    curl -fLo "$FONT_DIR/MesloLGS NF Bold.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold.ttf
    fc-cache -fv > /dev/null 2>&1
    print_status "MesloLGS NF 字体安装完成"
fi

# ==================== 8. 复制配置文件 ====================
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

if [ -f "$GUI_ENV_SOURCE" ]; then
    mkdir -p "$GUI_ENV_DIR"
    if [ -f "$GUI_ENV_TARGET" ]; then
        cp "$GUI_ENV_TARGET" "$GUI_ENV_TARGET.backup.$(date +%Y%m%d%H%M%S)"
        print_status "已备份 GUI 会话输入法环境配置"
    fi
    cp "$GUI_ENV_SOURCE" "$GUI_ENV_TARGET"
    print_status "已复制 GUI 会话输入法环境配置"
else
    print_warning "未找到 $GUI_ENV_SOURCE"
fi

# ==================== 9. 设置默认 Shell ====================
echo ""
echo ">>> 设置默认 Shell..."
if [ "$SHELL" != "$(which zsh)" ]; then
    chsh -s "$(which zsh)"
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
echo "  1. 注销并重新登录，使默认 Shell 生效"
echo "  2. 打开 Ghostty 终端"
echo "  3. 在 Ghostty 中优先选择 'MesloLGS NF' 字体，必要时回退到 'JetBrains Mono'"
echo "  4. GUI 应用的输入法环境也会在重新登录后生效"
echo ""
echo "已安装组件："
echo "  - Ghostty 深色终端配置"
echo "  - Zsh + Oh My Zsh + zsh-autosuggestions + zsh-syntax-highlighting"
echo "  - Starship 低噪声双行提示符"
echo "  - zoxide (按需启用)"
echo "  - fzf (模糊搜索)"
echo ""
echo "配置同步命令："
echo "  从仓库复制到系统: $SCRIPT_DIR/../apply-config.sh"
echo "  从系统同步到仓库: $SCRIPT_DIR/sync-config.sh"
echo ""
echo "配置文件目录: $CONFIG_DIR"
echo ""
