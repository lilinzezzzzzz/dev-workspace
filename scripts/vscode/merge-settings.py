#!/usr/bin/env python3
"""
VS Code Settings Merger Script
生成统一用户设置及 Python / Go 项目覆盖

使用方法:
    python scripts/vscode/merge-settings.py              # 生成所有配置
    python scripts/vscode/merge-settings.py --user       # 仅生成统一用户设置
    python scripts/vscode/merge-settings.py --project-python  # 仅生成 Python 项目覆盖
    python scripts/vscode/merge-settings.py --project-golang  # 仅生成 Go 项目覆盖
"""

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "development-config/vscode"


def strip_jsonc_comments(jsonc_content: str) -> str:
    """
    移除 JSONC 中的注释，转换为标准 JSON
    支持:
    - 单行注释 // ...
    - 多行注释 /* ... */
    - 尾随逗号处理
    """
    # 使用状态机方式处理，避免误删字符串内的内容
    result = []
    i = 0
    in_string = False
    string_char = None

    while i < len(jsonc_content):
        char = jsonc_content[i]

        # 处理字符串状态
        if in_string:
            result.append(char)
            if char == "\\" and i + 1 < len(jsonc_content):
                # 转义字符，跳过下一个字符
                i += 1
                result.append(jsonc_content[i])
            elif char == string_char:
                in_string = False
                string_char = None
            i += 1
            continue

        # 检测字符串开始
        if char in "\"'":
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue

        # 检测单行注释
        if char == "/" and i + 1 < len(jsonc_content) and jsonc_content[i + 1] == "/":
            # 跳过直到行尾
            while i < len(jsonc_content) and jsonc_content[i] != "\n":
                i += 1
            continue

        # 检测多行注释
        if char == "/" and i + 1 < len(jsonc_content) and jsonc_content[i + 1] == "*":
            i += 2
            # 跳过直到 */
            while i + 1 < len(jsonc_content):
                if jsonc_content[i] == "*" and jsonc_content[i + 1] == "/":
                    i += 2
                    break
                i += 1
            continue

        result.append(char)
        i += 1

    result_str = "".join(result)

    # 移除尾随逗号 (在 } 或 ] 之前的逗号)
    result_str = re.sub(r",(\s*[}\]])", r"\1", result_str)

    return result_str


def parse_jsonc(file_path: Path) -> dict[str, Any]:
    """解析 JSONC 文件，返回字典"""
    content = file_path.read_text(encoding="utf-8")
    json_content = strip_jsonc_comments(content)
    return json.loads(json_content)


def deep_merge(
    base: Mapping[str, Any],
    override: Mapping[str, Any],
) -> dict[str, Any]:
    """
    深度合并两个字典
    - override 中的值会覆盖 base 中的值
    - 对于嵌套字典，递归合并
    - 对于列表，override 完全替换 base
    """
    result = deepcopy(dict(base))

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def get_source_files(target: str) -> tuple[str, ...]:
    """返回指定目标按覆盖优先级排列的源文件。"""
    if target == "user":
        return (
            "common/settings.jsonc",
            "python/settings.jsonc",
            "golang/settings.jsonc",
        )
    if target in {"project-python", "project-golang"}:
        language = target.removeprefix("project-")
        return (
            "common/project-settings.jsonc",
            f"{language}/project-settings.jsonc",
        )
    raise ValueError(f"不支持的配置目标: {target}")


def merge_settings(base_dir: Path, target: str) -> dict[str, Any]:
    """合并统一用户默认设置或指定语言的项目覆盖。"""
    merged: dict[str, Any] = {}
    for source in get_source_files(target):
        merged = deep_merge(merged, parse_jsonc(base_dir / source))
    return merged


def generate_jsonc_with_comments(
    config: Mapping[str, Any],
    header_comment: str,
    source_files: Sequence[str],
) -> str:
    """生成配置正文及真实源文件列表，不复制源配置的逐项注释。"""
    lines = [
        "{",
        f"  // {header_comment}",
        "  // 此文件由 scripts/vscode/merge-settings.py 自动生成，请勿手动编辑",
        "  // 源配置: " + " + ".join(source_files),
        "",
    ]
    lines.extend(json.dumps(dict(config), indent=2, ensure_ascii=False).splitlines()[1:-1])
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="生成 VS Code 统一用户默认设置及项目覆盖",
    )
    targets = {
        "user": "统一用户默认设置",
        "project-python": "Python 项目覆盖",
        "project-golang": "Go 项目覆盖",
    }
    for target, title in targets.items():
        parser.add_argument(
            f"--{target}",
            action="store_true",
            help=f"生成{title}",
        )
    args = parser.parse_args()
    selected = [target for target in targets if getattr(args, target.replace("-", "_"))]
    if not selected:
        selected = list(targets)

    base_dir = CONFIG_DIR
    for target in selected:
        merged = merge_settings(base_dir, target)
        content = generate_jsonc_with_comments(
            merged,
            targets[target],
            get_source_files(target),
        )
        output_path = base_dir / f"settings-{target}.jsonc"
        output_path.write_text(content, encoding="utf-8")
        print(f"已生成: {output_path}")

    print(f"完成，共生成 {len(selected)} 个配置文件。")
    print("settings-user.jsonc 用于对比并合并到用户设置，保留现有本机私有设置。")
    print("settings-project-*.jsonc 是项目覆盖示例，按项目实际情况对比合并。")
    print("本脚本仅写入 development-config/vscode，不修改用户设置或任何项目的 .vscode。")


if __name__ == "__main__":
    main()
