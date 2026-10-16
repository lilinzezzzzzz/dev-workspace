from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
CONFIG_DIR = REPO_ROOT / "tool-configs/vscode"
SCRIPT_DIR = REPO_ROOT / "scripts/vscode"


@unittest.skipUnless(shutil.which("bash"), "Shell 入口需要 Bash")
class VscodeEntrypointTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="agent-task.")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repository = self.root / "repository with spaces"
        self.config = self.repository / "tool-configs/vscode"
        self.scripts = self.repository / "scripts/vscode"
        self.config.mkdir(parents=True)
        self.scripts.mkdir(parents=True)
        for source in CONFIG_DIR.glob("*/*.jsonc"):
            target = self.config / source.relative_to(CONFIG_DIR)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
        for source in SCRIPT_DIR.glob("*.py"):
            shutil.copyfile(source, self.scripts / source.name)
        self.entrypoint = self.config / "apply-config.sh"
        shutil.copy2(CONFIG_DIR / "apply-config.sh", self.entrypoint)
        self.cwd = self.root / "unrelated working directory"
        self.cwd.mkdir()
        self.log = self.root / "uv-calls.jsonl"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name in ("bash", "dirname", "cat"):
            command = shutil.which(name)
            assert command is not None
            (self.bin / name).symlink_to(command)
        dispatcher = self.root / "dispatch.py"
        dispatcher.write_text('''import json, os, subprocess, sys
from pathlib import Path
arguments = sys.argv[1:]
with Path(os.environ["TEST_UV_LOG"]).open("a") as stream:
    stream.write(json.dumps({"args": arguments, "cwd": os.getcwd()}) + "\\n")
assert arguments[:5] == ["run", "--project", os.environ["TEST_REPOSITORY"], "--locked", "python"], arguments
assert arguments[5] == "-B"
if arguments[6].endswith("merge-settings.py") and os.environ.get("TEST_GENERATOR_EXIT"):
    print("生成失败：测试错误", file=sys.stderr)
    raise SystemExit(int(os.environ["TEST_GENERATOR_EXIT"]))
raise SystemExit(subprocess.run([os.environ["TEST_PYTHON"], *arguments[5:]]).returncode)
''', encoding="utf-8")
        self.uv = self.bin / "uv"
        self.uv.write_text('#!/usr/bin/env bash\nexec "$TEST_PYTHON" -B "$TEST_DISPATCHER" "$@"\n', encoding="utf-8")
        self.uv.chmod(0o755)
        self.environment = {
            **os.environ,
            "PATH": str(self.bin),
            "TEST_PYTHON": sys.executable,
            "TEST_DISPATCHER": str(dispatcher),
            "TEST_REPOSITORY": str(self.repository),
            "TEST_UV_LOG": str(self.log),
        }

    def run_entrypoint(
        self,
        *arguments: str,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.entrypoint), *arguments],
            cwd=self.cwd,
            env=self.environment,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )

    def calls(self) -> list[dict[str, object]]:
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_default_entrypoint_generates_then_opens_menu_from_another_directory(self) -> None:
        result = self.run_entrypoint(input_text="y\n0\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("选择要应用", result.stdout)
        self.assertNotIn("已生成", result.stdout)
        self.assertNotIn("settings-user.jsonc", result.stdout)
        self.assertEqual(
            {path.name for path in self.config.glob("*.jsonc")},
            {"settings-user.jsonc", "settings-project-python.jsonc", "settings-project-golang.jsonc"},
        )
        calls = self.calls()
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0]["args"][6].endswith("merge-settings.py"))
        self.assertTrue(calls[1]["args"][6].endswith("apply-settings.py"))
        self.assertEqual([call["cwd"] for call in calls], [str(self.cwd)] * 2)
        self.assertFalse((self.cwd / ".vscode").exists())
        self.assertFalse(list(self.scripts.glob("*.jsonc")))

    def test_relative_project_path_and_arguments_are_forwarded_without_writing(self) -> None:
        project = self.cwd / "Python project with spaces"
        (project / "tests").mkdir(parents=True)
        arguments = ("project-python", project.name, "--test-dir", "tests", "--test-framework", "pytest")
        result = self.run_entrypoint(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(project / ".vscode/settings.json"), result.stdout)
        self.assertFalse((project / ".vscode").exists())
        self.assertEqual(self.calls()[1]["args"][7:], list(arguments))

    def test_skip_generation_uses_existing_files_without_refreshing(self) -> None:
        source = self.config / "settings-project-golang.jsonc"
        original = '{"go.testTimeout":"123s"}'
        source.write_text(original, encoding="utf-8")
        modified = source.stat().st_mtime_ns
        project = self.cwd / "go project"
        project.mkdir()
        result = self.run_entrypoint(input_text=f"n\n2\n{project}\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(source.read_text(), original)
        self.assertEqual(source.stat().st_mtime_ns, modified)
        self.assertEqual(json.loads((project / ".vscode/settings.json").read_text()), {"go.testTimeout": "123s"})

    def test_skip_missing_source_reports_error_without_generating(self) -> None:
        result = self.run_entrypoint(input_text="n\n3\n\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("来源不存在", result.stderr)
        self.assertEqual(len(self.calls()), 1)
        self.assertFalse(list(self.config.glob("*.jsonc")))

    def test_generation_prompt_retries_defaults_and_handles_eof(self) -> None:
        result = self.run_entrypoint(input_text="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.log.exists())
        self.assertFalse(list(self.config.glob("*.jsonc")))
        result = self.run_entrypoint(input_text="invalid\n\n0\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("请输入 y 或 n", result.stdout)
        self.assertIn("是否生成配置? [y/N]", result.stdout)
        self.assertEqual(len(self.calls()), 1)
        self.assertFalse(list(self.config.glob("*.jsonc")))

    def test_user_write_is_limited_to_explicit_temporary_target(self) -> None:
        target = self.cwd / "fake profile/settings.json"
        target.parent.mkdir()
        target.write_text('{"editor.fontSize":999,"machine.only":true}', encoding="utf-8")
        result = self.run_entrypoint("user", "--target", str(target), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(target.read_text())
        source = self.config / "settings-user.jsonc"
        self.assertNotEqual(values["editor.fontSize"], 999)
        self.assertTrue(values["machine.only"])
        self.assertTrue(source.is_file())

    def test_go_project_preview_conflicts_write_and_idempotence(self) -> None:
        project = self.cwd / "Go project with spaces"
        target = project / ".vscode/settings.json"
        target.parent.mkdir(parents=True)
        original = '{"go.testTimeout":"90s","gopls":{"env":{"CUSTOM":"value"}},"project.only":true}'
        target.write_text(original, encoding="utf-8")
        result = self.run_entrypoint("project-golang", project.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("settings-project-golang.jsonc", result.stdout)
        self.assertEqual(target.read_text(), original)
        result = self.run_entrypoint("project-golang", project.name, "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(target.read_text())
        self.assertEqual(values["go.testTimeout"], "30s")
        self.assertEqual(values["gopls"]["env"], {"CUSTOM": "value"})
        self.assertTrue(values["project.only"])
        self.assertFalse(any(key.startswith("python.") for key in values))
        arguments = ("project-golang", project.name, "--write")
        result = self.run_entrypoint(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(target.read_text())["go.testTimeout"], "30s")
        modified = target.stat().st_mtime_ns
        result = self.run_entrypoint(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.stat().st_mtime_ns, modified)

    def test_go_menu_requires_root_and_confirms_writing(self) -> None:
        result = self.run_entrypoint(input_text="y\n2\n\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("项目根目录不能为空", result.stderr)
        result = self.run_entrypoint("project-golang", "missing")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.cwd / "missing").exists())
        project = self.cwd / "go project"
        project.mkdir()
        result = self.run_entrypoint(input_text=f"y\n2\n{project}\n1\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((project / ".vscode").exists())
        self.assertNotIn("Python 根目录", result.stdout)
        result = self.run_entrypoint(input_text=f"y\n2\n{project}\n1\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads((project / ".vscode/settings.json").read_text())
        self.assertEqual(values["go.testFlags"], ["-v", "-race"])

    def test_go_menu_can_keep_conflicting_value_without_writing(self) -> None:
        project = self.cwd / "go project"
        project.mkdir()
        result = self.run_entrypoint("project-golang", str(project), "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = project / ".vscode/settings.json"
        values = json.loads(target.read_text())
        values["go.testTimeout"] = "90s"
        target.write_text(json.dumps(values), encoding="utf-8")
        before = target.read_bytes(), target.stat().st_mtime_ns
        result = self.run_entrypoint(input_text=f"n\n2\n{project}\n2\n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("保留: 1 项", result.stdout)
        self.assertIn("未选择任何改动", result.stdout)
        self.assertNotIn("是否写入以上配置", result.stdout)
        self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), before)

    def test_generate_only_keeps_selective_generation_behavior(self) -> None:
        result = self.run_entrypoint("--generate-only", "--user")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("已生成", result.stdout)
        self.assertIn("settings-user.jsonc", result.stdout)
        self.assertEqual([path.name for path in self.config.glob("*.jsonc")], ["settings-user.jsonc"])
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.calls()[0]["args"][-1], "--user")

    def test_generator_failure_stops_before_application(self) -> None:
        self.environment["TEST_GENERATOR_EXIT"] = "37"
        result = self.run_entrypoint(input_text="y\n1\n")
        self.assertEqual(result.returncode, 37)
        self.assertIn("生成失败：测试错误", result.stderr)
        self.assertEqual(len(self.calls()), 1)
        self.assertFalse(list(self.config.glob("*.jsonc")))

    def test_application_error_status_is_propagated(self) -> None:
        result = self.run_entrypoint("project-python")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(self.calls()), 2)
        self.assertFalse((self.cwd / ".vscode").exists())

    def test_help_works_without_uv_and_missing_uv_fails_without_generation(self) -> None:
        self.uv.unlink()
        result = self.run_entrypoint("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--generate-only", result.stdout)
        result = self.run_entrypoint()
        self.assertEqual(result.returncode, 127)
        self.assertIn("未找到 uv", result.stderr)
        self.assertFalse(list(self.config.glob("*.jsonc")))

    def test_subcommand_help_does_not_generate_files(self) -> None:
        result = self.run_entrypoint("user", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.calls()), 1)
        self.assertFalse(list(self.config.glob("*.jsonc")))


if __name__ == "__main__":
    unittest.main()
