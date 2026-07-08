from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "update_git_repos.py"
SPEC = importlib.util.spec_from_file_location("update_git_repos", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
update_git_repos = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = update_git_repos
SPEC.loader.exec_module(update_git_repos)


def completed(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["git"], returncode, stdout, stderr)


class UpdateRepositoryTest(unittest.TestCase):
    def test_run_git_kills_process_group_on_timeout(self) -> None:
        process = Mock(pid=1234, args=["git"])
        process.communicate.side_effect = [
            subprocess.TimeoutExpired(["git"], 0.01),
            ("", ""),
        ]

        with (
            patch.object(update_git_repos.subprocess, "Popen", return_value=process),
            patch.object(update_git_repos.os, "killpg") as killpg,
        ):
            with self.assertRaises(update_git_repos.CommandTimedOutError):
                update_git_repos.run_git(Path("/repo"), "pull", timeout=0.01)

        killpg.assert_called_once_with(1234, update_git_repos.signal.SIGKILL)
        self.assertEqual(process.communicate.call_count, 2)

    def test_updates_clean_branch_with_upstream(self) -> None:
        responses = [
            completed(),
            completed(stdout="main\n"),
            completed(stdout="origin/main\n"),
            completed(stdout="Already up to date.\n"),
        ]

        with patch.object(update_git_repos, "run_git", side_effect=responses) as run_git:
            result = update_git_repos.update_repository(Path("/repo"), 10)

        self.assertEqual(result.kind, update_git_repos.ResultKind.UPDATED)
        self.assertEqual(run_git.call_args_list[-1].kwargs["timeout"], 10)

    def test_skips_dirty_repository_without_pull(self) -> None:
        with patch.object(
            update_git_repos,
            "run_git",
            return_value=completed(stdout="?? local.txt\n"),
        ) as run_git:
            result = update_git_repos.update_repository(Path("/repo"), 10)

        self.assertEqual(result.kind, update_git_repos.ResultKind.MANUAL)
        run_git.assert_called_once()

    def test_marks_pull_failure_for_manual_intervention(self) -> None:
        responses = [
            completed(),
            completed(stdout="main\n"),
            completed(stdout="origin/main\n"),
            completed(
                returncode=128,
                stderr="fatal: Not possible to fast-forward\n",
            ),
        ]

        with patch.object(update_git_repos, "run_git", side_effect=responses):
            result = update_git_repos.update_repository(Path("/repo"), 10)

        self.assertEqual(result.kind, update_git_repos.ResultKind.MANUAL)
        self.assertIn("Not possible to fast-forward", result.detail)

    def test_marks_pull_timeout_and_continues(self) -> None:
        responses = [
            completed(),
            completed(stdout="main\n"),
            completed(stdout="origin/main\n"),
            update_git_repos.CommandTimedOutError(),
        ]

        with patch.object(update_git_repos, "run_git", side_effect=responses):
            result = update_git_repos.update_repository(Path("/repo"), 10)

        self.assertEqual(result.kind, update_git_repos.ResultKind.TIMED_OUT)


class WorkspaceRootConfigTest(unittest.TestCase):
    def test_color_auto_disables_for_non_tty_stream(self) -> None:
        self.assertFalse(update_git_repos.should_use_color("auto", io.StringIO()))

    def test_color_always_adds_ansi_codes(self) -> None:
        text = update_git_repos.badge("OK", "green", use_color=True)

        self.assertIn("\033[", text)
        self.assertIn("[OK]", text)

    def test_print_summary_only_outputs_counts(self) -> None:
        results = [
            update_git_repos.RepoResult(
                Path("/repo"),
                update_git_repos.ResultKind.UPDATED,
                "main <- origin/main",
            )
        ]
        output = io.StringIO()

        with redirect_stdout(output):
            update_git_repos.print_summary(results, use_color=False)

        output_text = output.getvalue()
        self.assertNotIn("[RESULTS]", output_text)
        self.assertNotIn("[UPDATED] /repo", output_text)
        self.assertIn("[SUMMARY] total=1 updated=1 skipped=0 timeout=0", output_text)

    def test_loads_absolute_existing_workspace_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace_root = Path(temporary_directory)
            config_file = workspace_root / ".workspace-root"
            config_file.write_text(f"{workspace_root}\n", encoding="utf-8")

            root = update_git_repos.load_workspace_root(config_file)

        self.assertEqual(root, workspace_root.resolve())

    def test_rejects_missing_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_file = Path(temporary_directory) / ".workspace-root"

            with self.assertRaises(update_git_repos.WorkspaceRootConfigError):
                update_git_repos.load_workspace_root(config_file)

    def test_rejects_relative_workspace_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_file = Path(temporary_directory) / ".workspace-root"
            config_file.write_text("relative/path\n", encoding="utf-8")

            with self.assertRaises(update_git_repos.WorkspaceRootConfigError):
                update_git_repos.load_workspace_root(config_file)

    def test_rejects_missing_workspace_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_file = Path(temporary_directory) / ".workspace-root"
            config_file.write_text(
                f"{Path(temporary_directory) / 'missing'}\n",
                encoding="utf-8",
            )

            with self.assertRaises(update_git_repos.WorkspaceRootConfigError):
                update_git_repos.load_workspace_root(config_file)

    def test_main_requires_confirmation_before_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace_root = Path(temporary_directory)
            with (
                patch.object(
                    update_git_repos,
                    "load_workspace_root",
                    return_value=workspace_root,
                ),
                patch.object(
                    update_git_repos,
                    "confirm_workspace_root",
                    return_value=False,
                ),
                patch.object(
                    update_git_repos,
                    "discover_repositories",
                ) as discover_repositories,
                patch.object(
                    update_git_repos.shutil,
                    "which",
                    return_value="/usr/bin/git",
                ),
            ):
                with (
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(io.StringIO()),
                ):
                    exit_code = update_git_repos.main([])

        self.assertEqual(exit_code, 1)
        discover_repositories.assert_not_called()

    def test_main_updates_after_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace_root = Path(temporary_directory)
            repo = workspace_root / "repo"
            repo.mkdir()
            result = update_git_repos.RepoResult(
                repo,
                update_git_repos.ResultKind.UPDATED,
                "main <- origin/main",
            )
            with (
                patch.object(
                    update_git_repos,
                    "load_workspace_root",
                    return_value=workspace_root,
                ),
                patch.object(
                    update_git_repos,
                    "confirm_workspace_root",
                    return_value=True,
                ),
                patch.object(
                    update_git_repos,
                    "discover_repositories",
                    return_value=[repo],
                ),
                patch.object(
                    update_git_repos,
                    "update_repository",
                    return_value=result,
                ),
                patch.object(
                    update_git_repos.shutil,
                    "which",
                    return_value="/usr/bin/git",
                ),
            ):
                with (
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(io.StringIO()),
                ):
                    exit_code = update_git_repos.main([])

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
