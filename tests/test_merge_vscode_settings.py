from __future__ import annotations

import glob
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parents[1] / "tool-configs" / "vscode"
SCRIPT_PATH = Path(__file__).parents[1] / "scripts/vscode/merge-settings.py"
SPEC = importlib.util.spec_from_file_location("merge_vscode_settings", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
settings_merger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(settings_merger)


class ConfigurationSplitTest(unittest.TestCase):
    def test_user_defaults_keep_python_and_go_editing_preferences(self) -> None:
        user = settings_merger.merge_settings(BASE_DIR, "user")
        self.assertFalse(user["[python]"]["editor.formatOnSave"])
        self.assertEqual(
            user["[python]"]["editor.codeActionsOnSave"],
            {
                "source.fixAll.ruff": "never",
                "source.organizeImports.ruff": "never",
            },
        )
        self.assertTrue(user["[go]"]["editor.formatOnSave"])
        self.assertEqual(user["[go]"]["editor.defaultFormatter"], "golang.go")
        self.assertTrue(user["ruff.enable"])
        self.assertEqual(user["ruff.configurationPreference"], "editorOnly")
        self.assertEqual(user["ruff.configuration"]["line-length"], 88)
        self.assertEqual(user["ruff.configuration"]["lint"]["ignore"], ["I001", "E501"])
        self.assertIn(
            "fastapi.Depends",
            user["ruff.configuration"]["lint"]["flake8-bugbear"]["extend-immutable-calls"],
        )

    def test_user_defaults_do_not_impose_project_environment_or_test_layout(self) -> None:
        user = settings_merger.merge_settings(BASE_DIR, "user")
        self.assertFalse(any(key.startswith("python.testing.") for key in user))
        for key in (
            "python.envFile",
            "python.terminal.useEnvFile",
            "python.analysis.extraPaths",
            "python.analysis.exclude",
            "go.testFlags",
            "go.testTimeout",
            "go.testEnvVars",
            "go.buildFlags",
            "go.buildTags",
            "go.lintFlags",
            "yaml.customTags",
        ):
            self.assertNotIn(key, user)
        self.assertNotIn("buildFlags", user["gopls"])
        self.assertNotIn("env", user["gopls"])
        for platform in ("windows", "linux", "osx"):
            self.assertNotIn("GOFLAGS", user[f"terminal.integrated.env.{platform}"])

    def test_user_plus_project_preserves_source_explicit_setting_values(self) -> None:
        """保证源模板显式值在合并后不变，允许统一用户默认增加生效项。"""
        user = settings_merger.merge_settings(BASE_DIR, "user")
        for language in ("python", "golang"):
            with self.subTest(language=language):
                project = settings_merger.merge_settings(BASE_DIR, f"project-{language}")
                effective = settings_merger.deep_merge(user, project)
                explicit: dict[str, object] = {}
                for source in (
                    BASE_DIR / "common/settings.jsonc",
                    BASE_DIR / language / "settings.jsonc",
                    BASE_DIR / "common/project-settings.jsonc",
                    BASE_DIR / language / "project-settings.jsonc",
                ):
                    explicit = settings_merger.deep_merge(
                        explicit,
                        settings_merger.parse_jsonc(source),
                    )
                self.assertEqual({key: effective[key] for key in explicit}, explicit)

    def test_python_auto_discovery_patterns_cover_hidden_workspaces(self) -> None:
        project = settings_merger.merge_settings(BASE_DIR, "project-python")
        key = "python.testing.autoTestDiscoverOnSavePattern"
        layouts = (
            ("template", project, "tests", "backend/tests"),
            (
                "backend",
                settings_merger.deep_merge(
                    project,
                    {key: "${workspaceFolder}/backend/tests/**/*.py"},
                ),
                "backend/tests",
                "tests",
            ),
        )
        workspace_paths = (
            "project",
            "My Project",
            ".codex/worktrees/project",
            ".hidden/worktrees/My Project",
        )
        with tempfile.TemporaryDirectory(prefix="agent-task.") as temporary:
            directory = Path(temporary).resolve()
            for layout, settings, test_directory, other_tests in layouts:
                for workspace_path in workspace_paths:
                    with self.subTest(layout=layout, workspace=workspace_path):
                        workspace = directory / layout / workspace_path
                        expected = {
                            workspace / test_directory / relative
                            for relative in (
                                "test_root.py",
                                "unit/test_nested.py",
                                "unit/deep/test_deep.py",
                            )
                        }
                        excluded = {
                            workspace / test_directory / "test_data.txt",
                            workspace / "src/main.py",
                            workspace / other_tests / "test_other.py",
                        }
                        for path in expected | excluded:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text("", encoding="utf-8")
                        pattern = settings[key].replace(
                            "${workspaceFolder}", workspace.as_posix()
                        )
                        self.assertTrue(Path(pattern).is_absolute())
                        matches = {
                            Path(path) for path in glob.glob(pattern, recursive=True)
                        }
                        self.assertEqual(matches, expected)

    def test_user_defaults_extend_notebook_and_file_type_settings_across_projects(self) -> None:
        user = settings_merger.merge_settings(BASE_DIR, "user")
        cases = (
            ("python", "[makefile]", {"editor.insertSpaces": False, "editor.tabSize": 4}),
            ("python", "[dockerfile]", {"editor.tabSize": 4, "editor.insertSpaces": True}),
            ("python", "[go]", user["[go]"]),
            ("golang", "[python]", user["[python]"]),
            ("golang", "notebook.formatOnSave.enabled", False),
            (
                "golang",
                "notebook.codeActionsOnSave",
                {
                    "notebook.source.fixAll": "explicit",
                    "notebook.source.organizeImports": "explicit",
                },
            ),
        )
        for language, key, expected in cases:
            with self.subTest(language=language, key=key):
                project = settings_merger.merge_settings(BASE_DIR, f"project-{language}")
                language_defaults = settings_merger.parse_jsonc(BASE_DIR / language / "settings.jsonc")
                effective = settings_merger.deep_merge(user, project)
                self.assertNotIn(key, language_defaults)
                self.assertNotIn(key, project)
                self.assertIn(key, user)
                self.assertEqual(effective[key], expected)

    def test_project_can_override_cross_project_defaults_without_losing_other_values(self) -> None:
        user = settings_merger.merge_settings(BASE_DIR, "user")
        project = {
            "notebook.formatOnSave.enabled": True,
            "notebook.codeActionsOnSave": {"notebook.source.fixAll": "never"},
            "[makefile]": {"editor.tabSize": 8},
            "[dockerfile]": {"editor.insertSpaces": False},
        }
        effective = settings_merger.deep_merge(user, project)
        self.assertTrue(effective["notebook.formatOnSave.enabled"])
        self.assertEqual(
            effective["notebook.codeActionsOnSave"],
            {
                "notebook.source.fixAll": "never",
                "notebook.source.organizeImports": "explicit",
            },
        )
        self.assertEqual(
            effective["[makefile]"],
            {"editor.insertSpaces": False, "editor.tabSize": 8},
        )
        self.assertEqual(
            effective["[dockerfile]"],
            {"editor.tabSize": 4, "editor.insertSpaces": False},
        )
        self.assertFalse(user["notebook.formatOnSave.enabled"])
        self.assertEqual(user["[makefile]"]["editor.tabSize"], 4)

    def test_go_overlay_keeps_common_terminal_environment_and_gopls_preferences(self) -> None:
        user = settings_merger.merge_settings(BASE_DIR, "user")
        project = settings_merger.merge_settings(BASE_DIR, "project-golang")
        effective = settings_merger.deep_merge(user, project)
        for platform in ("windows", "linux", "osx"):
            self.assertEqual(
                effective[f"terminal.integrated.env.{platform}"],
                {
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "GOFLAGS": "-mod=mod",
                },
            )
        self.assertTrue(effective["gopls"]["completeUnimported"])
        self.assertEqual(effective["gopls"]["buildFlags"], [])
        self.assertEqual(effective["gopls"]["env"], {})
        self.assertEqual(effective["go.testFlags"], ["-v", "-race"])
        self.assertEqual(effective["go.testTimeout"], "30s")

    def test_project_override_replaces_arrays_and_preserves_other_object_values(self) -> None:
        defaults = {
            "python.testing.pytestArgs": ["tests", "-s", "-v"],
            "[python]": {
                "editor.formatOnSave": False,
                "editor.defaultFormatter": "charliermarsh.ruff",
            },
        }
        project = {
            "python.testing.pytestArgs": ["integration", "-q"],
            "[python]": {"editor.formatOnSave": True},
        }
        effective = settings_merger.deep_merge(defaults, project)
        self.assertEqual(effective["python.testing.pytestArgs"], ["integration", "-q"])
        self.assertEqual(
            effective["[python]"],
            {
                "editor.formatOnSave": True,
                "editor.defaultFormatter": "charliermarsh.ruff",
            },
        )
        self.assertFalse(defaults["[python]"]["editor.formatOnSave"])
        effective["python.testing.pytestArgs"].append("-x")
        self.assertEqual(project["python.testing.pytestArgs"], ["integration", "-q"])

    def test_unknown_generation_target_is_rejected(self) -> None:
        for target in ("unknown", "python", "golang"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                settings_merger.merge_settings(BASE_DIR, target)


class GeneratorCommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agent-task.")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        repository = root / "repository with spaces"
        self.fixture = repository / "tool-configs/vscode"
        self.fixture.mkdir(parents=True)
        self.script = repository / "scripts/vscode/merge-settings.py"
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT_PATH, self.script)
        for source in BASE_DIR.glob("*/*.jsonc"):
            destination = self.fixture / source.relative_to(BASE_DIR)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        self.project = root / "project"
        (self.project / ".vscode").mkdir(parents=True)
        self.project_settings = self.project / ".vscode" / "settings.json"
        self.project_settings.write_text('{"project.private": true}\n', encoding="utf-8")
        self.home = root / "home"
        self.user_settings = self.home / "Library/Application Support/Code/User/settings.json"
        self.user_settings.parent.mkdir(parents=True)
        self.user_settings.write_text('{"machine.private": true}\n', encoding="utf-8")

    def run_generator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(self.home)
        result = subprocess.run(
            [sys.executable, "-B", str(self.script), *arguments],
            cwd=self.project,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            self.project_settings.read_text(encoding="utf-8"),
            '{"project.private": true}\n',
        )
        self.assertEqual(
            self.user_settings.read_text(encoding="utf-8"),
            '{"machine.private": true}\n',
        )
        return result

    def test_default_command_generates_three_outputs_with_real_source_headers(self) -> None:
        result = self.run_generator()
        self.assertEqual(result.returncode, 0, result.stderr)
        targets = {"user", "project-python", "project-golang"}
        self.assertEqual(
            {path.name for path in self.fixture.glob("*.jsonc")},
            {f"settings-{target}.jsonc" for target in targets},
        )
        for target in targets:
            output = self.fixture / f"settings-{target}.jsonc"
            self.assertEqual(
                settings_merger.parse_jsonc(output),
                settings_merger.merge_settings(BASE_DIR, target),
            )
            header = output.read_text(encoding="utf-8").splitlines()[3]
            self.assertIn("scripts/vscode/merge-settings.py", output.read_text(encoding="utf-8").splitlines()[2])
            self.assertNotIn("{lang}", header)
            for source in settings_merger.get_source_files(target):
                self.assertIn(source, header)

    def test_flags_only_generate_requested_outputs(self) -> None:
        cases = (
            (("--user",), {"user"}),
            (("--project-python",), {"project-python"}),
            (("--project-golang",), {"project-golang"}),
            (("--project-python", "--project-golang"), {"project-python", "project-golang"}),
            (("--user", "--project-python"), {"user", "project-python"}),
        )
        for arguments, targets in cases:
            with self.subTest(arguments=arguments):
                for path in self.fixture.glob("*.jsonc"):
                    path.unlink()
                result = self.run_generator(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    {path.name for path in self.fixture.glob("*.jsonc")},
                    {f"settings-{target}.jsonc" for target in targets},
                )

    def test_unknown_flag_fails_without_writing_outputs(self) -> None:
        for option in ("--unknown", "--python", "--golang"):
            with self.subTest(option=option):
                result = self.run_generator(option)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(self.fixture.glob("*.jsonc")), [])


if __name__ == "__main__":
    unittest.main()
