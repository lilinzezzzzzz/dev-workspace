# dev-workspace

基于 Docker 的本地开发工作区，包含一个可通过 SSH 进入的 Python 开发容器，以及常用的本地基础设施服务。

当前仓库重点覆盖三类内容：

- `python-workspace` 开发容器：Debian Bookworm + `uv` + 多版本 Python
- 本地基础设施：Redis、MySQL、Milvus、Attu
- 开发工具配置：VS Code、AI assistants、提示词与 SSH 密钥说明

## 当前服务

`docker-compose.yml` 当前定义了以下服务：

| 服务 | 容器名 | 默认端口 | 说明 |
| --- | --- | --- | --- |
| `python-workspace` | `python-workspace` | `10022`、`8000-8099` | Python 开发容器，按 `python-workspace` profile 启动 |
| `redis` | `redis` | `6379` | Redis 6，密码由 `.env` 配置 |
| `mysql` | `mysql` | `3306` | MySQL 8，root 密码由 `.env` 配置 |
| `postgres` | `postgres` | `5432` | PostgreSQL 17，按 `jsontype-postgres` profile 启动，用于 `JSONType` 方言测试 |
| `oracle` | `oracle` | `1521` | Oracle Database Free，按 `jsontype-oracle` profile 启动，用于 `JSONType` 方言测试 |
| `milvus-etcd` | `milvus-etcd` | - | Milvus 依赖组件 |
| `milvus-minio` | `milvus-minio` | - | Milvus 对象存储 |
| `milvus-standalone` | `milvus-standalone` | `19530`、`9091` | Milvus 单机版 |
| `attu` | `attu` | `18000` | Milvus 可视化管理界面 |

## 开发容器能力

`Dockerfile` 当前提供：

- 基础镜像：`debian:bookworm-slim`
- Python 管理：`uv`
- 预装 Python：`3.11.10`、`3.12.9`
- 默认 pinned Python：`3.11.10`
- SSH 服务：容器内启用 `sshd`
- APT / PyPI 镜像：阿里云镜像
- 系统包策略：构建时执行安全更新，并仅安装开发容器实际需要的工具

容器内关键环境变量：

| 变量 | 值 |
| --- | --- |
| `TZ` | `Etc/UTC` |
| `UV_PYTHON_INSTALL_DIR` | `/opt/python` |
| `UV_PYTHON_PREFERENCE` | `only-managed` |
| `UV_INDEX_URL` | `https://mirrors.aliyun.com/pypi/simple` |

## 快速开始

### 前置条件

1. 安装 Docker / Docker Desktop
2. 本机已有 SSH 密钥：`~/.ssh/id_rsa` 或 `~/.ssh/id_ed25519`

如果没有密钥，可先执行：

```bash
ssh-keygen -t rsa -b 4096
```

首次部署先创建环境文件，并将其中所有占位值替换为强密码：

```bash
cp .env.example .env
```

`.env` 不纳入版本控制。Compose 会校验全部密码变量均已配置；即使只启动部分
profile，也需要保留 `.env.example` 中列出的所有变量。

数据库镜像通常只在首次初始化数据目录时读取初始化密码。已有 MySQL、PostgreSQL
或 Oracle 数据时，仅修改 `.env` 不会自动轮换库内密码；需要在数据库内单独修改，
或在确认不需要旧数据后重新初始化对应存储。

### 一键脚本

Windows：

```powershell
.\setup.ps1
```

Linux / macOS：

```bash
chmod +x setup.sh
./setup.sh
```

### 启动说明

需要注意，当前仓库里 `python-workspace` 服务被放在 `python-workspace` profile 下：

- `setup.ps1` 会用 `--profile python-workspace` 启动开发容器和基础设施
- `setup.sh` 当前只执行 `docker compose up -d`，因此默认只会启动非 profile 服务，不会启动 `python-workspace`

如果你在 Linux / macOS 上需要启动开发容器，请额外执行：

```bash
docker compose --profile python-workspace up -d
```

如果只想启动基础设施：

```bash
docker compose up -d
```

如果需要连同开发容器一起启动：

```bash
docker compose --profile python-workspace up -d
```

如果需要做 `JSONType` 的跨数据库方言验证，可按需启动额外数据库：

```bash
docker compose --profile jsontype-postgres up -d postgres
docker compose --profile jsontype-oracle up -d oracle
```

如果需要同时拉起两个专项测试库：

```bash
docker compose --profile jsontype-postgres --profile jsontype-oracle up -d postgres oracle
```

说明：

- PostgreSQL 当前定位为 `JSONType` 方言专项测试容器；`ai-service` 的配置层还不能直接切到 PostgreSQL 运行整套应用
- Oracle Free 镜像首次启动较慢，镜像和 named volume 都比较大
- Oracle 当前使用 Docker named volume 持久化数据，避免宿主机 bind mount 权限导致初始化失败

## 常用连接方式

### 进入开发容器

```bash
docker exec -it python-workspace bash
```

### SSH 连接开发容器

```bash
ssh root@localhost -p 10022
```

登录密码读取自 `.env` 中的 `PYTHON_WORKSPACE_ROOT_PASSWORD`。密码在容器启动时
设置，不会写入 Docker 镜像层。

说明：

- 当前 `docker-compose.yml` 只挂载 `ssh-keys/id_rsa` 和 `ssh-keys/id_rsa.pub`
- `scripts/entrypoint.sh` 也只会用 `id_rsa.pub` 生成容器内的 `authorized_keys`
- 因此按当前仓库状态，免密登录路径以 `RSA` 密钥为准

如果本地已有对应私钥，可用：

```bash
ssh -i ./ssh-keys/id_rsa root@localhost -p 10022
```

### Redis

```bash
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h localhost -p 6379
```

### MySQL

```bash
mysql -h localhost -P 3306 -u root -p"$MYSQL_ROOT_PASSWORD"
```

### PostgreSQL

```bash
PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -p 5432 -U postgres -d postgres
```

### Oracle

```bash
sqlplus "system/${ORACLE_PWD}@//localhost:1521/FREE"
```

### Attu

浏览器打开：

```text
http://localhost:18000
```

### Milvus

常用连接地址：

```text
localhost:19530
```

## Python 开发

进入容器后可直接使用 `uv`：

```bash
uv python list
uv venv
uv venv --python 3.12.9
uv pip install -r requirements.txt
uv run python main.py
```

安装新的 Python 版本：

```bash
uv python install 3.13
```

切换 pinned 版本：

```bash
uv python pin 3.12.9
```

## 常用 Docker 命令

构建镜像：

```bash
docker compose build
```

构建并包含开发容器：

```bash
docker compose --profile python-workspace build
```

查看状态：

```bash
docker compose ps
docker compose --profile python-workspace ps
```

停止服务：

```bash
docker compose down
```

查看开发容器日志：

```bash
docker logs python-workspace
```

### Docker 日志与磁盘监控

Milvus、etcd 和 MinIO 的 `json-file` 日志按单文件 `50 MB`、最多 `3` 个文件轮转，并使用 `unless-stopped` 重启策略。宿主机也应在 `/etc/docker/daemon.json` 中配置相同的默认日志上限，避免其他新建容器产生无限增长的日志文件。

Linux 主机可以安装仓库提供的磁盘检查 timer：

```bash
sudo install -m 0755 scripts/check_disk_usage.sh /usr/local/sbin/dev-workspace-disk-usage-check
sudo install -m 0644 systemd/dev-workspace-disk-usage.service /etc/systemd/system/
sudo install -m 0644 systemd/dev-workspace-disk-usage.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dev-workspace-disk-usage.timer
```

timer 每 5 分钟检查一次根文件系统。使用率达到 `80%` 时，检查单元失败并通过 `logger` 写入 `daemon.err`；可使用以下命令查看：

```bash
journalctl -u dev-workspace-disk-usage.service
```

## 目录结构

```text
.
├── Dockerfile
├── docker-compose.yml
├── setup.sh
├── setup.ps1
├── scripts/
│   ├── check_disk_usage.sh
│   └── entrypoint.sh
├── systemd/
│   ├── dev-workspace-disk-usage.service
│   └── dev-workspace-disk-usage.timer
├── ssh-keys/
│   └── README.md
├── development-config/
│   ├── terminal/
│   └── vscode/
├── docs/
└── infras/
    ├── mongodb/
    ├── mq/
    ├── mysql/
    └── redis/
```

补充说明：

- `infras/milvus/` 目录会在首次启动相关容器后自动生成数据目录，但当前未纳入仓库
- `infras/mq/docker-compose.yml` 提供 Kafka 相关独立编排
- `development-config/vscode/README.md`、`development-config/terminal/README.md`、`ssh-keys/README.md` 分别说明对应配置的使用方式
- AI assistant rules、skills 和 Codex/Qoder 同步入口已迁移到独立项目 `agent-workbench`

## 已知现状

- Linux / macOS 的 `setup.sh` 当前不会自动启动 `python-workspace` profile
- README 之外的部分辅助文档仍有旧容器名或旧目录描述，使用时应以根目录 `docker-compose.yml`、`Dockerfile` 和脚本为准
- `python-workspace` 容器的 SSH 免密登录当前按 `RSA` 挂载路径实现，`ED25519` 复制到了 `ssh-keys/`，但没有被 compose 挂载到容器

## 故障排查

开发容器未启动：

```bash
docker compose --profile python-workspace ps
docker compose --profile python-workspace up -d
```

检查 SSH 服务：

```bash
docker logs python-workspace
docker exec python-workspace ss -lnt
```

检查基础设施状态：

```bash
docker compose ps
```
