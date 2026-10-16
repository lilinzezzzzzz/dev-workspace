#!/usr/bin/env python3
"""预览或应用 VS Code 用户设置, Python / Go 项目设置; 需要 Python 3.11+"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import stat
import sys
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonc_settings import edit_settings, load_settings, same_value

try:
    import readline
except ModuleNotFoundError:
    readline = None

try:
    import tomllib
except ModuleNotFoundError:
    raise SystemExit("需要 Python 3.11+; 请使用 development-config/vscode/apply-config.sh 运行") from None

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "development-config/vscode"
PATTERN_KEY = "python.testing.autoTestDiscoverOnSavePattern"


@dataclass
class ApplicationPlan:
    source: Path
    target: Path
    location: Path
    previous: str | None
    content: str
    existing: dict[str, Any]
    desired: dict[str, Any]
    summary: list[str]
    notices: list[str]


def user_settings_path() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    if sys.platform == "win32":
        if not os.environ.get("APPDATA"):
            raise ValueError("未找到 APPDATA, 请通过 --target 指定用户设置")
        return Path(os.environ["APPDATA"]) / "Code/User/settings.json"
    directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    if not directory.is_absolute():
        raise ValueError("XDG_CONFIG_HOME 必须为绝对路径, 请通过 --target 指定用户设置")
    return directory / "Code/User/settings.json"


def read_text(path: Path) -> str:
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


@dataclass
class SettingChange:
    path: tuple[str, ...]
    exists: bool
    previous: Any
    proposed: Any


def collect_changes(
    existing: dict[str, Any],
    proposed: dict[str, Any],
    prefix: tuple[str, ...] = (),
) -> list[SettingChange]:
    changes = []
    for key, value in proposed.items():
        path = (*prefix, key)
        exists = key in existing
        if exists and same_value(existing[key], value):
            continue
        if isinstance(value, dict) and ((exists and isinstance(existing[key], dict)) or (not exists and value)):
            changes.extend(collect_changes(existing.get(key, {}), value, path))
        else:
            changes.append(SettingChange(path, exists, existing.get(key), value))
    return changes


def selected_settings(existing: dict[str, Any], changes: list[SettingChange]) -> dict[str, Any]:
    result = deepcopy(existing)
    for change in changes:
        parent = result
        for key in change.path[:-1]:
            parent = parent.setdefault(key, {})
        parent[change.path[-1]] = deepcopy(change.proposed)
    return result


def project_directory(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_dir():
        raise ValueError(f"目录必须位于项目内且已存在: {relative}")
    return candidate


def workspace_path(root: Path, path: Path) -> str:
    relative = path.relative_to(root).as_posix()
    return "${workspaceFolder}" if relative == "." else "${workspaceFolder}/" + relative


def choose_python_root(root: Path, explicit: str | None) -> Path:
    if explicit is not None:
        return project_directory(root, explicit)
    return root


def declared_test_paths(python_root: Path) -> list[str]:
    file = python_root / "pyproject.toml"
    if not file.is_file():
        return []
    with file.open("rb") as stream:
        data = tomllib.load(stream)
    options = data
    for key in ("tool", "pytest", "ini_options"):
        value = options.get(key, {})
        if not isinstance(value, dict):
            raise TypeError(f"pyproject.toml 的 {key} 必须为表")
        options = value
    paths = options.get("testpaths", [])
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise ValueError("pyproject.toml 的 pytest testpaths 必须为字符串数组")
    return paths


def existing_test_directories(root: Path, existing: dict[str, Any]) -> list[Path]:
    if not existing.get("python.testing.pytestEnabled"):
        return []
    cwd = existing.get("python.testing.cwd") or "${workspaceFolder}"
    if not isinstance(cwd, str):
        raise TypeError("已有 python.testing.cwd 必须为字符串")
    cwd = cwd.replace("${workspaceFolder}", str(root))
    directories = []
    arguments = existing.get("python.testing.pytestArgs", [])
    if not isinstance(arguments, list):
        raise TypeError("已有 pytestArgs 必须为数组")
    for argument in arguments:
        if not isinstance(argument, str) or argument.startswith("-"):
            break
        candidate = (root / cwd / argument).resolve()
        if candidate.is_dir() and candidate.is_relative_to(root):
            directories.append(candidate)
    return list(dict.fromkeys(directories))


def choose_test_directories(
    root: Path,
    python_root: Path,
    args: argparse.Namespace,
    existing: dict[str, Any],
) -> list[Path]:
    if args.test_dir is not None:
        return list(dict.fromkeys(project_directory(root, path) for path in args.test_dir))
    if args.python_root is None:
        configured = existing_test_directories(root, existing)
        if configured:
            return configured
    declared = declared_test_paths(python_root)
    if declared:
        return list(dict.fromkeys(project_directory(root, str(python_root / path)) for path in declared))
    candidates = [path for path in (python_root / "tests", python_root / "test", python_root / "dev/tests") if path.is_dir()]
    if len(candidates) > 1:
        raise ValueError("存在多个可能的测试目录, 请通过 --test-dir 明确选择, 可重复指定")
    return candidates


def choose_framework(args: argparse.Namespace, existing: dict[str, Any], tests: list[Path]) -> str:
    if args.test_framework != "auto":
        return args.test_framework
    pytest = existing.get("python.testing.pytestEnabled")
    unittest = existing.get("python.testing.unittestEnabled")
    if any(value is not None and not isinstance(value, bool) for value in (pytest, unittest)):
        raise TypeError("已有测试框架开关必须为布尔值")
    if pytest and unittest:
        raise ValueError("已有配置同时启用两种测试框架, 请指定 --test-framework")
    if pytest or unittest:
        if not tests:
            raise ValueError("已有测试已启用但无法定位测试目录, 请指定 --test-dir 或 --test-framework none")
        return "pytest" if pytest else "unittest"
    if pytest is False and unittest is False:
        return "none"
    return "pytest" if tests else "none"


def project_settings(
    args: argparse.Namespace,
    template: dict[str, Any],
    existing: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    root = args.project.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"项目根目录不存在: {root}")
    python_root = choose_python_root(root, args.python_root)
    result = deepcopy(template)
    explicit: dict[str, Any] = {}
    summary = [f"Python 根目录: {python_root.relative_to(root)}"]
    sources = (
        [project_directory(root, path) for path in args.source_dir]
        if args.source_dir is not None
        else [python_root / "src" if (python_root / "src").is_dir() else python_root]
    )
    result["python.analysis.extraPaths"] = [workspace_path(root, path) for path in sources]
    if args.python_root is not None or args.source_dir is not None:
        explicit["python.analysis.extraPaths"] = result["python.analysis.extraPaths"]
    if (python_root / ".venv/bin/python").is_file():
        result["python.defaultInterpreterPath"] = workspace_path(root, python_root / ".venv/bin/python")
        if args.python_root is not None:
            explicit["python.defaultInterpreterPath"] = result["python.defaultInterpreterPath"]
    environment = None
    if args.env_file is not None:
        environment = (root / args.env_file).resolve()
        if not environment.is_relative_to(root) or not environment.is_file():
            raise ValueError("--env-file 必须指向项目内已有文件")
    elif not args.no_env:
        candidates = list(dict.fromkeys(path for path in (python_root / ".env", root / ".env") if path.is_file()))
        if len(candidates) > 1:
            raise ValueError("存在多个环境文件, 请指定 --env-file 或 --no-env")
        environment = candidates[0] if candidates else None
    result["python.terminal.useEnvFile"] = environment is not None
    result.pop("python.envFile", None)
    if environment is not None:
        result["python.envFile"] = workspace_path(root, environment)
    if args.env_file is not None or args.no_env:
        explicit["python.terminal.useEnvFile"] = result["python.terminal.useEnvFile"]
        if environment is not None:
            explicit["python.envFile"] = result["python.envFile"]
    summary.append(f"环境文件: {environment.relative_to(root) if environment else '不启用终端环境文件'}")
    tests = [] if args.test_framework == "none" else choose_test_directories(root, python_root, args, existing)
    framework = choose_framework(args, existing, tests)
    if framework != "none" and not tests:
        raise ValueError("启用测试时必须有测试目录, 请指定 --test-dir")
    if framework == "unittest" and len(tests) != 1:
        raise ValueError("unittest 只支持一个起始目录, 请指定一个 --test-dir")
    for key in list(result):
        if key.startswith("python.testing."):
            del result[key]
    result.update({
        "python.testing.pytestEnabled": framework == "pytest",
        "python.testing.unittestEnabled": framework == "unittest",
        "python.testing.autoTestDiscoverOnSaveEnabled": framework != "none",
    })
    if tests and framework != "none":
        result["python.testing.cwd"] = workspace_path(root, python_root)
        patterns = [workspace_path(root, path) + "/**/*.py" for path in tests]
        result[PATTERN_KEY] = patterns[0] if len(patterns) == 1 else "{" + ",".join(patterns) + "}"
        relative = [os.path.relpath(path, python_root).replace(os.sep, "/") for path in tests]
        if framework == "pytest":
            result["python.testing.pytestArgs"] = relative + ["-s", "-v", "--tb=short"]
        else:
            result["python.testing.unittestArgs"] = ["-v", "-s", relative[0], "-p", "test*.py"]
    if args.python_root is not None or args.test_dir is not None or args.test_framework != "auto":
        explicit.update({key: value for key, value in result.items() if key.startswith("python.testing.")})
    summary.append(f"测试: {framework}; 目录: {', '.join(str(path.relative_to(root)) for path in tests) or '无'}")
    summary.append("源码路径: " + ", ".join(str(path.relative_to(root)) for path in sources))
    return result, explicit, summary


def write_settings(
    target: Path,
    previous: str | None,
    content: str,
    *,
    expected_location: Path | None = None,
) -> None:
    location = expected_location or target.resolve()
    if target.is_symlink() or target.resolve() != location:
        raise ValueError("目标为符号链接, 请使用真实文件路径; 项目设置请先人工处理链接")
    current = read_text(target) if target.exists() else None
    if current != previous:
        raise ValueError("目标在预览后发生变化, 未写入, 请重新运行")
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        current = read_text(target) if target.exists() else None
        if current != previous or target.is_symlink() or target.resolve() != location:
            raise ValueError("目标在预览后发生变化, 未写入, 请重新运行")
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    user = commands.add_parser("user", help="应用统一用户默认设置")
    user.add_argument("--target", type=Path, help="非默认 Profile, 远程设置或测试目标的实际路径")
    project = commands.add_parser("project-python", help="应用 Python 项目覆盖")
    project.add_argument("project", type=Path, help="必填: 项目根目录")
    project.add_argument("--python-root", help="Python 根目录, 相对项目根目录, 默认项目根目录, 如 backend")
    project.add_argument("--source-dir", action="append", help="源码目录, 相对项目根目录, 可重复指定")
    project.add_argument("--test-dir", action="append", help="测试目录, 相对项目根目录, 可重复指定")
    project.add_argument("--test-framework", choices=("auto", "pytest", "unittest", "none"), default="auto")
    environment = project.add_mutually_exclusive_group()
    environment.add_argument("--env-file", help="环境文件, 相对项目根目录")
    environment.add_argument("--no-env", action="store_true", help="不向 Python 终端加载环境文件")
    golang = commands.add_parser("project-golang", help="应用 Go 项目覆盖")
    golang.add_argument("project", type=Path, help="必填: 项目根目录")
    for command in (user, project, golang):
        command.add_argument("--write", action="store_true", help="实际写入; 省略时只预览")
        command.add_argument("--diff", action="store_true", help="显示文本差异, 可能包含本机配置值")
    return parser


def prepare_plan(args: argparse.Namespace) -> ApplicationPlan:
    project = args.command in {"project-python", "project-golang"}
    if project and not args.project.expanduser().resolve().is_dir():
        raise ValueError(f"项目根目录不存在: {args.project}")
    source = CONFIG_DIR / f"settings-{args.command}.jsonc"
    source = source.expanduser()
    if not source.is_file():
        raise ValueError("来源不存在, 请先运行 development-config/vscode/apply-config.sh --generate-only")
    template = load_settings(source.read_text(encoding="utf-8"))
    target = (
        args.project.expanduser().resolve() / ".vscode/settings.json"
        if project else args.target or user_settings_path()
    )
    target = target.expanduser()
    if project and not target.resolve().is_relative_to(args.project.expanduser().resolve()):
        raise ValueError("项目 .vscode 的链接指向项目外, 不会写入")
    if target.is_symlink():
        raise ValueError("目标为符号链接, 不会替换链接, 请指定或处理真实目标")
    previous = read_text(target) if target.exists() else None
    existing = load_settings(previous or "", allow_empty=True)
    explicit: dict[str, Any] = {}
    summary = []
    notices = []
    if args.command == "project-python":
        template, explicit, summary = project_settings(args, template, existing)
        python_root = choose_python_root(args.project.expanduser().resolve(), args.python_root)
        interpreter = python_root / ".venv/bin/python"
        if not interpreter.is_file():
            notices.append(f"提示: 未找到 {interpreter}, 请创建虚拟环境或在 VS Code 中手动选择解释器")
    template.update(explicit)
    desired = selected_settings(existing, collect_changes(existing, template))
    return ApplicationPlan(
        source=source,
        target=target,
        location=target.resolve(),
        previous=previous,
        content=edit_settings(previous or "", desired),
        existing=existing,
        desired=desired,
        summary=summary,
        notices=notices,
    )


def ask(question: str) -> str:
    print(f"\n[?] {question}")
    return input("  > ")


def display_plan(plan: ApplicationPlan, show_diff: bool) -> None:
    print("\n-- 配置预览 ------------------------")
    print(f"来源: {plan.source}\n目标: {plan.target}")
    for line in plan.summary:
        print(line)
    changes = collect_changes(plan.existing, plan.desired)
    additions = sum(not change.exists for change in changes)
    print(f"新增设置: {additions} 项; 同名值不同: {len(changes) - additions} 项")
    print("模板和项目识别结果仅作为建议; 额外设置保留")
    if show_diff:
        display_diff(plan)


def display_diff(plan: ApplicationPlan) -> None:
    print("\n-- 详细差异 ------------------------")
    print("".join(difflib.unified_diff(
        (plan.previous or "").splitlines(True),
        plan.content.splitlines(True),
        fromfile=str(plan.target),
        tofile=str(plan.target),
        n=0,
    )))


def display_changes(before: dict[str, Any], after: dict[str, Any], prefix: str = "") -> None:
    labels = {
        "python.terminal.useEnvFile": "终端自动加载环境文件",
        "python.envFile": "环境文件路径",
        "python.analysis.extraPaths": "Python 源码搜索路径",
        "python.testing.cwd": "测试运行目录",
        "python.testing.autoTestDiscoverOnSavePattern": "保存后触发测试发现的文件范围",
        "python.testing.autoTestDiscoverOnSaveEnabled": "保存后自动发现测试",
        "python.testing.pytestEnabled": "启用 pytest",
        "python.testing.unittestEnabled": "启用 unittest",
        "python.testing.pytestArgs": "pytest 运行参数",
        "python.testing.unittestArgs": "unittest 运行参数",
        "python.defaultInterpreterPath": "默认 Python 解释器路径",
    }
    for key, value in after.items():
        path = f"{prefix} / {key}" if prefix else key
        if key in before and same_value(before[key], value):
            continue
        if isinstance(value, dict) and (key not in before or isinstance(before[key], dict)) and value:
            display_changes(before.get(key, {}), value, path)
            continue
        action = "修改" if key in before else "新增"
        title = labels.get(path, path)
        print(f"\n  [{action}] {title}")
        if title != path:
            print(f"    配置项: {path}")
        previous = json.dumps(before[key], ensure_ascii=False) if key in before else "未在此文件设置 (可能继承用户设置或默认值)"
        print(f"    当前值: {previous}")
        print(f"    应用后: {json.dumps(value, ensure_ascii=False)}")


def choose_number(question: str, *, allow_cancel: bool = False) -> str:
    choices = {"1", "2", "0"} if allow_cancel else {"1", "2"}
    while True:
        answer = ask(question).strip() or "1"
        if answer in choices:
            return answer
        options = "1, 2 或 0" if allow_cancel else "1 或 2"
        print(f"[!] 请输入 {options} (默认 1)")


def review_plan(plan: ApplicationPlan) -> None:
    changes = collect_changes(plan.existing, plan.desired)
    if not changes:
        apply_plan(plan, False)
        return
    print("\n-- 全部变更预览 --------------------")
    print("以下为目标文件中的值; true 表示开启, false 表示关闭")
    print("${workspaceFolder} 表示你输入的项目根目录")
    display_changes(plan.existing, plan.desired)
    mode = choose_number(
        "如何处理这些配置? (默认 1)\n    1. 全部应用\n    2. 逐项处理\n    0. 取消",
        allow_cancel=True,
    )
    if mode == "0":
        print("[结果] 已取消, 未写入")
        return
    selected = changes
    if mode == "2":
        selected = []
        for index, change in enumerate(changes, 1):
            print(f"\n-- [{index}/{len(changes)}] {' / '.join(change.path)} --")
            previous = json.dumps(change.previous, ensure_ascii=False) if change.exists else "未在此文件设置"
            print(f"  当前值: {previous}")
            print(f"  建议值: {json.dumps(change.proposed, ensure_ascii=False)}")
            options = "1. 保留当前值\n    2. 使用建议值" if change.exists else "1. 跳过新增\n    2. 新增此项"
            if choose_number(f"如何处理? (默认 1)\n    {options}") == "2":
                selected.append(change)
    plan.desired = selected_settings(plan.existing, selected)
    plan.content = edit_settings(plan.previous or "", plan.desired) if selected else plan.previous or ""
    additions = sum(not change.exists for change in selected)
    total_additions = sum(not change.exists for change in changes)
    updates = len(selected) - additions
    retained = len(changes) - total_additions - updates
    print("\n-- 最终预览 ------------------------")
    print(f"新增: {additions} 项; 修改: {updates} 项; 保留: {retained} 项; 跳过新增: {total_additions - additions} 项")
    if mode == "2":
        display_changes(plan.existing, plan.desired)
    else:
        print("将应用上方预览中的全部建议, 尚未写入")
    if not selected:
        print("[结果] 未选择任何改动, 未写入")
        for notice in plan.notices:
            print(f"[!] {notice}")
        return
    write = ask("预览完成, 是否写入以上配置? [Y/n]").strip().lower() in {"", "y"}
    apply_plan(plan, write)


def apply_plan(plan: ApplicationPlan, write: bool) -> None:
    if plan.previous == plan.content:
        print("\n[完成] 配置已一致, 无需写入")
    elif write:
        write_settings(
            plan.target,
            plan.previous,
            plan.content,
            expected_location=plan.location,
        )
        print("\n[完成] 已写入")
    else:
        print("\n[结果] 仅预览, 未写入; 命令行模式可增加 --write")
    for notice in plan.notices:
        print(f"[!] {notice}")


def interactive(parser: argparse.ArgumentParser) -> None:
    if readline is not None:
        # 启用终端行编辑以正确处理中文退格，不记录本机路径等输入历史。
        readline.set_auto_history(False)
    print("\n-- 应用配置 ------------------------\n选择要应用的 VS Code 配置:\n  1. Python 项目配置 (默认)\n  2. Go 项目配置\n  3. 用户配置\n  0. 取消")
    choice = ask("请选择 [1/2/3/0] (默认 1):").strip() or "1"
    if choice == "0":
        print("\n[结果] 已取消, 未写入")
        return
    if choice == "3":
        arguments = ["user"]
        target = ask(f"用户设置路径 (留空使用 {user_settings_path()}):").strip()
        if target:
            arguments.extend(["--target", str(Path(target).expanduser())])
    elif choice in {"1", "2"}:
        root = ask("请输入项目根目录 (必填):").strip()
        if not root:
            raise ValueError("项目根目录不能为空, 不会使用当前目录")
        project_root = Path(root).expanduser().resolve()
        if not project_root.is_dir():
            raise ValueError(f"项目根目录不是有效的目录 (不存在或不是目录): {root}")
        command = "project-python" if choice == "1" else "project-golang"
        arguments = [command, str(project_root)]
        if choice == "1":
            python_root = ask(
                "Python 根目录 (留空使用项目根目录):\n"
                "    通常是 pyproject.toml 所在目录, 不是源码包目录\n"
                "    例如填写 backend, 不要填写 backend/src/docflow\n"
                "    可输入相对项目根目录的路径, 或项目内目录的绝对路径"
            ).strip()
            if python_root:
                arguments.extend(["--python-root", python_root])
    else:
        raise ValueError("请选择 1, 2, 3 或 0")
    args = parser.parse_args(arguments)
    plan = prepare_plan(args)
    display_plan(plan, False)
    review_plan(plan)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = sys.argv[1:] if argv is None else argv
    try:
        if not arguments:
            interactive(parser)
        else:
            args = parser.parse_args(arguments)
            plan = prepare_plan(args)
            display_plan(plan, args.diff)
            apply_plan(plan, args.write)
        return 0
    except EOFError:
        print("\n[结果] 已取消, 未写入")
        return 0
    except KeyboardInterrupt:
        print("\n[结果] 操作已中断")
        return 130
    except (OSError, ValueError, TypeError) as error:
        print(f"\n[错误] 错误: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
