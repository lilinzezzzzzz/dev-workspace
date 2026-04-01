#!/bin/bash
# 应用配置脚本
# 将仓库中的配置复制到系统对应位置
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo "======================================"
echo "       应用配置脚本"
echo "======================================"
echo ""
echo "将以下配置从仓库复制到系统:"
echo "  $CONFIG_DIR/zshrc           -> ~/.zshrc"
echo "  $CONFIG_DIR/ghostty.config  -> ~/.config/ghostty/config"
echo "  $CONFIG_DIR/starship.toml   -> ~/.config/starship.toml"
echo ""

# 备份并复制 zshrc
if [ -f "$CONFIG_DIR/zshrc" ]; then
    if [ -f "$HOME/.zshrc" ]; then
        cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%Y%m%d%H%M%S)"
        print_status "已备份 ~/.zshrc"
    fi
    cp "$CONFIG_DIR/zshrc" "$HOME/.zshrc"
    print_status "已复制 .zshrc"
else
    print_warning "未找到 $CONFIG_DIR/zshrc"
fi

# 复制 Ghostty 配置
if [ -f "$CONFIG_DIR/ghostty.config" ]; then
    mkdir -p "$HOME/.config/ghostty"
    cp "$CONFIG_DIR/ghostty.config" "$HOME/.config/ghostty/config"
    print_status "已复制 Ghostty 配置"
    
    # macOS: 重启 Ghostty 使配置生效
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if pgrep -x "ghostty" > /dev/null; then
            read -p "是否重启 Ghostty 使配置生效? [Y/n]: " restart_ghostty
            if [[ ! "$restart_ghostty" =~ ^[Nn]$ ]]; then
                killall ghostty 2>/dev/null
                sleep 0.5
                open -a Ghostty
                print_status "已重启 Ghostty"
            fi
        fi
    fi
else
    print_warning "未找到 $CONFIG_DIR/ghostty.config"
fi

# 复制 Starship 配置
if [ -f "$CONFIG_DIR/starship.toml" ]; then
    mkdir -p "$HOME/.config"
    cp "$CONFIG_DIR/starship.toml" "$HOME/.config/starship.toml"
    print_status "已复制 Starship 配置"
else
    print_warning "未找到 $CONFIG_DIR/starship.toml"
fi

echo ""
echo "======================================"
echo -e "${GREEN}  配置已应用！${NC}"
echo "======================================"
echo ""

# 询问是否重启 shell
read -p "是否重新加载 shell 使配置生效? [Y/n]: " reload_choice

if [[ ! "$reload_choice" =~ ^[Nn]$ ]]; then
    echo "重新加载 zsh..."
    exec zsh
else
    echo "请手动运行以下命令使配置生效:"
    echo "  source ~/.zshrc"
    echo ""
fi
