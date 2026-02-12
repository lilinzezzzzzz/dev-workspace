#!/usr/bin/env python3
"""
VS Code Settings Merger Script
合并 common/settings.json 与语言特定配置(python/golang)
生成完整的 VS Code settings.json 配置文件

使用方法:
    python merge-settings.py              # 生成所有配置
    python merge-settings.py --python     # 仅生成 Python 配置
    python merge-settings.py --golang     # 仅生成 Go 配置
"""

import json
import re
import argparse
from pathlib import Path
from copy import deepcopy
from typing import Any, Dict


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
            if char == '\\' and i + 1 < len(jsonc_content):
                # 转义字符，跳过下一个字符
                i += 1
                result.append(jsonc_content[i])
            elif char == string_char:
                in_string = False
                string_char = None
            i += 1
            continue

        # 检测字符串开始
        if char in '"\'':
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue

        # 检测单行注释
        if char == '/' and i + 1 < len(jsonc_content) and jsonc_content[i + 1] == '/':
            # 跳过直到行尾
            while i < len(jsonc_content) and jsonc_content[i] != '\n':
                i += 1
            continue

        # 检测多行注释
        if char == '/' and i + 1 < len(jsonc_content) and jsonc_content[i + 1] == '*':
            i += 2
            # 跳过直到 */
            while i + 1 < len(jsonc_content):
                if jsonc_content[i] == '*' and jsonc_content[i + 1] == '/':
                    i += 2
                    break
                i += 1
            continue

        result.append(char)
        i += 1

    result_str = ''.join(result)

    # 移除尾随逗号 (在 } 或 ] 之前的逗号)
    result_str = re.sub(r',(\s*[}\]])', r'\1', result_str)

    return result_str


def parse_jsonc(file_path: Path) -> Dict[str, Any]:
    """解析 JSONC 文件，返回字典"""
    content = file_path.read_text(encoding='utf-8')
    json_content = strip_jsonc_comments(content)
    return json.loads(json_content)


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并两个字典
    - override 中的值会覆盖 base 中的值
    - 对于嵌套字典，递归合并
    - 对于列表，override 完全替换 base
    """
    result = deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def generate_jsonc_with_comments(config: Dict[str, Any], header_comment: str = "") -> str:
    """
    生成带有头部注释的 JSONC 内容
    由于无法保留原始注释，这里添加文件头部说明
    """
    lines = ["{"]
    lines.append(f"  // {header_comment}")
    lines.append("  // 此文件由 merge-settings.py 自动生成，请勿手动编辑")
    lines.append("  // 源配置: common/settings.json + {lang}/settings.json")
    lines.append("")

    # 格式化 JSON 内容
    json_str = json.dumps(config, indent=2, ensure_ascii=False)

    # 跳过第一行的 "{" 和最后一行的 "}"
    json_lines = json_str.split('\n')[1:-1]
    lines.extend(json_lines)
    lines.append("}")

    return '\n'.join(lines)


def merge_settings(base_dir: Path, lang: str) -> Dict[str, Any]:
    """
    合并通用配置和语言特定配置

    Args:
        base_dir: vscode-idea 目录路径
        lang: 语言名称 (python 或 golang)

    Returns:
        合并后的配置字典
    """
    common_path = base_dir / "common" / "settings.json"
    lang_path = base_dir / lang / "settings.json"

    # 解析配置文件
    common_config = parse_jsonc(common_path)
    lang_config = parse_jsonc(lang_path)

    # 深度合并
    merged = deep_merge(common_config, lang_config)

    return merged


def main():
    parser = argparse.ArgumentParser(
        description="合并 VS Code 配置文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python merge-settings.py              # 生成所有配置
    python merge-settings.py --python     # 仅生成 Python 配置
    python merge-settings.py --golang     # 仅生成 Go 配置
        """
    )
    parser.add_argument('--python', action='store_true', help='仅生成 Python 配置')
    parser.add_argument('--golang', action='store_true', help='仅生成 Go 配置')

    args = parser.parse_args()

    # 确定脚本所在目录
    script_dir = Path(__file__).parent

    # 确定要生成哪些配置
    generate_python = args.python or (not args.python and not args.golang)
    generate_golang = args.golang or (not args.python and not args.golang)

    generated_files = []

    if generate_python:
        print("📄 正在合并 Python 配置...")
        merged = merge_settings(script_dir, "python")
        output_path = script_dir / "settings-python.jsonc"

        # 生成 JSONC 内容
        content = generate_jsonc_with_comments(merged, "Python 开发环境配置")
        output_path.write_text(content, encoding='utf-8')

        print(f"   ✅ 已生成: {output_path}")
        generated_files.append(output_path)

    if generate_golang:
        print("📄 正在合并 Golang 配置...")
        merged = merge_settings(script_dir, "golang")
        output_path = script_dir / "settings-golang.jsonc"

        # 生成 JSONC 内容
        content = generate_jsonc_with_comments(merged, "Golang 开发环境配置")
        output_path.write_text(content, encoding='utf-8')

        print(f"   ✅ 已生成: {output_path}")
        generated_files.append(output_path)

    print(f"\n🎉 完成! 共生成 {len(generated_files)} 个配置文件")
    print("\n使用方法:")
    print("  将生成的配置文件复制到项目的 .vscode/settings.json 即可使用")
    print("  或创建符号链接: ln -s /path/to/settings-python.jsonc .vscode/settings.json")


if __name__ == "__main__":
    main()
