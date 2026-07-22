# UV 多版本 Python 管理指南

## 已安装的 Python 版本

镜像中已预装以下 Python 版本（通过 uv 管理）：
- Python 3.11.10
- Python 3.12.9（默认版本）
- Python 3.13（最新稳定版）

## 常用命令

### 查看已安装的 Python 版本
```bash
uv python list
```

### 切换默认 Python 版本
```bash
# 切换到 3.11.10
uv python pin 3.11.10

# 切换到 3.12.9
uv python pin 3.12.9

# 切换到 3.13
uv python pin 3.13
```

### 安装新的 Python 版本
```bash
# 安装特定版本
uv python install 3.10.14

# 安装最新的某个大版本
uv python install 3.14
```

### 查看当前使用的 Python 版本
```bash
uv python find
# 或
python --version
```

## 项目开发

### 创建虚拟环境（指定 Python 版本）
```bash
# 使用默认版本
uv venv

# 使用特定版本
uv venv --python 3.11.10
uv venv --python 3.12.9
uv venv --python 3.13
```

### 激活虚拟环境
```bash
source .venv/bin/activate
```

### 安装依赖
```bash
# 使用 uv 安装（比 pip 快很多）
uv pip install requests numpy pandas

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 使用 uv sync（推荐，自动管理环境）
uv sync
```

### 运行 Python 脚本（无需激活虚拟环境）
```bash
# uv 自动使用项目环境
uv run python script.py

# 使用特定版本运行
uv run --python 3.11.10 python script.py
```

## 项目初始化

### 初始化新项目
```bash
# 创建新项目（生成 pyproject.toml）
uv init my-project
cd my-project

# 添加依赖
uv add requests pandas numpy

# 添加开发依赖
uv add --dev pytest black ruff
```

### 从现有项目迁移
```bash
# 如果有 requirements.txt
uv pip compile requirements.txt -o requirements.lock

# 如果有 pyproject.toml
uv sync
```

## 环境变量说明

镜像中已配置的 uv 环境变量：
- `UV_PYTHON_INSTALL_DIR=/opt/python` - Python 安装目录
- `UV_PYTHON_PREFERENCE=only-managed` - 只使用 uv 管理的 Python
- `UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple` - 使用阿里云镜像源

## 构建镜像

```bash
# 构建镜像
docker-compose build

# 或使用 Docker 直接构建
docker build -t python-uv-env:latest .
```

## 启动容器

```bash
# 启动所有服务
docker-compose up -d

# 只启动 python-venv 服务
docker-compose up -d python-venv
```

## 进入容器

```bash
# 使用 docker exec
docker exec -it python-venv bash

# 或使用 SSH（密码见 .env 的 PYTHON_WORKSPACE_ROOT_PASSWORD）
ssh root@localhost -p 10022
```

## 最佳实践

1. **使用 `uv run`** - 无需手动激活虚拟环境
2. **使用 `pyproject.toml`** - 现代 Python 项目标准
3. **使用 `uv sync`** - 自动同步环境和依赖
4. **版本固定** - 在项目目录使用 `uv python pin` 固定版本
5. **依赖锁定** - uv 自动生成 `uv.lock` 确保环境一致

## 示例工作流

```bash
# 1. 进入容器
docker exec -it python-venv bash

# 2. 创建新项目
cd /app
uv init my-api --python 3.12.9

# 3. 添加依赖
cd my-api
uv add fastapi uvicorn

# 4. 运行项目
uv run uvicorn main:app --reload

# 5. 如需切换 Python 版本
uv python pin 3.11.10
uv sync  # 重新同步环境
```

## 故障排查

### 查看 uv 配置
```bash
uv config list
```

### 清理缓存
```bash
uv cache clean
```

### 重新安装 Python
```bash
uv python uninstall 3.12.9
uv python install 3.12.9
```

## 参考资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
