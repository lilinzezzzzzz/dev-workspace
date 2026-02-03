#!/bin/bash
set -e

# 处理 SSH 密钥
SSH_DIR="/root/.ssh"
HOST_SSH_DIR="/tmp/host-ssh"

# 复制私钥（用于从容器连接 Git/其他服务器）
if [ -f "$HOST_SSH_DIR/id_rsa" ]; then
    cp "$HOST_SSH_DIR/id_rsa" "$SSH_DIR/id_rsa"
    chmod 600 "$SSH_DIR/id_rsa"
    echo "[SSH] 私钥已配置"
fi

# 复制公钥并生成 authorized_keys（用于免密登录容器）
if [ -f "$HOST_SSH_DIR/id_rsa.pub" ]; then
    cp "$HOST_SSH_DIR/id_rsa.pub" "$SSH_DIR/id_rsa.pub"
    cp "$HOST_SSH_DIR/id_rsa.pub" "$SSH_DIR/authorized_keys"
    chmod 644 "$SSH_DIR/id_rsa.pub"
    chmod 600 "$SSH_DIR/authorized_keys"
    echo "[SSH] 公钥已配置，已启用免密登录"
fi

# 复制 SSH 配置文件（可选）
if [ -f "$HOST_SSH_DIR/config" ]; then
    cp "$HOST_SSH_DIR/config" "$SSH_DIR/config"
    chmod 600 "$SSH_DIR/config"
    echo "[SSH] 配置文件已复制"
fi

# 复制 known_hosts（可选）
if [ -f "$HOST_SSH_DIR/known_hosts" ]; then
    cp "$HOST_SSH_DIR/known_hosts" "$SSH_DIR/known_hosts"
    chmod 644 "$SSH_DIR/known_hosts"
    echo "[SSH] known_hosts 已复制"
fi

echo "[SSH] 配置完成"

# 启动 sshd
exec /usr/sbin/sshd -D -e
