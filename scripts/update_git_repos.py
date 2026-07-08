#!/usr/bin/env python3
"""安全地批量快进更新指定目录下的 Git 仓库。"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TextIO


WORKSPACE_ROOT_FILE = Path(__file__).resolve().parent / ".workspace-root"
DEFAULT_TIMEOUT_SECONDS = 10.0
COLOR_AUTO = "auto"
COLOR_ALWAYS = "always"
COLOR_NEVER = "never"
ANSI_RESET = "\033[0m"
ANSI_CODES = {
    "bold": "1",
    "dim": "2",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "cyan": "36",
}


class ResultKind(Enum):
    """表示单个仓库的更新结果。"""

    UPDATED = "成功更新"
    MANUAL = "跳过（需人工介入）"
    TIMED_OUT = "超时"


RESULT_COLORS = {
    ResultKind.UPDATED: "green",
    ResultKind.MANUAL: "yellow",
    ResultKind.TIMED_OUT: "red",
}

RESULT_LABELS = {
    ResultKind.UPDATED: "UPDATED",
    ResultKind.MANUAL: "SKIPPED",
    ResultKind.TIMED_OUT: "TIMEOUT",
}


@dataclass(frozen=True, slots=True)
class RepoResult:
    """保存单个仓库的更新结果。"""

    path: Path
    kind: ResultKind
    detail: str


class CommandTimedOutError(RuntimeError):
    """表示子进程超过允许的执行时间。"""


class WorkspaceRootConfigError(RuntimeError):
    """表示 workspace root 配置不可用。"""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        metavar="SECONDS",
        help=f"单个仓库 git pull 的超时秒数（默认：{DEFAULT_TIMEOUT_SECONDS:g}）",
    )
    parser.add_argument(
        "--color",
        choices=(COLOR_AUTO, COLOR_ALWAYS, COLOR_NEVER),
        default=COLOR_AUTO,
        help="输出颜色模式（默认：auto）",
    )
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout 必须大于 0")
    return args


def should_use_color(mode: str, stream: TextIO) -> bool:
    """判断当前输出流是否应启用 ANSI 颜色。"""

    if mode == COLOR_ALWAYS:
        return True
    if mode == COLOR_NEVER:
        return False
    return (
        stream.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def color_text(text: str, *styles: str, use_color: bool) -> str:
    """按需给文本添加 ANSI 样式。"""

    if not use_color:
        return text
    codes = [ANSI_CODES[style] for style in styles]
    return f"\033[{';'.join(codes)}m{text}{ANSI_RESET}"


def badge(text: str, color: str, *, use_color: bool) -> str:
    """生成统一的状态标签。"""

    return color_text(f"[{text}]", "bold", color, use_color=use_color)


def result_badge(kind: ResultKind, *, use_color: bool) -> str:
    """生成仓库更新结果标签。"""

    return badge(RESULT_LABELS[kind], RESULT_COLORS[kind], use_color=use_color)


def print_error(message: str, *, use_color: bool, detail: str | None = None) -> None:
    """输出统一格式的错误消息。"""

    print(f"{badge('ERROR', 'red', use_color=use_color)} {message}", file=sys.stderr)
    if detail:
        print(f"  {detail}", file=sys.stderr)


def load_workspace_root(config_file: Path = WORKSPACE_ROOT_FILE) -> Path:
    """从配置文件读取 workspace root 绝对路径。"""

    if not config_file.is_file():
        raise WorkspaceRootConfigError(f"配置文件不存在：{config_file}")

    try:
        content = config_file.read_text(encoding="utf-8").strip()
    except OSError as error:
        message = f"读取配置文件失败：{config_file}：{error}"
        raise WorkspaceRootConfigError(message) from error

    lines = content.splitlines()
    if not lines:
        raise WorkspaceRootConfigError(f"配置文件为空：{config_file}")
    if len(lines) != 1:
        raise WorkspaceRootConfigError(
            f"配置文件必须只包含一行 workspace root 绝对路径：{config_file}"
        )

    root = Path(lines[0])
    if not root.is_absolute():
        raise WorkspaceRootConfigError(f"workspace root 必须是绝对路径：{root}")
    if not root.is_dir():
        raise WorkspaceRootConfigError(f"workspace root 路径不存在或不是目录：{root}")
    return root.resolve()


def confirm_workspace_root(root: Path, *, use_color: bool) -> bool:
    """要求用户确认即将更新的 workspace root。"""

    print(badge("CONFIG", "cyan", use_color=use_color), "Workspace root")
    print(f"  config: {color_text(str(WORKSPACE_ROOT_FILE), 'dim', use_color=use_color)}")
    print(f"  root:   {color_text(str(root), 'bold', use_color=use_color)}")
    try:
        prompt = f"{badge('CONFIRM', 'yellow', use_color=use_color)} 执行快进更新？[y/N] "
        answer = input(prompt)
    except EOFError:
        if not sys.stdin.isatty():
            print(flush=True)
        return False
    if not sys.stdin.isatty():
        print(flush=True)
    return answer.strip().lower() in {"y", "yes"}


def discover_repositories(root: Path) -> list[Path]:
    """发现普通 Git 仓库和 worktree，不跟随符号链接。"""

    def raise_scan_error(error: OSError) -> None:
        raise error

    repositories: list[Path] = []
    for current_dir, dir_names, file_names in os.walk(
        root,
        onerror=raise_scan_error,
        followlinks=False,
    ):
        if ".git" in dir_names or ".git" in file_names:
            repositories.append(Path(current_dir))
        # 不进入 Git 元数据目录，但仍允许发现仓库内嵌套的独立仓库。
        if ".git" in dir_names:
            dir_names.remove(".git")
    return sorted(repositories)


def run_git(
    repo: Path,
    *args: str,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """在仓库内运行 Git 命令，并在超时时终止整个进程组。"""

    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    process = subprocess.Popen(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        # Git 可能派生 ssh 等子进程，必须终止整个进程组。
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        raise CommandTimedOutError from error
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)


def command_detail(completed: subprocess.CompletedProcess[str]) -> str:
    """提取适合展示的一行命令输出。"""

    output = completed.stderr.strip() or completed.stdout.strip()
    return output.splitlines()[-1] if output else f"退出码 {completed.returncode}"


def update_repository(repo: Path, timeout: float) -> RepoResult:
    """仅在仓库可安全快进时执行更新。"""

    status = run_git(repo, "status", "--porcelain")
    if status.returncode != 0:
        return RepoResult(
            repo,
            ResultKind.MANUAL,
            f"无法读取仓库状态：{command_detail(status)}",
        )
    if status.stdout:
        return RepoResult(repo, ResultKind.MANUAL, "存在未提交或未跟踪的修改")

    branch = run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch.returncode != 0:
        return RepoResult(repo, ResultKind.MANUAL, "当前处于 detached HEAD")

    upstream = run_git(
        repo,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if upstream.returncode != 0:
        return RepoResult(repo, ResultKind.MANUAL, "当前分支未配置 upstream")

    branch_name = branch.stdout.strip()
    upstream_name = upstream.stdout.strip()
    try:
        pull = run_git(repo, "pull", "--ff-only", timeout=timeout)
    except CommandTimedOutError:
        return RepoResult(repo, ResultKind.TIMED_OUT, f"超过 {timeout:g} 秒，已强制中止")

    if pull.returncode != 0:
        return RepoResult(
            repo,
            ResultKind.MANUAL,
            f"无法直接快进更新：{command_detail(pull)}",
        )

    pull_output = pull.stdout.strip()
    detail = f"{branch_name} <- {upstream_name}"
    if pull_output:
        detail = f"{detail}；{pull_output.splitlines()[-1]}"
    return RepoResult(repo, ResultKind.UPDATED, detail)


def print_summary(results: Sequence[RepoResult], *, use_color: bool) -> None:
    """输出汇总统计。"""

    counts = {kind: 0 for kind in ResultKind}
    for result in results:
        counts[result.kind] += 1

    total = len(results)
    updated = color_text(str(counts[ResultKind.UPDATED]), "green", use_color=use_color)
    skipped = color_text(str(counts[ResultKind.MANUAL]), "yellow", use_color=use_color)
    timed_out = color_text(str(counts[ResultKind.TIMED_OUT]), "red", use_color=use_color)
    print(
        f"\n{badge('SUMMARY', 'blue', use_color=use_color)} "
        f"total={total} updated={updated} skipped={skipped} timeout={timed_out}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """执行批量仓库更新。"""

    args = parse_args(argv)
    stdout_color = should_use_color(args.color, sys.stdout)
    stderr_color = should_use_color(args.color, sys.stderr)

    try:
        root = load_workspace_root()
    except WorkspaceRootConfigError as error:
        print_error("Workspace root 配置不可用", detail=str(error), use_color=stderr_color)
        return 2

    if shutil.which("git") is None:
        print_error(
            "未找到 git 命令",
            detail="请先安装 git 并确认 PATH 可用。",
            use_color=stderr_color,
        )
        return 2

    if not confirm_workspace_root(root, use_color=stdout_color):
        print(
            f"{badge('CANCELLED', 'yellow', use_color=stderr_color)} 未执行任何更新。",
            file=sys.stderr,
        )
        return 1

    try:
        print(f"\n{badge('SCAN', 'cyan', use_color=stdout_color)} 正在扫描 Git 仓库...")
        repositories = discover_repositories(root)
    except OSError as error:
        print_error(
            "扫描 workspace root 失败",
            detail=f"{root}：{error}",
            use_color=stderr_color,
        )
        return 2

    results: list[RepoResult] = []
    total = len(repositories)
    print(f"{badge('FOUND', 'cyan', use_color=stdout_color)} {total} repositories\n")
    for index, repo in enumerate(repositories, start=1):
        progress = color_text(f"[{index}/{total}]", "dim", use_color=stdout_color)
        print(f"{progress} {repo}")
        try:
            result = update_repository(repo, args.timeout)
        except OSError as error:
            result = RepoResult(repo, ResultKind.MANUAL, f"执行 Git 失败：{error}")
        results.append(result)
        print(f"  {result_badge(result.kind, use_color=stdout_color)} {result.detail}")

    print_summary(results, use_color=stdout_color)
    has_unresolved = any(
        result.kind in {ResultKind.MANUAL, ResultKind.TIMED_OUT} for result in results
    )
    return 1 if has_unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
