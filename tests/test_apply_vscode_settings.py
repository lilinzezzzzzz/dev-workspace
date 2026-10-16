from __future__ import annotations

import importlib.util
import json
import os
import runpy
import select
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

BASE_DIR = Path(__file__).parents[1] / "development-config/vscode"
SCRIPT_DIR = Path(__file__).parents[1] / "scripts/vscode"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


jsonc = load_module("jsonc_settings", SCRIPT_DIR / "jsonc_settings.py")
application = load_module("apply_vscode_settings", SCRIPT_DIR / "apply-settings.py")
generator = runpy.run_path(str(SCRIPT_DIR / "merge-settings.py"))


class JsoncEditingTest(unittest.TestCase):
    def test_comments_trailing_commas_and_string_literals(self) -> None:
        text = r'''{
          // 注释不能改变字符串里的逗号和注释符号
          "literal": ", } // /* ,]",
          "url": "https://example.com/path",
          "escaped": "quote: \" // still a string",
          "items": [1, /* item */ false,],
        }'''
        values = jsonc.load_settings(text)
        self.assertEqual(values["literal"], ", } // /* ,]")
        self.assertEqual(values["items"], [1, False])
        self.assertEqual(jsonc.edit_settings(text, values), text)

    def test_duplicate_invalid_or_non_object_settings_are_rejected(self) -> None:
        for text in (
            '{"a": 1, "a": 2}',
            '{"a": {"b": 1, "b": 2}}',
            '{"a": 1',
            '{"a": NaN}',
            '{"a": 1 /* unfinished',
            '{"a": [1 2]}',
            '[]',
        ):
            with self.subTest(text=text), self.assertRaises((ValueError, TypeError)):
                jsonc.load_settings(text)

    def test_nested_updates_preserve_comments_bom_and_crlf(self) -> None:
        text = '\ufeff{\r\n  // 保留\r\n  "a": {"x": 1}, // 行尾\r\n}\r\n'
        result = jsonc.edit_settings(text, {"a": {"x": 2, "y": True}, "b": [1, 2]})
        self.assertEqual(jsonc.load_settings(result), {"a": {"x": 2, "y": True}, "b": [1, 2]})
        self.assertTrue(result.startswith("\ufeff"))
        self.assertIn("// 保留\r\n", result)
        self.assertIn("// 行尾\r\n", result)
        self.assertNotIn("\n", result.replace("\r\n", ""))

    def test_object_insertions_and_scalar_type_changes(self) -> None:
        for text in ('{}', '{ /* keep */ }', '{"a":0}', '{"a":0,}', '{\n"a":0 // keep\n}'):
            with self.subTest(text=text):
                before = jsonc.load_settings(text)
                desired = {**before, "a": False, "nested": {"b": ["x", "y"]}}
                result = jsonc.edit_settings(text, desired)
                self.assertEqual(jsonc.load_settings(result), desired)
                self.assertIs(jsonc.load_settings(result)["a"], False)
        self.assertIn("// only comment", jsonc.edit_settings("// only comment", {"a": 1}))


class ApplySettingsTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="agent-task.")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        repository = self.root / "repository with spaces"
        self.fixture = repository / "development-config/vscode"
        self.fixture.mkdir(parents=True)
        self.scripts = repository / "scripts/vscode"
        self.scripts.mkdir(parents=True)
        for name in ("apply-settings.py", "jsonc_settings.py"):
            shutil.copyfile(SCRIPT_DIR / name, self.scripts / name)
        self.user_source = self.fixture / "settings-user.jsonc"
        self.user_source.write_text(json.dumps({
            "editor.fontSize": 14,
            "git.blame.editorDecoration.enabled": True,
            "[python]": {"editor.formatOnSave": False},
        }), encoding="utf-8")
        project = generator["merge_settings"](BASE_DIR, "project-python")
        (self.fixture / "settings-project-python.jsonc").write_text(json.dumps(project), encoding="utf-8")

    def run_script(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.scripts / "apply-settings.py"), *args],
            input=input_text,
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def project(self, name: str = "project") -> Path:
        project = self.root / name
        project.mkdir(parents=True)
        return project

    def create(self, path: Path, text: str = "") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_user_preview_has_no_filesystem_writes(self) -> None:
        target = self.root / "profile/User/settings.json"
        result = self.run_script("user", "--target", str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("仅预览", result.stdout)
        self.assertFalse(target.parent.exists())

    def test_user_template_wins_and_extra_settings_comments_permissions_survive(self) -> None:
        target = self.root / "settings.json"
        target.write_text('''{
  // 本机专用项和说明保留
  "todo-tree.ripgrep.ripgrep": "/custom/rg",
  "git.blame.editorDecoration.enabled": false,
  "[python]": {
    // 已有语言块
    "editor.formatOnSave": true,
    "custom.projectHint": true
  }
}
''', encoding="utf-8")
        target.chmod(0o640)
        source = self.user_source.read_bytes()
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings(target.read_text())
        self.assertTrue(values["git.blame.editorDecoration.enabled"])
        self.assertFalse(values["[python]"]["editor.formatOnSave"])
        self.assertTrue(values["[python]"]["custom.projectHint"])
        self.assertEqual(values["todo-tree.ripgrep.ripgrep"], "/custom/rg")
        self.assertIn("// 本机专用项和说明保留", target.read_text())
        self.assertIn("// 已有语言块", target.read_text())
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)
        self.assertEqual(self.user_source.read_bytes(), source)
        before = target.read_bytes(), target.stat().st_mtime_ns
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), before)

    def test_real_user_template_can_be_applied_to_an_empty_target(self) -> None:
        template = generator["merge_settings"](BASE_DIR, "user")
        self.user_source.write_text(json.dumps(template), encoding="utf-8")
        target = self.root / "settings.json"
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(jsonc.load_settings(target.read_text()), template)

    def test_user_mode_rejects_removed_conflict_option(self) -> None:
        result = self.run_script("user", "--conflicts", "existing")
        self.assertEqual(result.returncode, 2)

    def test_project_root_is_required_in_cli_and_menu(self) -> None:
        result = self.run_script("project-python", "--write")
        self.assertEqual(result.returncode, 2)
        result = self.run_script(input_text="1\n\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("项目根目录不能为空", result.stderr)
        self.assertFalse((self.root / ".vscode").exists())

    def test_invalid_project_root_stops_before_further_questions(self) -> None:
        file = self.root / "not-a-directory.txt"
        file.write_text("keep", encoding="utf-8")
        for choice in ("1", "2"):
            for root in ("预览完成，是否写入以上配", str(file)):
                with self.subTest(choice=choice, root=root):
                    result = self.run_script(input_text=f"{choice}\n{root}\n")
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertIn("项目根目录不是有效的目录", result.stderr)
                    self.assertNotIn("Python 根目录", result.stdout)
                    self.assertNotIn("项目同名设置冲突时", result.stdout)
                    self.assertNotIn("配置预览", result.stdout)
        self.assertEqual(file.read_text(), "keep")
        self.assertFalse((self.root / "预览完成，是否写入以上配").exists())

    @unittest.skipUnless(os.name == "posix" and application.readline is not None, "需要 POSIX 终端和 readline")
    def test_terminal_can_erase_chinese_characters_before_entering_project_path(self) -> None:
        # pty 仅在 POSIX 可用，平台筛选后再导入。
        import pty

        project = self.project("中文项目")
        master, slave = pty.openpty()
        process = subprocess.Popen(
            [sys.executable, "-B", str(self.scripts / "apply-settings.py")],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            env={**os.environ, "TERM": "xterm-256color"},
        )
        os.close(slave)
        output = bytearray()

        def wait_for(text: str) -> None:
            expected = text.encode()
            deadline = time.monotonic() + 10
            while expected not in output:
                self.assertLess(time.monotonic(), deadline, output.decode(errors="replace"))
                if select.select([master], [], [], 0.1)[0]:
                    output.extend(os.read(master, 65536))

        try:
            wait_for("请选择")
            os.write(master, b"1\n")
            wait_for("请输入项目根目录")
            os.write(master, "详细".encode() + b"\x7f\x7f" + str(project).encode() + b"\n")
            wait_for("Python 根目录 (")
            os.write(master, b"\n")
            wait_for("如何处理这些配置?")
            os.write(master, b"1\n")
            wait_for("预览完成, 是否写入")
            os.write(master, b"n\n")
            wait_for("仅预览, 未写入")
            self.assertEqual(process.wait(timeout=10), 0)
            self.assertFalse((project / ".vscode").exists())
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
            os.close(master)

    def test_explicit_backend_layout_is_detected_without_importing_project_code(self) -> None:
        project = self.project(".codex/worktrees/My Project")
        self.create(project / "backend/pyproject.toml", '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n')
        self.create(project / "backend/src/pkg/__init__.py", 'raise RuntimeError("must not execute")')
        self.create(project / "backend/tests/test_app.py", 'raise RuntimeError("must not execute")')
        self.create(project / "backend/.env", "FAKE_SECRET=do-not-display")
        self.create(project / "backend/.venv/bin/python")
        result = self.run_script("project-python", str(project), "--python-root", "backend")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((project / ".vscode").exists())
        result = self.run_script("project-python", str(project), "--python-root", "backend", "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings((project / ".vscode/settings.json").read_text())
        self.assertEqual(values["python.testing.cwd"], "${workspaceFolder}/backend")
        self.assertEqual(values["python.testing.pytestArgs"], ["tests", "-s", "-v", "--tb=short"])
        self.assertEqual(values[application.PATTERN_KEY], "${workspaceFolder}/backend/tests/**/*.py")
        self.assertEqual(values["python.analysis.extraPaths"], ["${workspaceFolder}/backend/src"])
        self.assertEqual(values["python.envFile"], "${workspaceFolder}/backend/.env")
        self.assertEqual(values["python.defaultInterpreterPath"], "${workspaceFolder}/backend/.venv/bin/python")
        self.assertNotIn("do-not-display", result.stdout + result.stderr)
        self.assertFalse((project / ".vscode/launch.json").exists())

    def test_no_tests_disables_discovery_without_inventing_directories(self) -> None:
        project = self.project()
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings((project / ".vscode/settings.json").read_text())
        self.assertFalse(values["python.testing.pytestEnabled"])
        self.assertFalse(values["python.testing.autoTestDiscoverOnSaveEnabled"])
        self.assertFalse(values["python.terminal.useEnvFile"])
        self.assertNotIn("python.testing.pytestArgs", values)
        self.assertNotIn(application.PATTERN_KEY, values)
        self.assertNotIn("python.envFile", values)
        self.assertFalse((project / "tests").exists())

    def test_python_batch_cli_and_menu_apply_suggestions(self) -> None:
        project = self.project()
        target = project / ".vscode/settings.json"
        for menu in (False, True):
            with self.subTest(menu=menu):
                self.create(target, '{"python.analysis.extraPaths":["custom"],"private.setting":true}')
                result = (
                    self.run_script(input_text=f"1\n{project}\n\n1\ny\n")
                    if menu else self.run_script("project-python", str(project), "--write")
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                values = jsonc.load_settings(target.read_text())
                self.assertEqual(values["python.analysis.extraPaths"], ["${workspaceFolder}"])
                self.assertTrue(values["private.setting"])
                self.assertTrue(result.stdout.strip().endswith("请创建虚拟环境或在 VS Code 中手动选择解释器"))
        result = self.run_script("project-python", str(project), "--conflicts", "existing")
        self.assertEqual(result.returncode, 2)

    def test_only_posix_venv_interpreter_is_detected_and_missing_notice_is_last(self) -> None:
        project = self.project()
        self.create(project / ".venv/Scripts/python.exe")
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = project / ".vscode/settings.json"
        self.assertNotIn("python.defaultInterpreterPath", jsonc.load_settings(target.read_text()))
        self.assertIn("提示: 未找到", result.stdout.splitlines()[-1])
        result = self.run_script("project-python", str(project))
        self.assertIn("配置已一致", result.stdout)
        self.assertIn("提示: 未找到", result.stdout.splitlines()[-1])
        self.create(project / ".venv/bin/python")
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("提示: 未找到", result.stdout)
        self.assertEqual(jsonc.load_settings(target.read_text())["python.defaultInterpreterPath"], "${workspaceFolder}/.venv/bin/python")

    def test_existing_venv_directory_is_proposed_as_executable_without_preview_write(self) -> None:
        project = self.project()
        self.create(project / "backend/.venv/bin/python")
        target = project / ".vscode/settings.json"
        original = '{"python.defaultInterpreterPath":"${workspaceFolder}/backend/.venv"}'
        self.create(target, original)
        parser = application.build_parser()
        with patch.object(application, "CONFIG_DIR", self.fixture):
            plan = application.prepare_plan(parser.parse_args([
                "project-python", str(project), "--python-root", "backend",
            ]))
        self.assertEqual(plan.existing["python.defaultInterpreterPath"], "${workspaceFolder}/backend/.venv")
        self.assertEqual(plan.desired["python.defaultInterpreterPath"], "${workspaceFolder}/backend/.venv/bin/python")
        self.assertEqual(target.read_text(), original)

    def test_extra_project_values_survive_and_explicit_paths_define_suggestions(self) -> None:
        project = self.project()
        self.create(project / "tests/test_one.py")
        self.create(project / "integration/test_two.py")
        self.create(project / ".vscode/settings.json", json.dumps({
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests", "-q"],
            "python.analysis.extraPaths": ["custom"],
            "private.setting": True,
        }))
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        file = project / ".vscode/settings.json"
        values = jsonc.load_settings(file.read_text())
        self.assertEqual(values["python.testing.pytestArgs"], ["tests", "-s", "-v", "--tb=short"])
        self.assertEqual(values["python.analysis.extraPaths"], ["${workspaceFolder}"])
        result = self.run_script("project-python", str(project), "--test-dir", "integration", "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings(file.read_text())
        self.assertEqual(values["python.testing.pytestArgs"][0], "integration")
        self.assertTrue(values["private.setting"])

    def test_declared_multiple_test_directories_and_unittest_override(self) -> None:
        project = self.project()
        self.create(project / "pyproject.toml", '[tool.pytest.ini_options]\ntestpaths = ["tests", "integration"]\n')
        self.create(project / "tests/test_one.py")
        self.create(project / "integration/test_two.py")
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        file = project / ".vscode/settings.json"
        values = jsonc.load_settings(file.read_text())
        self.assertEqual(values["python.testing.pytestArgs"][:2], ["tests", "integration"])
        self.assertEqual(values[application.PATTERN_KEY], "{${workspaceFolder}/tests/**/*.py,${workspaceFolder}/integration/**/*.py}")
        result = self.run_script("project-python", str(project), "--test-dir", "tests", "--test-framework", "unittest", "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings(file.read_text())
        self.assertTrue(values["python.testing.unittestEnabled"])
        self.assertFalse(values["python.testing.pytestEnabled"])
        self.assertEqual(values["python.testing.unittestArgs"], ["-v", "-s", "tests", "-p", "test*.py"])

    def test_project_root_is_default_even_with_backend_metadata(self) -> None:
        project = self.project()
        self.create(project / "pyproject.toml")
        self.create(project / "backend/pyproject.toml")
        result = self.run_script("project-python", str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Python 根目录: .", result.stdout)
        outside = self.root / "outside"
        outside.mkdir()
        result = self.run_script("project-python", str(project), "--python-root", ".", "--test-dir", "../outside", "--write")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((project / ".vscode").exists())

    def test_invalid_documents_and_symlinks_are_not_overwritten(self) -> None:
        target = self.root / "settings.json"
        self.user_source.write_text('{"a":1,"a":2}', encoding="utf-8")
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(target.exists())
        self.user_source.write_text('{"a":1}', encoding="utf-8")
        target.write_text('{"broken":', encoding="utf-8")
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), '{"broken":')
        target.unlink()
        real = self.root / "real.json"
        real.write_text("{}", encoding="utf-8")
        target.symlink_to(real)
        result = self.run_script("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(target.is_symlink())
        self.assertEqual(real.read_text(), "{}")

    def test_user_menu_applies_template_after_review(self) -> None:
        target = self.root / "settings.json"
        result = self.run_script(input_text=f"3\n{target}\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("选择要应用", result.stdout)
        self.assertEqual(jsonc.load_settings(target.read_text())["editor.fontSize"], 14)

    def test_menu_previews_diff_by_default_before_write_confirmation(self) -> None:
        target = self.root / "settings.json"
        for confirm in ("", "y", "Y", "n", "N", "invalid"):
            with self.subTest(confirm=confirm):
                target.unlink(missing_ok=True)
                result = self.run_script(input_text=f"3\n{target}\n\n{confirm}\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("1. 全部应用", result.stdout)
                self.assertEqual(result.stdout.count("来源: "), 1)
                self.assertLess(result.stdout.index("同名值不同"), result.stdout.index("应用后: "))
                self.assertLess(result.stdout.index("应用后: "), result.stdout.index("如何处理这些配置"))
                self.assertEqual(result.stdout.count("当前值: "), 3)
                self.assertLess(result.stdout.index("应用后: "), result.stdout.index("预览完成, 是否写入"))
                self.assertNotIn("@@", result.stdout)
                self.assertIn("是否写入以上配置? [Y/n]", result.stdout)
                self.assertEqual(target.exists(), confirm.lower() in {"", "y"})

    def test_individual_mode_and_cancel_leave_existing_file_unchanged(self) -> None:
        self.user_source.write_text('{"a":2}', encoding="utf-8")
        target = self.root / "settings.json"
        target.write_text('{"a":1}', encoding="utf-8")
        before = target.read_bytes(), target.stat().st_mtime_ns
        for answers in ("0\n", "2\n\n", "1\nn\n"):
            with self.subTest(answers=answers):
                result = self.run_script(input_text=f"3\n{target}\n{answers}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), before)
                self.assertLess(result.stdout.index("应用后: 2"), result.stdout.index("如何处理这些配置"))
                if answers == "0\n":
                    self.assertIn("已取消", result.stdout)
                    self.assertNotIn("是否写入以上配置", result.stdout)
                elif answers == "2\n\n":
                    self.assertIn("保留: 1 项", result.stdout)
                    self.assertIn("未选择任何改动", result.stdout)

    def test_individual_choices_write_only_selected_nested_values_and_arrays(self) -> None:
        template = {"same": 1, "update": 2, "keep": True, "nested": {"old": 1, "new": 9}, "array": [2], "fresh": 5}
        existing = {"same": 1, "update": 1, "keep": False, "nested": {"old": 0, "extra": 7}, "array": [1]}
        self.user_source.write_text(json.dumps(template), encoding="utf-8")
        target = self.root / "settings.json"
        original = "// 保留注释\n" + json.dumps(existing)
        target.write_text(original, encoding="utf-8")
        inputs = f"3\n{target}\n2\n2\n\n2\n\n2\n\n"
        result = self.run_script(input_text=inputs + "n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_text(), original)
        result = self.run_script(input_text=inputs + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(jsonc.load_settings(target.read_text()), {
            **existing, "update": 2, "nested": {"old": 1, "extra": 7}, "array": [2],
        })
        self.assertIn("// 保留注释", target.read_text())
        self.assertIn("新增设置: 2 项; 同名值不同: 4 项", result.stdout)
        self.assertIn("新增: 0 项; 修改: 3 项; 保留: 1 项; 跳过新增: 2 项", result.stdout)
        self.assertLess(result.stdout.index("同名值不同"), result.stdout.index("如何处理这些配置"))

    def test_all_skipped_or_eof_does_not_create_target(self) -> None:
        self.user_source.write_text('{"new":{"a":1,"b":2}}', encoding="utf-8")
        target = self.root / "empty/settings.json"
        for answers in ("2\n\n\n", "2\n2\n", "1\n"):
            with self.subTest(answers=answers):
                result = self.run_script(input_text=f"3\n{target}\n{answers}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(target.parent.exists())

    def test_new_object_children_are_independent_and_invalid_choice_retries(self) -> None:
        self.user_source.write_text('{"new":{"a":1,"b":2}}', encoding="utf-8")
        target = self.root / "settings.json"
        result = self.run_script(input_text=f"3\n{target}\ninvalid\n2\ninvalid\n2\n\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(jsonc.load_settings(target.read_text()), {"new": {"a": 1}})
        self.assertIn("请输入 1, 2 或 0", result.stdout)
        self.assertIn("请输入 1 或 2", result.stdout)
        self.assertIn("新增: 1 项; 修改: 0 项; 保留: 0 项; 跳过新增: 1 项", result.stdout)

    def test_default_menu_is_python_and_default_processing_applies_all_after_confirmation(self) -> None:
        project = self.project()
        result = self.run_script(input_text=f"\n{project}\n\n\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1. Python 项目配置 (默认)", result.stdout)
        self.assertIn("2. Go 项目配置", result.stdout)
        self.assertIn("3. 用户配置", result.stdout)
        self.assertIn("settings-project-python.jsonc", result.stdout)
        self.assertFalse((project / ".vscode").exists())

    def test_change_collection_preserves_extra_keys_and_handles_atomic_type_changes(self) -> None:
        before = {"nested": {"extra": 1}, "typed": True, "object": 1, "array": [1], "slash/key": None}
        proposed = {"nested": {}, "typed": 1, "object": {"new": 2}, "array": [2, 3], "slash/key": "value"}
        changes = application.collect_changes(before, proposed)
        self.assertEqual([change.path for change in changes], [("typed",), ("object",), ("array",), ("slash/key",)])
        self.assertEqual(application.selected_settings(before, changes), {
            "nested": {"extra": 1}, "typed": 1, "object": {"new": 2}, "array": [2, 3], "slash/key": "value",
        })
        self.assertIs(before["typed"], True)

    def test_readable_changes_include_nested_updates_and_exclude_unchanged_values(self) -> None:
        with patch("builtins.print") as output:
            application.display_changes(
                {"python.terminal.useEnvFile": True, "nested": {"x": 1, "kept": 7}},
                {"python.terminal.useEnvFile": False, "nested": {"x": 2, "kept": 7}, "new": []},
            )
        text = "\n".join(call.args[0] for call in output.call_args_list)
        self.assertIn("终端自动加载环境文件", text)
        self.assertIn("当前值: true", text)
        self.assertIn("应用后: false", text)
        self.assertIn("nested / x", text)
        self.assertNotIn("kept", text)
        self.assertIn("未在此文件设置", text)

    def test_project_directory_link_cannot_write_outside_project(self) -> None:
        project = self.project()
        shared = self.root / "shared"
        shared.mkdir()
        (project / ".vscode").symlink_to(shared, target_is_directory=True)
        result = self.run_script("project-python", str(project), "--write")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((shared / "settings.json").exists())

    def test_changed_parent_link_invalidates_preview(self) -> None:
        folder = self.root / "profile"
        folder.mkdir()
        target = folder / "settings.json"
        parser = application.build_parser()
        with patch.object(application, "CONFIG_DIR", self.fixture):
            plan = application.prepare_plan(parser.parse_args(["user", "--target", str(target)]))
        folder.rmdir()
        shared = self.root / "shared"
        shared.mkdir()
        folder.symlink_to(shared, target_is_directory=True)
        with self.assertRaises(ValueError):
            application.apply_plan(plan, True)
        self.assertFalse((shared / "settings.json").exists())

    def test_project_menu_can_cancel_after_preview(self) -> None:
        project = self.project()
        result = self.run_script(input_text=f"1\n{project}\n\n1\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("仅预览", result.stdout)
        self.assertFalse((project / ".vscode").exists())

    def test_project_menu_writes_only_the_entered_project(self) -> None:
        project = self.project("project with spaces")
        result = self.run_script(input_text=f"1\n{project}\n\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / ".vscode/settings.json").is_file())
        self.assertFalse((self.root / ".vscode").exists())

    def test_ambiguous_environment_files_require_a_choice(self) -> None:
        project = self.project()
        self.create(project / "backend/pyproject.toml")
        self.create(project / ".env", "FAKE_SECRET=one")
        self.create(project / "backend/.env", "FAKE_SECRET=two")
        result = self.run_script("project-python", str(project), "--python-root", "backend", "--write")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((project / ".vscode").exists())
        result = self.run_script("project-python", str(project), "--python-root", "backend", "--no-env", "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = jsonc.load_settings((project / ".vscode/settings.json").read_text())
        self.assertFalse(values["python.terminal.useEnvFile"])
        self.assertNotIn("python.envFile", values)

    def test_stale_plan_refuses_to_overwrite_new_target_content(self) -> None:
        target = self.root / "settings.json"
        target.write_text("{}", encoding="utf-8")
        target.write_text('{"newer":true}', encoding="utf-8")
        with self.assertRaises(ValueError):
            application.write_settings(target, "{}", '{"planned":true}')
        self.assertEqual(target.read_text(), '{"newer":true}')

    def test_default_user_paths_cover_supported_platforms(self) -> None:
        with patch.object(application.Path, "home", return_value=self.root):
            with patch.object(application.sys, "platform", "darwin"):
                self.assertEqual(application.user_settings_path(), self.root / "Library/Application Support/Code/User/settings.json")
            with patch.object(application.sys, "platform", "linux"), patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "xdg")}):
                self.assertEqual(application.user_settings_path(), self.root / "xdg/Code/User/settings.json")
            with patch.object(application.sys, "platform", "linux"), patch.dict(os.environ, {"XDG_CONFIG_HOME": ""}):
                self.assertEqual(application.user_settings_path(), self.root / ".config/Code/User/settings.json")
            with (
                patch.object(application.sys, "platform", "linux"),
                patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative"}),
                self.assertRaises(ValueError),
            ):
                application.user_settings_path()
            with patch.object(application.sys, "platform", "win32"), patch.dict(os.environ, {"APPDATA": str(self.root / "appdata")}):
                self.assertEqual(application.user_settings_path(), self.root / "appdata/Code/User/settings.json")


if __name__ == "__main__":
    unittest.main()
