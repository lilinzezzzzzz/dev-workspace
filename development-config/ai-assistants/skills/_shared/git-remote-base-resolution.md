# Git Remote Base Resolution

Use this shared rule whenever a git skill accepts, infers, reviews against, drafts against, checks out from, or restacks onto a base branch or base ref.

## Default Resolution

- Apply this rule to all specified base branches, not just `dev`.
- Treat an unqualified base branch name such as `dev`, `main`, `master`, or `release/1.0` as a remote branch by default. Resolve it to the corresponding remote-tracking ref `<remote>/<branch>`, for example `dev` -> `origin/dev`.
- Use `origin` as the default remote when it exists. If `origin` is absent and exactly one remote exists, use that remote. If multiple non-`origin` remotes exist, ask which remote to use.
- If the user provides a full remote-tracking ref such as `origin/main` or `upstream/release/1.0`, use that remote and branch. Parse the first path component as the remote and fetch the remaining branch name.
- For an unqualified branch with slashes such as `release/1.0`, do not treat the first path component as a remote unless it is a configured git remote.
- Use a local ref only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.
- Never silently fall back to a same-name local branch when the remote-tracking ref is missing or ambiguous.

## Freshness

- The default base for remote-tracking refs is the latest remote base, not the local cached state.
- Fetch the specific remote branch first, for example `git fetch origin dev`, then use the fetched remote-tracking ref such as `origin/dev`.
- A successful fetch is required before describing any result as based on the latest remote commit.
- After a successful fetch, record the base commit SHA with `git rev-parse --verify <base-ref>`.
- If fetch is skipped, blocked, or fails, stop and report that the latest remote base cannot be verified.
- Continue with the local cached remote-tracking ref only when the user explicitly allows that downgrade. When downgraded, state that the cached ref may not match the latest remote branch.

## Reporting

- State the exact base ref used, for example `origin/dev`.
- State whether the base ref is `remote-tracking`, `local`, or another explicit ref.
- For a fetched remote-tracking base, state that fetch was executed and include the fetched base commit SHA.
- For an explicit downgrade, state `fetch: degraded` or `base_freshness: local-cached`, and say the ref may not match the latest remote branch.
