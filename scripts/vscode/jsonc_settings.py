"""读取 JSONC，并只编辑发生变化的设置，保留其余注释和文本。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class JsonNode:
    value: Any
    start: int
    end: int
    members: dict[str, JsonNode] = field(default_factory=dict)
    key_start: int | None = None
    trailing_comma: bool = False


def _reject_constant(value: str) -> None:
    raise ValueError(f"JSONC 不支持常量 {value}")


class JsoncParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.position = 1 if text.startswith("\ufeff") else 0
        self.decoder = json.JSONDecoder(parse_constant=_reject_constant)

    def skip_trivia(self) -> None:
        while self.position < len(self.text):
            if self.text[self.position] in " \t\r\n":
                self.position += 1
            elif self.text.startswith("//", self.position):
                end = self.text.find("\n", self.position)
                self.position = len(self.text) if end < 0 else end
            elif self.text.startswith("/*", self.position):
                end = self.text.find("*/", self.position + 2)
                if end < 0:
                    raise ValueError("JSONC 块注释未结束")
                self.position = end + 2
            else:
                return

    def parse(self) -> JsonNode | None:
        self.skip_trivia()
        if self.position == len(self.text):
            return None
        node = self.parse_value()
        self.skip_trivia()
        if self.position != len(self.text):
            raise ValueError(f"JSONC 根值之后存在额外内容，位置 {self.position}")
        return node

    def parse_value(self) -> JsonNode:
        self.skip_trivia()
        if self.position >= len(self.text):
            raise ValueError("JSONC 值不完整")
        start = self.position
        char = self.text[start]
        if char == "{":
            return self.parse_object()
        if char == "[":
            self.position += 1
            values = []
            self.skip_trivia()
            while self.position < len(self.text) and self.text[self.position] != "]":
                values.append(self.parse_value().value)
                self.skip_trivia()
                if self.position < len(self.text) and self.text[self.position] == ",":
                    self.position += 1
                    self.skip_trivia()
                else:
                    break
            self.expect("]")
            return JsonNode(values, start, self.position)
        value, self.position = self.decoder.raw_decode(self.text, self.position)
        return JsonNode(value, start, self.position)

    def expect(self, char: str) -> None:
        self.skip_trivia()
        if self.position >= len(self.text) or self.text[self.position] != char:
            raise ValueError(f"JSONC 位置 {self.position} 应为 {char}")
        self.position += 1

    def parse_object(self) -> JsonNode:
        start = self.position
        self.position += 1
        members: dict[str, JsonNode] = {}
        trailing_comma = False
        self.skip_trivia()
        while self.position < len(self.text) and self.text[self.position] != "}":
            key_start = self.position
            key, self.position = self.decoder.raw_decode(self.text, self.position)
            if not isinstance(key, str):
                raise TypeError("JSONC 对象的键必须为字符串")
            if key in members:
                raise ValueError(f"JSONC 存在重复键：{key}")
            self.expect(":")
            node = self.parse_value()
            node.key_start = key_start
            members[key] = node
            self.skip_trivia()
            if self.position < len(self.text) and self.text[self.position] == ",":
                self.position += 1
                self.skip_trivia()
                trailing_comma = self.text[self.position:self.position + 1] == "}"
            else:
                break
        self.expect("}")
        return JsonNode(
            {key: node.value for key, node in members.items()},
            start,
            self.position,
            members=members,
            trailing_comma=trailing_comma,
        )


def load_settings(text: str, *, allow_empty: bool = False) -> dict[str, Any]:
    node = JsoncParser(text).parse()
    if node is None:
        if allow_empty:
            return {}
        raise ValueError("设置文件为空，请先生成配置")
    if not isinstance(node.value, dict):
        raise TypeError("设置文件的根值必须为对象")
    return node.value


def same_value(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def _indent(text: str, position: int) -> str:
    line_start = text.rfind("\n", 0, position) + 1
    return re.match(r"[ \t]*", text[line_start:position]).group()


def _render(value: Any, indent: str) -> str:
    lines = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).splitlines()
    return lines[0] + "".join("\n" + indent + line for line in lines[1:])


def edit_settings(text: str, desired: dict[str, Any]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    root = JsoncParser(text).parse()
    if root is None:
        prefix = text + (newline if text and not text.endswith("\n") else "")
        return prefix + json.dumps(desired, ensure_ascii=False, indent=2).replace("\n", newline) + newline
    if not isinstance(root.value, dict):
        raise TypeError("设置文件的根值必须为对象")
    edits: list[tuple[int, int, str]] = []

    def update(node: JsonNode, value: Any) -> None:
        if same_value(node.value, value):
            return
        if not isinstance(node.value, dict) or not isinstance(value, dict):
            position = node.key_start if node.key_start is not None else node.start
            edits.append((node.start, node.end, _render(value, _indent(text, position))))
            return
        if not node.value.keys() <= value.keys():
            raise ValueError("应用设置不会删除已有键")
        for key, child in node.members.items():
            update(child, value[key])
        additions = [(key, item) for key, item in value.items() if key not in node.members]
        if not additions:
            return
        parent_indent = _indent(text, node.start)
        child_indent = parent_indent + "  "
        for child in node.members.values():
            key_start = child.key_start
            assert key_start is not None
            line_start = text.rfind("\n", 0, key_start) + 1
            if not text[line_start:key_start].strip():
                child_indent = text[line_start:key_start]
                break
        close = node.end - 1
        line_start = text.rfind("\n", 0, close) + 1
        insert = line_start if not text[line_start:close].strip() else close
        leading_comma = ""
        if node.members and not node.trailing_comma:
            last = next(reversed(node.members.values()))
            if last.end == insert:
                leading_comma = ","
            else:
                edits.append((last.end, last.end, ","))
        lines = []
        for index, (key, item) in enumerate(additions):
            line = child_indent + json.dumps(key, ensure_ascii=False) + ": "
            line += _render(item, child_indent)
            if index < len(additions) - 1 or node.trailing_comma:
                line += ","
            lines.append(line)
        prefix = "" if insert and text[insert - 1] == "\n" else "\n"
        suffix = parent_indent if insert == close else ""
        edits.append((insert, insert, leading_comma + prefix + "\n".join(lines) + "\n" + suffix))

    update(root, desired)
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement.replace("\n", newline) + text[end:]
    if not same_value(load_settings(text), desired):
        raise ValueError("JSONC 编辑结果校验失败，未写入")
    return text
