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


DEFAULT_ROOT = Path("/Users/lilinze/Documents")
DEFAULT_TIMEOUT_SECONDS = 10.0


class ResultKind(Enum):
    """表示单个仓库的更新结果。"""

    UPDATED = "成功更新"
    MANUAL = "跳过（需人工介入）"
    TIMED_OUT = "超时"


@dataclass(frozen=True, slots=True)
class RepoResult:
    """保存单个仓库的更新结果。"""

    path: Path
    kind: ResultKind
    detail: str


class CommandTimedOutError(RuntimeError):
    """表示子进程超过允许的执行时间。"""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"扫描根目录（默认：{DEFAULT_ROOT}）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        metavar="SECONDS",
        help=f"单个仓库 git pull 的超时秒数（默认：{DEFAULT_TIMEOUT_SECONDS:g}）",
    )
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout 必须大于 0")
    return args


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


def print_summary(results: Sequence[RepoResult]) -> None:
    """输出逐仓库结果和汇总统计。"""

    print("\n执行结果：")
    for result in results:
        print(f"  [{result.kind.value}] {result.path}：{result.detail}")

    counts = {kind: 0 for kind in ResultKind}
    for result in results:
        counts[result.kind] += 1
    print(
        "\n汇总："
        f"发现 {len(results)} 个仓库，"
        f"成功更新 {counts[ResultKind.UPDATED]} 个，"
        f"跳过且需人工介入 {counts[ResultKind.MANUAL]} 个，"
        f"超时 {counts[ResultKind.TIMED_OUT]} 个。"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """执行批量仓库更新。"""

    args = parse_args(argv)
    root = args.root.expanduser().resolve()

    if shutil.which("git") is None:
        print("错误：未找到 git 命令。", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"错误：目录不存在：{root}", file=sys.stderr)
        return 2

    try:
        repositories = discover_repositories(root)
    except OSError as error:
        print(f"错误：扫描目录失败：{root}：{error}", file=sys.stderr)
        return 2

    results: list[RepoResult] = []
    for index, repo in enumerate(repositories, start=1):
        print(f"[{index}/{len(repositories)}] {repo}")
        try:
            result = update_repository(repo, args.timeout)
        except OSError as error:
            result = RepoResult(repo, ResultKind.MANUAL, f"执行 Git 失败：{error}")
        results.append(result)
        print(f"  {result.kind.value}：{result.detail}")

    print_summary(results)
    has_unresolved = any(
        result.kind in {ResultKind.MANUAL, ResultKind.TIMED_OUT} for result in results
    )
    return 1 if has_unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
