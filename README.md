# Docker Python 开发环境

基于 Docker 的 Python 多版本开发环境，使用 `uv` 管理 Python 版本和虚拟环境。

## 特性

- **多版本 Python**: 预装 Python 3.11.10 和 3.12.9，支持随时安装其他版本
- **uv 包管理**: 使用 uv 替代 pip，速度提升 10-100 倍
- **SSH 免密登录**: 支持从宿主机免密登录容器
- **Git SSH 支持**: 容器内可直接拉取/推送代码到远程仓库
- **共享网络**: 容器间使用 `common-network`，支持 `127.0.0.1` 互访
- **一键部署**: 提供跨平台自动化部署脚本

## 快速开始

### 前置条件

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 确保本机已生成 SSH 密钥：
   ```bash
   # 如果没有，先生成
   ssh-keygen -t rsa -b 4096
   ```

### 一键部署

**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

脚本会自动完成：
1. 检查 Docker 环境
2. 检查并复制 SSH 密钥
3. 设置私钥权限
4. 构建 Docker 镜像
5. 启动服务

## 服务列表

| 服务 | 容器名 | 端口映射 | 说明 |
|-----|-------|---------|------|
| dev-env | dev-env | 10022→22, 8000-8090 | Python 开发环境 |
| redis | redis | 6379→6379 | Redis 缓存服务 |

## 连接方式

### SSH 连接容器

```bash
# 免密登录（推荐）
ssh -i ./ssh-keys/id_rsa root@localhost -p 10022

# 密码登录（密码: 123456）
ssh root@localhost -p 10022
```

### 进入容器

```bash
docker exec -it dev-env bash
```

### Redis 连接

```bash
redis-cli -h localhost -p 6379 -a 123456
```

## Python 版本管理

容器内使用 `uv` 管理 Python 版本：

```bash
# 查看已安装的 Python 版本
uv python list

# 安装新版本
uv python install 3.13

# 切换默认版本
uv python pin 3.12.9
```

## 项目开发

### 创建虚拟环境

```bash
# 使用默认 Python 版本
uv venv

# 指定 Python 版本
uv venv --python 3.12.9
```

### 安装依赖

```bash
# 安装单个包
uv pip install requests

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 使用 uv sync（推荐）
uv sync
```

### 运行脚本

```bash
# 无需激活虚拟环境
uv run python script.py

# 指定 Python 版本运行
uv run --python 3.11.10 python script.py
```

## 目录结构

```
docker-venv/
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # 服务编排配置
├── scripts/                # 脚本目录
├── setup.ps1               # Windows 一键部署脚本
├── setup.sh                # Linux/Mac 一键部署脚本
├── scripts/                # 脚本目录
│   └── entrypoint.sh       # 容器入口脚本
├── ssh-keys/               # SSH 密钥目录
│   ├── copy-ssh-keys.ps1   # Windows 密钥复制脚本
│   ├── copy-ssh-keys.sh    # Linux/Mac 密钥复制脚本
│   └── README.md           # SSH 使用说明
└── infras/                 # 基础设施配置
    ├── redis/              # Redis 配置和数据
    └── mysql/              # MySQL 配置和数据
```

## 常用命令

### Docker 操作

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker logs dev-env
```

### 容器内操作

```bash
# 查看 Python 版本
uv python list

# 初始化新项目
uv init my-project

# 添加依赖
uv add requests pandas

# 运行项目
uv run python main.py
```

## 网络配置

所有服务使用 `common-network` 桥接网络：

- 容器间可使用服务名互访：`redis:6379`
- 宿主机通过映射端口访问：`localhost:6379`

## 环境变量

| 变量 | 值 | 说明 |
|-----|---|------|
| TZ | UTC | 时区 |
| UV_PYTHON_INSTALL_DIR | /opt/python | Python 安装目录 |
| UV_INDEX_URL | mirrors.aliyun.com | PyPI 镜像源 |

## 故障排查

### SSH 连接失败

```bash
# 检查容器日志
docker logs dev-env

# 确认 SSH 服务状态
docker exec dev-env ss -lnt | grep 22
```

### 私钥权限问题 (Windows)

```powershell
# 重新设置权限
icacls .\ssh-keys\id_rsa /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

### 镜像构建失败

```bash
# 清理缓存重新构建
docker-compose build --no-cache
```

## 参考资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [Docker 文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
