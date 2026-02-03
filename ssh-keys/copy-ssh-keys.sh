#!/bin/bash
################################################################################
# 复制SSH密钥脚本 - Linux/Mac版本
################################################################################
#
# 功能: 将当前用户的SSH密钥复制到当前目录
# 用法: ./copy-ssh-keys.sh
#

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_SOURCE_DIR="${HOME}/.ssh"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSH密钥复制工具 (Linux/Mac)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查源目录是否存在
if [ ! -d "$SSH_SOURCE_DIR" ]; then
    echo -e "${RED}错误: SSH目录不存在: $SSH_SOURCE_DIR${NC}"
    echo -e "${YELLOW}请先生成SSH密钥: ssh-keygen -t rsa -b 4096${NC}"
    exit 1
fi

echo -e "${YELLOW}源目录: $SSH_SOURCE_DIR${NC}"
echo -e "${YELLOW}目标目录: $SCRIPT_DIR${NC}"
echo ""

# 列出将要复制的文件
echo "将复制以下文件:"
ls -lh "$SSH_SOURCE_DIR" 2>/dev/null | grep -E "^-" || echo "  (无文件)"
echo ""

# 询问确认
read -p "确认复制? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

# 复制文件
echo -e "${GREEN}开始复制...${NC}"

# 复制常见的SSH文件
files_to_copy=("id_rsa" "id_rsa.pub" "id_ed25519" "id_ed25519.pub" "config" "known_hosts" "known_hosts.old")
copied_count=0

for file in "${files_to_copy[@]}"; do
    if [ -f "$SSH_SOURCE_DIR/$file" ]; then
        cp "$SSH_SOURCE_DIR/$file" "$SCRIPT_DIR/" 2>/dev/null && {
            echo -e "  ${GREEN}✓${NC} 已复制: $file"
            copied_count=$((copied_count + 1))
        } || {
            echo -e "  ${RED}✗${NC} 复制失败: $file"
        }
    fi
done

echo ""
if [ $copied_count -eq 0 ]; then
    echo -e "${YELLOW}警告: 没有找到任何SSH密钥文件${NC}"
    echo -e "${YELLOW}建议生成新密钥: ssh-keygen -t rsa -b 4096 -f $SCRIPT_DIR/id_rsa${NC}"
else
    echo -e "${GREEN}✓ 成功复制 $copied_count 个文件${NC}"
    echo ""
    echo -e "${YELLOW}提示:${NC}"
    echo "  1. 这些密钥文件已被 .gitignore 排除，不会提交到Git"
    echo "  2. 私钥文件(id_rsa)包含敏感信息，请妥善保管"
    echo "  3. 可以使用以下命令连接到容器:"
    echo "     ssh -i $SCRIPT_DIR/id_rsa root@localhost -p 10022"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  操作完成${NC}"
echo -e "${GREEN}========================================${NC}"
