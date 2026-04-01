#!/bin/bash
# 配置同步脚本
# 将当前系统的终端配置同步回仓库目录
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
echo "       配置同步脚本"
echo "======================================"
echo ""
echo "将以下配置同步到: $CONFIG_DIR"
echo "  - ~/.zshrc"
echo "  - ~/.config/ghostty/config"
echo "  - ~/.config/starship.toml"
echo ""

# 同步 zshrc
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$CONFIG_DIR/zshrc"
    print_status "已同步 .zshrc"
else
    print_warning "未找到 ~/.zshrc"
fi

# 同步 Ghostty 配置
if [ -f "$HOME/.config/ghostty/config" ]; then
    cp "$HOME/.config/ghostty/config" "$CONFIG_DIR/ghostty.config"
    print_status "已同步 Ghostty 配置"
else
    print_warning "未找到 ~/.config/ghostty/config"
fi

# 同步 Starship 配置
if [ -f "$HOME/.config/starship.toml" ]; then
    cp "$HOME/.config/starship.toml" "$CONFIG_DIR/starship.toml"
    print_status "已同步 Starship 配置"
else
    print_warning "未找到 ~/.config/starship.toml"
fi

echo ""
echo "======================================"
echo -e "${GREEN}  同步完成！${NC}"
echo "======================================"
echo ""
echo "配置文件已保存到:"
echo "  $CONFIG_DIR/"
echo ""
echo "别忘了提交更改到 Git:"
echo "  git add $CONFIG_DIR/"
echo "  git commit -m 'chore(terminal): 更新终端配置'"
echo ""
