#!/bin/bash
################################################################################
# 一键部署开发环境 - Linux/Mac 版本
################################################################################
#
# 功能: 自动完成 SSH 密钥检查、Docker 构建和服务启动
# 用法: ./setup.sh
#

set -e

# 颜色定义
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m'

# 输出函数
print_step() {
    echo -e "\n${CYAN}[→] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Python 开发环境一键部署${NC}"
echo -e "${GREEN}========================================${NC}"

# ============================================================
# 步骤 1: 检查 Docker 环境
# ============================================================
print_step "检查 Docker 环境..."

if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装"
    echo -e "${YELLOW}请先安装 Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

docker_version=$(docker --version 2>&1)
print_success "Docker 已安装: $docker_version"

if ! docker compose version &> /dev/null; then
    print_error "Docker Compose 未安装"
    exit 1
fi

compose_version=$(docker compose version 2>&1)
print_success "Docker Compose 已安装: $compose_version"

# ============================================================
# 步骤 2: 检查 SSH 密钥
# ============================================================
print_step "检查 SSH 密钥..."

SSH_SOURCE_DIR="$HOME/.ssh"
SSH_TARGET_DIR="$SCRIPT_DIR/ssh-keys"
RSA_KEY="$SSH_SOURCE_DIR/id_rsa"
ED25519_KEY="$SSH_SOURCE_DIR/id_ed25519"

if [ ! -f "$ED25519_KEY" ] && [ ! -f "$RSA_KEY" ]; then
    print_error "未找到 SSH 密钥文件"
    echo ""
    echo -e "${YELLOW}请先生成 SSH 密钥:${NC}"
    echo "  ssh-keygen -t ed25519"
    echo "  或"
    echo "  ssh-keygen -t rsa -b 4096"
    exit 1
fi

print_success "检测到 SSH 密钥"

# ============================================================
# 步骤 3: 复制 SSH 密钥
# ============================================================
print_step "复制 SSH 密钥到项目目录..."

# 确保目标目录存在
mkdir -p "$SSH_TARGET_DIR"

# 复制密钥文件
files_to_copy=("id_rsa" "id_rsa.pub" "id_ed25519" "id_ed25519.pub")
copied_count=0

for file in "${files_to_copy[@]}"; do
    source_file="$SSH_SOURCE_DIR/$file"
    if [ -f "$source_file" ]; then
        cp "$source_file" "$SSH_TARGET_DIR/"
        echo -e "  ${GRAY}已复制: $file${NC}"
        copied_count=$((copied_count + 1))
    fi
done

if [ $copied_count -eq 0 ]; then
    print_error "没有复制任何密钥文件"
    exit 1
fi

print_success "已复制 $copied_count 个密钥文件"

# ============================================================
# 步骤 4: 设置私钥权限
# ============================================================
print_step "设置私钥文件权限..."

private_keys=("id_rsa" "id_ed25519")
for key in "${private_keys[@]}"; do
    key_path="$SSH_TARGET_DIR/$key"
    if [ -f "$key_path" ]; then
        chmod 600 "$key_path"
        echo -e "  ${GRAY}已设置权限: $key${NC}"
    fi
done

print_success "私钥权限设置完成"

# ============================================================
# 步骤 5: 构建 Docker 镜像
# ============================================================
print_step "构建 Docker 镜像 (可能需要几分钟)..."

if docker compose build --no-cache 2>&1 | while read line; do echo -e "  ${GRAY}$line${NC}"; done; then
    print_success "Docker 镜像构建完成"
else
    print_error "Docker 镜像构建失败"
    exit 1
fi

# ============================================================
# 步骤 6: 启动服务
# ============================================================
print_step "启动服务..."

if docker compose up -d 2>&1 | while read line; do echo -e "  ${GRAY}$line${NC}"; done; then
    print_success "服务启动完成"
else
    print_error "服务启动失败"
    exit 1
fi

# ============================================================
# 步骤 7: 等待健康检查
# ============================================================
print_step "等待服务就绪..."

sleep 5

docker compose ps --format "table {{.Name}}\t{{.Status}}" | while read line; do
    if echo "$line" | grep -q "running\|Up"; then
        echo -e "  ${GREEN}✓ $line${NC}"
    else
        echo -e "  ${GRAY}$line${NC}"
    fi
done

# ============================================================
# 完成
# ============================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}连接方式:${NC}"
echo "  SSH 免密登录:  ssh -i ./ssh-keys/id_ed25519 root@localhost -p 10022"
echo "  SSH 密码登录:  ssh root@localhost -p 10022  (密码: 123456)"
echo "  进入容器:      docker exec -it python-workspace bash"
echo ""
echo -e "${CYAN}Redis 连接:${NC}"
echo "  redis-cli -h localhost -p 6379 -a 123456"
echo ""
