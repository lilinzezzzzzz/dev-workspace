#!/usr/bin/env python3
"""Restack the current branch onto the latest base branch with cherry-pick."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass


VERSION_SUFFIX_RE = re.compile(r"^(?P<name>.+)-v(?P<version>\d+)$")


@dataclass(frozen=True)
class Commit:
    sha: str
    subject: str


@dataclass(frozen=True)
class RestackPlan:
    base_branch: str
    source_branch: str
    new_branch: str
    base_ref: str
    base_ref_kind: str
    commits: list[Commit]
    fetch_executed: bool


@dataclass(frozen=True)
class BaseResolution:
    base_branch: str
    base_ref: str
    base_ref_kind: str
    remote: str | None
    remote_branch: str | None


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the completed process."""
    return subprocess.run(
        ["git", *args],
        check=check,
        text=True,
        capture_output=True,
    )


def git_output(*args: str) -> str:
    """Run a git command and return trimmed stdout."""
    result = run_git(*args)
    return result.stdout.strip()


def ensure_repo() -> None:
    """Fail fast when the current directory is not inside a git worktree."""
    try:
        git_output("rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.stderr.strip() or "Not inside a git repository.") from exc


def ensure_clean_worktree() -> None:
    """Require a clean worktree to avoid mixing unrelated state into the restack."""
    if git_output("status", "--porcelain"):
        raise SystemExit("Working tree is dirty. Commit or stash changes before restacking.")


def current_branch() -> str:
    """Return the currently checked out branch name."""
    branch = git_output("branch", "--show-current")
    if not branch:
        raise SystemExit("Detached HEAD is not supported. Check out a branch first.")
    return branch


def next_versioned_branch(source_branch: str) -> str:
    """Return the next versioned branch name using the repository's simple -vN convention."""
    match = VERSION_SUFFIX_RE.match(source_branch)
    if not match:
        return f"{source_branch}-v2"
    next_version = int(match.group("version")) + 1
    return f"{match.group('name')}-v{next_version}"


def fetch_base(*, remote: str, base: str) -> None:
    """Fetch the latest base branch from the remote."""
    try:
        run_git("fetch", remote, base)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "git fetch failed."
        raise SystemExit(message) from exc


def ensure_ref_exists(ref: str) -> None:
    """Fail if the expected git ref does not exist."""
    result = run_git("rev-parse", "--verify", ref, check=False)
    if result.returncode != 0:
        raise SystemExit(f"Git ref not found: {ref}")


def ref_exists(ref: str) -> bool:
    """Return whether a git ref exists."""
    return run_git("show-ref", "--verify", ref, check=False).returncode == 0


def list_remotes() -> list[str]:
    """Return configured git remotes."""
    output = git_output("remote")
    return [line for line in output.splitlines() if line]


def select_remote(*, requested_remote: str | None, remotes: list[str]) -> str:
    """Select the remote used for an unqualified base branch."""
    if requested_remote:
        if requested_remote not in remotes:
            raise SystemExit(f"Remote not found: {requested_remote}")
        return requested_remote
    if "origin" in remotes:
        return "origin"
    if len(remotes) == 1:
        return remotes[0]
    if not remotes:
        raise SystemExit(
            "No git remote found. Provide --base-ref only when you explicitly want a local ref."
        )
    raise SystemExit(
        "Multiple remotes found and no origin remote exists. Provide --remote explicitly: "
        + ", ".join(remotes)
    )


def resolve_base_ref(
    *,
    base: str,
    remote: str | None,
    base_ref: str | None,
) -> BaseResolution:
    """Resolve user base input to the effective base ref."""
    remotes = list_remotes()
    if base_ref:
        if base_ref.startswith("refs/heads/"):
            base_ref_kind = "local"
        elif base_ref.startswith("refs/remotes/") or ref_exists(f"refs/remotes/{base_ref}"):
            base_ref_kind = "remote-tracking"
        else:
            base_ref_kind = "explicit"
        return BaseResolution(
            base_branch=base,
            base_ref=base_ref,
            base_ref_kind=base_ref_kind,
            remote=None,
            remote_branch=None,
        )

    if base.startswith("refs/heads/"):
        return BaseResolution(
            base_branch=base,
            base_ref=base,
            base_ref_kind="local",
            remote=None,
            remote_branch=None,
        )

    if base.startswith("refs/remotes/"):
        remote_branch = base.removeprefix("refs/remotes/")
        remote_name, _, branch_name = remote_branch.partition("/")
        return BaseResolution(
            base_branch=base,
            base_ref=base,
            base_ref_kind="remote-tracking",
            remote=remote_name if remote_name in remotes and branch_name else None,
            remote_branch=branch_name or None,
        )

    remote_name, separator, branch_name = base.partition("/")
    if separator and (remote_name in remotes or ref_exists(f"refs/remotes/{base}")):
        return BaseResolution(
            base_branch=base,
            base_ref=base,
            base_ref_kind="remote-tracking",
            remote=remote_name if remote_name in remotes else None,
            remote_branch=branch_name if remote_name in remotes else None,
        )

    selected_remote = select_remote(requested_remote=remote, remotes=remotes)
    return BaseResolution(
        base_branch=base,
        base_ref=f"{selected_remote}/{base}",
        base_ref_kind="remote-tracking",
        remote=selected_remote,
        remote_branch=base,
    )


def collect_commits(*, base_ref: str, source_branch: str) -> list[Commit]:
    """Collect commits that exist on the source branch but not on the base ref."""
    output = git_output("log", "--reverse", "--format=%H%x09%s", f"{base_ref}..{source_branch}")
    commits: list[Commit] = []
    for line in output.splitlines():
        sha, subject = line.split("\t", 1)
        commits.append(Commit(sha=sha, subject=subject))
    return commits


def ensure_branch_absent(branch_name: str) -> None:
    """Avoid reusing an existing branch name."""
    result = run_git("show-ref", "--verify", f"refs/heads/{branch_name}", check=False)
    if result.returncode == 0:
        raise SystemExit(f"Branch already exists: {branch_name}")


def create_branch(*, new_branch: str, base_ref: str) -> None:
    """Create and check out the new branch from the base ref without inheriting upstream."""
    try:
        run_git("switch", "--no-track", "-c", new_branch, base_ref)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "Failed to create branch."
        raise SystemExit(message) from exc


def cherry_pick_commits(commits: list[Commit]) -> None:
    """Cherry-pick commits one by one to provide precise conflict reporting."""
    for commit in commits:
        result = run_git("cherry-pick", commit.sha, check=False)
        if result.returncode != 0:
            conflict_message = (
                f"Cherry-pick stopped on {commit.sha} {commit.subject}\n"
                "Resolve conflicts, then run `git cherry-pick --continue`, or abort with "
                "`git cherry-pick --abort`."
            )
            raise SystemExit(conflict_message)


def build_plan(
    *,
    source_branch: str,
    new_branch: str | None,
    base: str,
    remote: str | None,
    base_ref: str | None,
    skip_fetch: bool,
) -> RestackPlan:
    """Resolve the inputs into an executable restack plan."""
    base_resolution = resolve_base_ref(base=base, remote=remote, base_ref=base_ref)
    if (
        not skip_fetch
        and base_ref is None
        and base_resolution.remote is not None
        and base_resolution.remote_branch is not None
    ):
        fetch_base(remote=base_resolution.remote, base=base_resolution.remote_branch)
        fetch_executed = True
    else:
        fetch_executed = False
    ensure_ref_exists(base_resolution.base_ref)
    ensure_ref_exists(source_branch)

    resolved_new_branch = new_branch or next_versioned_branch(source_branch)
    commits = collect_commits(base_ref=base_resolution.base_ref, source_branch=source_branch)
    if not commits:
        raise SystemExit(
            f"No commits found in {source_branch} that are not already in {base_resolution.base_ref}."
        )

    return RestackPlan(
        base_branch=base_resolution.base_branch,
        source_branch=source_branch,
        new_branch=resolved_new_branch,
        base_ref=base_resolution.base_ref,
        base_ref_kind=base_resolution.base_ref_kind,
        commits=commits,
        fetch_executed=fetch_executed,
    )


def print_plan(plan: RestackPlan) -> None:
    """Print the planned restack steps in a human-readable form."""
    print(f"base_branch: {plan.base_branch}")
    print(f"source_branch: {plan.source_branch}")
    print(f"base_ref: {plan.base_ref}")
    print(f"base_ref_kind: {plan.base_ref_kind}")
    print(f"new_branch: {plan.new_branch}")
    print(f"fetch_executed: {'yes' if plan.fetch_executed else 'no'}")
    print("commits:")
    for commit in plan.commits:
        print(f"  - {commit.sha} {commit.subject}")
    print("commands:")
    print(f"  git switch --no-track -c {plan.new_branch} {plan.base_ref}")
    for commit in plan.commits:
        print(f"  git cherry-pick {commit.sha}")
    print("status: awaiting_confirmation")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Recreate a branch from the latest base branch and cherry-pick source-only commits.",
    )
    parser.add_argument(
        "--base",
        required=True,
        help="Base branch or remote-tracking ref, such as dev, main, origin/dev, or refs/heads/main",
    )
    parser.add_argument(
        "--remote",
        help="Remote for unqualified base branches. Default: origin when present, otherwise the sole remote",
    )
    parser.add_argument("--source-branch", help="Source branch to restack. Default: current branch")
    parser.add_argument("--new-branch", help="Override the generated versioned branch name")
    parser.add_argument(
        "--base-ref",
        help="Explicit git ref to use as base, such as origin/main, upstream/master, or refs/heads/main",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip `git fetch <remote> <base>` before building the plan",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow execution with a dirty worktree",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the restack after printing the plan",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Acknowledge that the printed branches were reviewed and execution may continue",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = parse_args()
    ensure_repo()
    if not args.allow_dirty:
        ensure_clean_worktree()

    source_branch = args.source_branch or current_branch()
    plan = build_plan(
        source_branch=source_branch,
        new_branch=args.new_branch,
        base=args.base,
        remote=args.remote,
        base_ref=args.base_ref,
        skip_fetch=args.skip_fetch,
    )
    print_plan(plan)

    if not args.apply:
        return
    if not args.confirm:
        raise SystemExit("`--apply` requires `--confirm` after the user reviews the branches.")

    ensure_branch_absent(plan.new_branch)
    create_branch(new_branch=plan.new_branch, base_ref=plan.base_ref)
    cherry_pick_commits(plan.commits)
    print("status: completed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted.")
