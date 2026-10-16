#!/usr/bin/env bash
# 统一入口：使用仓库的 uv 环境，选择是否生成配置，再进入应用流程。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
IMPLEMENTATION_DIR="$REPO_ROOT/scripts/vscode"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat <<'HELP'
用法: apply-config.sh [应用参数]
      apply-config.sh --generate-only [生成参数]

不带参数: 选择是否生成三份配置 (默认不生成), 再进入 Python (默认) / Go / 用户配置菜单
带应用参数: 自动生成三份配置后应用; 默认仅预览
应用参数: user [--target PATH] [--write] [--diff]
          project-python ROOT [项目选项] [--write] [--diff]
          project-golang ROOT [--write] [--diff]
只生成:   --generate-only [--user] [--project-python] [--project-golang]

应用参数原样转发给 scripts/vscode/apply-settings.py
更多帮助: apply-config.sh user --help
          apply-config.sh project-python --help
          apply-config.sh project-golang --help
HELP
    exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "[错误] 未找到 uv, 请先安装 uv" >&2
    exit 127
fi

if [[ "${1:-}" == "--generate-only" ]]; then
    shift
    exec uv run --project "$REPO_ROOT" --locked python -B \
        "$IMPLEMENTATION_DIR/merge-settings.py" "$@"
fi

# 子命令帮助不生成文件。
for argument in "$@"; do
    if [[ "$argument" == "--help" || "$argument" == "-h" ]]; then
        exec uv run --project "$REPO_ROOT" --locked python -B \
            "$IMPLEMENTATION_DIR/apply-settings.py" "$@"
    fi
done

generate_config=true
if [[ "$#" -eq 0 ]]; then
    while true; do
        printf '\n[?] 是否生成配置? [y/N]\n  > '
        if ! IFS= read -r answer; then
            printf '\n[结果] 已取消\n'
            exit 0
        fi
        case "$answer" in
            y|Y) break ;;
            ""|n|N) generate_config=false; break ;;
            *) printf '[!] 请输入 y 或 n (回车默认不生成)\n' ;;
        esac
    done
fi

if [[ "$generate_config" == true ]]; then
    # 应用流程隐藏生成日志，保留标准错误；只生成模式仍显示完整结果。
    uv run --project "$REPO_ROOT" --locked python -B \
        "$IMPLEMENTATION_DIR/merge-settings.py" > /dev/null
fi

exec uv run --project "$REPO_ROOT" --locked python -B \
    "$IMPLEMENTATION_DIR/apply-settings.py" "$@"
