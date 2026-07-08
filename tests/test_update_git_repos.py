from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
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
            completed(returncode=128, stderr="fatal: Not possible to fast-forward\n"),
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


if __name__ == "__main__":
    unittest.main()
