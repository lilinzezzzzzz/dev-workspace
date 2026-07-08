# AGENTS.md

## Scope

- 本文件适用于整个 `dev-workspace` 仓库。
- 本仓库主要维护本地开发工作区：Docker Compose 基础设施、Python 开发容器、终端/VS Code 配置、SSH 密钥同步说明和辅助脚本。

## Repository Rules

- 不提交机器私有信息、密钥、token、cookie、真实服务凭证或本机绝对路径配置。
- `ssh-keys/` 下的私钥、公钥和 `known_hosts` 按 `.gitignore` 处理；不要新增可提交的真实密钥。
- `scripts/.workspace-root` 是本机私有配置，用于 `scripts/update_git_repos.py`，必须保持 ignored，不要提交。
- `infras/**/data`、`infras/**/logs` 和 Milvus/PostgreSQL 等本地数据目录是运行时产物，不要手工纳入版本控制。
- 修改 `development-config/terminal/configs/zshrc`、`ghostty.config`、`starship.toml` 或 `environment.d/*` 时，同步更新 `development-config/terminal/README.md` 中的使用说明。
- 修改 VS Code 配置模板时，同步更新 `development-config/vscode/README.md`，并避免覆盖 `.vscode/` 中的用户本地配置。

## Docker And Runtime

- `python-workspace` 服务在 `python-workspace` profile 下；需要启动开发容器时使用：

  ```bash
  docker compose --profile python-workspace up -d
  ```

- 默认基础设施可用：

  ```bash
  docker compose up -d
  ```

- `postgres` 和 `oracle` 是 `JSONType` 方言验证用 profile 服务，不要把它们描述成默认必启服务。
- `Dockerfile` 面向本地开发，包含开发便利配置和固定 dev-only root 密码；不要把这些设置包装成生产安全基线。

## Scripts

- 运行 Python 测试优先使用 `python3 -B`，避免生成 `__pycache__`：

  ```bash
  python3 -B -m unittest tests/test_update_git_repos.py
  ```

- `scripts/update_git_repos.py` 只允许从脚本同目录的 `scripts/.workspace-root` 读取 workspace root；不要恢复默认扫描根目录或绕过确认。
- 修改 `scripts/update_git_repos.py` 时，同步更新 `tests/test_update_git_repos.py`，至少覆盖配置读取、确认逻辑、跳过/超时/失败分支和输出格式。

## Documentation

- README 应以 `docker-compose.yml`、`Dockerfile`、`setup.sh`、`setup.ps1` 和 `development-config/` 的当前行为为准。
- 如果脚本输出与实际 Compose profile 行为不一致，README 必须明确现状和限制，不要扩大承诺。
