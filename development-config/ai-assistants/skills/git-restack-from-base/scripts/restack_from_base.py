#!/usr/bin/env python3
"""Restack the current branch onto the latest base branch using git rebase."""

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
    is_merge: bool
    is_signed: bool


@dataclass(frozen=True)
class RestackPlan:
    base_branch: str
    source_branch: str
    new_branch: str
    base_ref: str
    base_commit_sha: str
    base_ref_kind: str
    base_freshness: str
    commits: list[Commit]
    fetch_executed: bool
    has_merge_commits: bool
    signed_commit_count: int
    stacked_refs: list[str]


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


def ref_commit_sha(ref: str) -> str:
    """Return the commit SHA for a resolved git ref."""
    return git_output("rev-parse", "--verify", ref)


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
    """Collect commits that exist on the source branch but not on the base ref.

    The `%P` parent list is used to detect merge commits, because `git rebase`
    flattens merges by default and the user should be warned before apply.
    The `%G?` signature flag is used to detect GPG-signed commits, because
    plain rebase drops signatures unless a re-signing strategy is applied.
    """
    output = git_output(
        "log", "--reverse", "--format=%H%x09%P%x09%G?%x09%s", f"{base_ref}..{source_branch}"
    )
    commits: list[Commit] = []
    for line in output.splitlines():
        sha, parents, signature, subject = line.split("\t", 3)
        is_merge = len(parents.split()) > 1
        is_signed = signature in {"G", "U", "X", "Y", "R", "E"}
        commits.append(
            Commit(sha=sha, subject=subject, is_merge=is_merge, is_signed=is_signed)
        )
    return commits


def detect_stacked_refs(*, base_ref: str, source_branch: str) -> list[str]:
    """Find other local branches whose tip lies inside the branch-only range.

    When such refs exist, a plain rebase leaves them stranded on the pre-rebase
    commits. Git 2.38+ supports `git rebase --update-refs` to move them along,
    but we surface a warning instead of enabling it silently.
    """
    commits_output = git_output("log", "--format=%H", f"{base_ref}..{source_branch}")
    branch_commit_set = set(commits_output.splitlines())
    if not branch_commit_set:
        return []
    refs_output = git_output(
        "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/"
    )
    stacked: list[str] = []
    for line in refs_output.splitlines():
        if not line:
            continue
        name, _, sha = line.partition(" ")
        if name == source_branch:
            continue
        if sha in branch_commit_set:
            stacked.append(name)
    return stacked


def base_freshness(*, base_ref_kind: str, fetch_executed: bool) -> str:
    """Describe whether the base ref was freshly fetched or locally cached."""
    if base_ref_kind == "remote-tracking":
        return "fetched" if fetch_executed else "local-cached"
    return base_ref_kind


def ensure_branch_absent(branch_name: str) -> None:
    """Avoid reusing an existing branch name."""
    result = run_git("show-ref", "--verify", f"refs/heads/{branch_name}", check=False)
    if result.returncode == 0:
        raise SystemExit(f"Branch already exists: {branch_name}")


def create_branch_from_source(*, new_branch: str, source_branch: str) -> None:
    """Create and check out the new branch from the source branch as a safety-net copy."""
    try:
        run_git("switch", "--no-track", "-c", new_branch, source_branch)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "Failed to create branch."
        raise SystemExit(message) from exc


def rebase_onto_base(*, base_ref: str) -> None:
    """Rebase the branch-only commits onto the latest base ref in a single atomic step.

    `--empty=drop` guarantees deterministic handling of commits whose changes
    already exist in the new base; without it, older git versions stop the
    rebase and newer versions may keep or drop depending on configuration.
    """
    result = run_git(
        "rebase", "--empty=drop", "--onto", base_ref, base_ref, check=False
    )
    if result.returncode != 0:
        conflict_message = (
            "Rebase stopped before completing. The most common cause is a merge conflict,\n"
            "but it may also be a pre-rebase hook rejection or another git-side error.\n"
            "Check the git output above for the exact reason.\n"
            "For conflicts: resolve them, then run `git rebase --continue`, "
            "or abort with `git rebase --abort`.\n"
            "The versioned branch is your safety net; the original source branch is untouched."
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
    base_commit_sha = ref_commit_sha(base_resolution.base_ref)
    ensure_ref_exists(source_branch)

    resolved_new_branch = new_branch or next_versioned_branch(source_branch)
    commits = collect_commits(base_ref=base_resolution.base_ref, source_branch=source_branch)
    if not commits:
        raise SystemExit(
            f"No commits to rebase: {source_branch} is already up to date with "
            f"{base_resolution.base_ref}."
        )
    has_merge_commits = any(commit.is_merge for commit in commits)
    signed_commit_count = sum(1 for commit in commits if commit.is_signed)
    stacked_refs = detect_stacked_refs(
        base_ref=base_resolution.base_ref, source_branch=source_branch
    )

    return RestackPlan(
        base_branch=base_resolution.base_branch,
        source_branch=source_branch,
        new_branch=resolved_new_branch,
        base_ref=base_resolution.base_ref,
        base_commit_sha=base_commit_sha,
        base_ref_kind=base_resolution.base_ref_kind,
        base_freshness=base_freshness(
            base_ref_kind=base_resolution.base_ref_kind,
            fetch_executed=fetch_executed,
        ),
        commits=commits,
        fetch_executed=fetch_executed,
        has_merge_commits=has_merge_commits,
        signed_commit_count=signed_commit_count,
        stacked_refs=stacked_refs,
    )


def print_plan(plan: RestackPlan) -> None:
    """Print the planned restack steps in a human-readable form."""
    print(f"base_branch: {plan.base_branch}")
    print(f"source_branch: {plan.source_branch}")
    print(f"base_ref: {plan.base_ref}")
    print(f"base_commit_sha: {plan.base_commit_sha}")
    print(f"base_ref_kind: {plan.base_ref_kind}")
    print(f"base_freshness: {plan.base_freshness}")
    print(f"new_branch: {plan.new_branch}")
    print(f"fetch_executed: {'yes' if plan.fetch_executed else 'no'}")
    print(f"commits_to_rebase: {len(plan.commits)}")
    for commit in plan.commits:
        markers: list[str] = []
        if commit.is_merge:
            markers.append("merge")
        if commit.is_signed:
            markers.append("signed")
        marker = f" [{', '.join(markers)}]" if markers else ""
        print(f"  - {commit.sha} {commit.subject}{marker}")
    if plan.has_merge_commits:
        print(
            "warning: merge commits detected; git rebase will flatten them by default. "
            "If you must preserve the merge topology, abort and rerun with a manual "
            "`git rebase --rebase-merges --onto <base_ref> <base_ref>`."
        )
    if plan.signed_commit_count:
        print(
            f"warning: {plan.signed_commit_count} signed commit(s) detected; git rebase drops "
            "GPG signatures unless `commit.gpgSign=true` is configured or the rebase is "
            "rerun with `-S`. After apply, re-sign if required."
        )
    if plan.stacked_refs:
        refs_list = ", ".join(plan.stacked_refs)
        print(
            f"warning: other local branches point into the rebase range: {refs_list}. "
            "A plain rebase will leave them stranded on pre-rebase commits. Consider "
            "`git rebase --update-refs` (git 2.38+) or update those branches manually."
        )
    print("commands:")
    print(f"  git switch --no-track -c {plan.new_branch} {plan.source_branch}")
    print(f"  git rebase --empty=drop --onto {plan.base_ref} {plan.base_ref}")
    print("status: awaiting_confirmation")


def print_rewritten_commits(*, new_branch: str, base_ref: str) -> None:
    """Print the rewritten commits on the new branch for post-apply verification."""
    output = git_output(
        "log", "--reverse", "--format=%H%x09%s", f"{base_ref}..{new_branch}"
    )
    print("rewritten_commits:")
    for line in output.splitlines():
        sha, subject = line.split("\t", 1)
        print(f"  - {sha} {subject}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Recreate a branch on top of the latest base branch by rebasing source-only commits onto it.",
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
        help=(
            "Use the local cached remote-tracking ref without fetching. "
            "Only use after the user explicitly allows degrading freshness."
        ),
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
    create_branch_from_source(new_branch=plan.new_branch, source_branch=plan.source_branch)
    rebase_onto_base(base_ref=plan.base_ref)
    print_rewritten_commits(new_branch=plan.new_branch, base_ref=plan.base_ref)
    print("status: completed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted.")
