# SSH密钥使用示例

## 目录说明

此目录包含用于容器SSH连接的密钥文件：

- `id_ed25519` - SSH私钥 (推荐)
- `id_ed25519.pub` - SSH公钥
- `id_rsa` - SSH私钥 (兼容旧系统)
- `id_rsa.pub` - SSH公钥
- `config` - SSH配置文件
- `known_hosts` - 已知主机列表

## 快速开始

### 使用自动化脚本复制密钥（推荐）

我们提供了跨平台的脚本来自动复制SSH密钥：

**Windows系统:**
```powershell
# 在 ssh-keys 目录下执行
.\copy-ssh-keys.ps1
```

**Linux/Mac系统:**
```bash
# 在 ssh-keys 目录下执行
chmod +x copy-ssh-keys.sh
./copy-ssh-keys.sh
```

脚本会自动：
- 检查 `~/.ssh` 目录是否存在
- 列出将要复制的文件
- 请求确认后复制密钥文件
- 显示操作结果和使用提示

## 使用方法

### 1. 生成新的SSH密钥对（推荐）

如果是首次使用或需要为容器生成专用密钥，在当前目录执行：

```bash
# 生成新的SSH密钥对 (推荐 ED25519)
ssh-keygen -t ed25519 -f ./id_ed25519 -N "" -C "docker-container"

# Windows PowerShell 中执行
ssh-keygen -t ed25519 -f ".\id_ed25519" -N '""' -C "docker-container"

# 兼容旧系统可使用 RSA
ssh-keygen -t rsa -b 4096 -f ./id_rsa -N "" -C "docker-container"
```

### 2. 复制现有密钥

如果要使用主机的SSH密钥：

```bash
# Linux/Mac (推荐 ED25519)
cp ~/.ssh/id_ed25519* ./
# 或复制 RSA 密钥
cp ~/.ssh/id_rsa* ./

# Windows PowerShell (推荐 ED25519)
Copy-Item -Path "$env:USERPROFILE\.ssh\id_ed25519*" -Destination ".\" -Force
# 或复制 RSA 密钥
Copy-Item -Path "$env:USERPROFILE\.ssh\id_rsa*" -Destination ".\" -Force
```

### 3. 连接到容器

容器启动后，使用SSH连接：

```bash
# 使用 ED25519 密钥连接（端口10022，推荐）
ssh -i ./id_ed25519 root@localhost -p 10022

# 或使用 RSA 密钥连接
ssh -i ./id_rsa root@localhost -p 10022

# 或使用密码连接（密码见 .env 的 PYTHON_WORKSPACE_ROOT_PASSWORD）
ssh root@localhost -p 10022
```

### 4. 配置免密登录

将公钥添加到目标服务器：

```bash
# 复制 ED25519 公钥到目标服务器（推荐）
ssh-copy-id -i ./id_ed25519.pub -p 10022 root@localhost

# 或复制 RSA 公钥
ssh-copy-id -i ./id_rsa.pub -p 10022 root@localhost

# 或手动添加
cat ./id_ed25519.pub | ssh -p 10022 root@localhost "cat >> ~/.ssh/authorized_keys"
```

## 权限说明

容器启动时会自动设置正确的权限：

- `.ssh/` 目录: 700
- 私钥文件: 600
- 公钥文件: 644
- `authorized_keys`: 600

## 安全建议

1. **不要提交私钥到Git仓库**
   - 在 `.gitignore` 中添加 `ssh-keys/id_ed25519` 和 `ssh-keys/id_rsa`

2. **使用专用密钥**
   - 为容器生成独立的密钥对，不要使用个人主密钥

3. **定期轮换密钥**
   - 建议每3-6个月更换一次SSH密钥

4. **限制密钥权限**
   - 确保私钥文件权限为600（仅所有者可读写）

## 故障排查

### 连接被拒绝

```bash
# 检查容器SSH服务状态
docker exec python-venv ps aux | grep sshd

# 查看SSH日志
docker logs python-venv
```

### 权限错误

```bash
# 重新设置密钥权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
# 如果使用 RSA
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### 密钥不匹配

确保 `id_ed25519.pub` 或 `id_rsa.pub` 的内容已添加到目标服务器的 `~/.ssh/authorized_keys` 文件中。
